import time
from pico2d import load_image, draw_rectangle
import server
from sdl2 import SDLK_a, SDL_KEYDOWN, SDL_KEYUP, SDLK_UP, SDLK_DOWN, SDLK_LEFT, SDLK_RIGHT, SDLK_SPACE, SDLK_x

from state_machine import StateMachine
import player_loader
import player_states
import transform_loader
import transform_states
from transform_loader import TRANSFORM_SPRITE_W, TRANSFORM_SPRITE_H, TRANSFORM_FOOT_OFFSET_Y
from character_constants import (
    SCREEN_W, SCREEN_H, SPRITE_W, SPRITE_H,
    CHARACTER_COLLISION_W, CHARACTER_COLLISION_H,
    TRANSFORM_COLLISION_W, TRANSFORM_COLLISION_H
)


# Idle, Walk, Roll, Attack 클래스 정의 모두 삭제하고 player_states 모듈로 이동

class Main_character:
    def __init__(self):
        # 1. 컴포넌트(로더) 생성
        self.loader = player_loader.PlayerLoader()
        self.transform_loader = transform_loader.TransformLoader()

        # 2. 위치/상태
        self.x = SCREEN_W // 2
        self.y = SCREEN_H // 2
        self.dir = 'DOWN'  # 기본 캐릭터는 DOWN
        self.frame = 0

        # 3. 스탯
        self.health = 300
        self.max_health = 300
        self.money = 0

        # 포션 개수
        self.hp_potion_count = 0

        # 전리품 인벤토리 (loot1 ~ loot4 각각의 개수)
        self.loot_inventory = {
            'loot1': 7,
            'loot2': 7,
            'loot3': 7,
            'loot4': 7
        }

        # 캐릭터별 공격력 설정
        self.base_attack = 20  # 기본 캐릭터 공격력
        self.transform_attack = 10  # 변신 캐릭터 공격력
        self.attack = self.base_attack  # 현재 공격력 (초기값은 기본 캐릭터)

        # 4. 입력 맵
        self.key_map = {'UP': False, 'DOWN': False, 'LEFT': False, 'RIGHT': False}

        # 5. 타이밍
        self.frame_time_acc = 0.0
        self.roll_moved = 0.0

        # 6. 공격 콤보 관리
        self.attack_stage = 1
        self.next_attack_request = False
        self.last_attack_end_time = 0.0
        self.attack_combo_window = 1.0

        # 7. 변신 관련
        self.is_transformed = False  # 변신 상태 플래그

        # 죽음 플래그
        self.is_dead = False

        # 공격 범위 디버그 표시 플래그
        self.show_attack_bb = True

        # 무적 시간 관련
        self.invincible = False  # 무적 상태 여부
        self.invincible_timer = 0.0  # 무적 시간 타이머
        self.invincible_duration = 1.0  # 무적 지속 시간 (1초)

        # 8. 기본 캐릭터 상태 인스턴스 (player_states에서 가져옴)
        self.IDLE = player_states.Idle(self)
        self.WALK = player_states.Walk(self)
        self.ROLL = player_states.Roll(self)
        self.ATTACK = player_states.Attack(self)

        # 9. 변신 캐릭터 상태 인스턴스 (transform_states에서 가져옴)
        self.TRANSFORM_IDLE = transform_states.TransformIdle(self)
        self.TRANSFORM_WALK = transform_states.TransformWalk(self)
        self.TRANSFORM_ROLL = transform_states.TransformRoll(self)
        self.TRANSFORM_ATTACK = transform_states.TransformAttack(self)

        # 10. 상태 머신 (기본 캐릭터로 시작)
        self.state_machine = StateMachine(
            self.IDLE,
            {
                self.IDLE: {
                    'MOVE': lambda e: self.WALK,
                    'SPACE': lambda e: self.ROLL,
                    'ATTACK': lambda e: self.ATTACK
                },
                self.WALK: {
                    'STOP': lambda e: self.IDLE,
                    'SPACE': lambda e: self.ROLL,
                    'ATTACK': lambda e: self.ATTACK
                },
                self.ROLL: {
                    'STOP': lambda e: self.IDLE,
                    'ATTACK': lambda e: self.ATTACK
                },
                self.ATTACK: {
                    'STOP': lambda e: self.IDLE
                }
            }
        )

        # 변신 캐릭터 상태 머신
        self.transform_state_machine = StateMachine(
            self.TRANSFORM_IDLE,
            {
                self.TRANSFORM_IDLE: {
                    'MOVE': lambda e: self.TRANSFORM_WALK,
                    'SPACE': lambda e: self.TRANSFORM_ROLL,
                    'ATTACK': lambda e: self.TRANSFORM_ATTACK
                },
                self.TRANSFORM_WALK: {
                    'STOP': lambda e: self.TRANSFORM_IDLE,
                    'SPACE': lambda e: self.TRANSFORM_ROLL,
                    'ATTACK': lambda e: self.TRANSFORM_ATTACK
                },
                self.TRANSFORM_ROLL: {
                    'STOP': lambda e: self.TRANSFORM_IDLE,
                    'ATTACK': lambda e: self.TRANSFORM_ATTACK
                },
                self.TRANSFORM_ATTACK: {
                    'STOP': lambda e: self.TRANSFORM_IDLE
                }
            }
        )

    def toggle_transform(self):
       # 변신 상태 토글
        if self.is_transformed:
            # 변신 해제
            self.is_transformed = False
            self.attack = self.base_attack  # 기본 캐릭터 공격력으로 변경
            self.dir = 'DOWN'
            self.state_machine = StateMachine(
                self.IDLE,
                {
                    self.IDLE: {
                        'MOVE': lambda e: self.WALK,
                        'SPACE': lambda e: self.ROLL,
                        'ATTACK': lambda e: self.ATTACK
                    },
                    self.WALK: {
                        'STOP': lambda e: self.IDLE,
                        'SPACE': lambda e: self.ROLL,
                        'ATTACK': lambda e: self.ATTACK
                    },
                    self.ROLL: {
                        'STOP': lambda e: self.IDLE,
                        'ATTACK': lambda e: self.ATTACK
                    },
                    self.ATTACK: {
                        'STOP': lambda e: self.IDLE
                    }
                }
            )
            self.state_machine.cur_state.enter(None)
            print(f"변신 해제! 공격력: {self.attack}")
        else:
            # 변신: Hurt 애니메이션 재생 후 변신 상태로 전환
            self.is_transformed = True
            self.attack = self.transform_attack  # 변신 캐릭터 공격력으로 변경
            if self.dir == 'UP' or self.dir == 'DOWN':
                self.dir = 'RIGHT'

            # TransformHurt 상태 생성 (아직 없으므로 즉시 변신)
            self.state_machine = self.transform_state_machine
            self.state_machine.cur_state = self.TRANSFORM_IDLE
            self.state_machine.cur_state.enter(None)

            # Hurt 애니메이션을 한 번 재생
            self.transform_hurt_animation_playing = True
            self.transform_hurt_frame = 0
            self.transform_hurt_acc = 0.0
            print(f"변신! 공격력: {self.attack}")

    def update(self, dt):
        # 변신 Hurt 애니메이션 재생 중이면 먼저 처리
        if getattr(self, 'transform_hurt_animation_playing', False):
            loader = self.transform_loader
            frames = loader.hurt_frames
            frame_time = 0.1

            self.transform_hurt_acc += dt
            while self.transform_hurt_acc >= frame_time:
                self.transform_hurt_acc -= frame_time
                self.transform_hurt_frame += 1

                if self.transform_hurt_frame >= frames:
                    # Hurt 애니메이션 종료, 정상 변신 상태로 전환
                    self.transform_hurt_animation_playing = False
                    self.transform_hurt_frame = 0
                    self.transform_hurt_acc = 0.0
                    break
            return

        try:
            self.state_machine.update(dt)
        except Exception:
            pass

        # 무적 타이머 업데이트
        if self.invincible:
            self.invincible_timer += dt
            if self.invincible_timer >= self.invincible_duration:
                self.invincible = False  # 무적 해제

    def draw(self):
        # 카메라 오프셋 계산
        cam = getattr(server, 'tiled_map', None)
        use_cam = bool(cam and getattr(cam, 'use_camera', False))
        cam_ox = cam.cam_offset_x if use_cam else 0
        cam_oy = cam.cam_offset_y if use_cam else 0

        # 변신 Hurt 애니메이션 재생 중이면 Hurt 그리기
        if getattr(self, 'transform_hurt_animation_playing', False):
            loader = self.transform_loader
            image = loader.hurt_image
            frames = loader.hurt_frames
            frame_idx = int(getattr(self, 'transform_hurt_frame', 0)) % frames

            # 실제 프레임 크기 사용 (144x144)
            x_offset = frame_idx * TRANSFORM_SPRITE_W
            img_height = image.h

            # 발(실제 발 위치)을 원점으로 하기 위해 y 좌표 조정
            draw_y_world = self.y + (TRANSFORM_SPRITE_H // 2) - TRANSFORM_FOOT_OFFSET_Y
            draw_x_world = self.x
            draw_x = draw_x_world + cam_ox
            draw_y = draw_y_world + cam_oy

            # 왼쪽 방향이면 이미지 좌우 반전
            if self.dir == 'LEFT':
                image.clip_composite_draw(
                    x_offset, 0, TRANSFORM_SPRITE_W, img_height,
                    0, 'h', draw_x, draw_y, TRANSFORM_SPRITE_W, TRANSFORM_SPRITE_H
                )
            else:  # RIGHT
                image.clip_draw(
                    x_offset, 0, TRANSFORM_SPRITE_W, img_height,
                    draw_x, draw_y, TRANSFORM_SPRITE_W, TRANSFORM_SPRITE_H
                )

            # 디버그: 실제 충돌 범위 표시 (변신 캐릭터)
            draw_rectangle(
                self.x - TRANSFORM_COLLISION_W // 2 + cam_ox,
                self.y - TRANSFORM_COLLISION_H // 2 + cam_oy,
                self.x + TRANSFORM_COLLISION_W // 2 + cam_ox,
                self.y + TRANSFORM_COLLISION_H // 2 + cam_oy
            )
            # 발 위치 표시 (노란색 작은 점)
            draw_rectangle(self.x - 2 + cam_ox, self.y - 2 + cam_oy, self.x + 2 + cam_ox, self.y + 2 + cam_oy)
            return

        try:
            self.state_machine.draw()

            # 공격 범위 표시 (빨간 박스)
            if self.show_attack_bb:
                bb = self.get_bb()
                if bb is not None:
                    left, bottom, right, top = bb
                    # 빨간색으로 공격 범위 표시
                    if use_cam:
                        draw_rectangle(left + cam_ox, bottom + cam_oy, right + cam_ox, top + cam_oy)
                    else:
                        draw_rectangle(left, bottom, right, top)

            # 디버그: 실제 충돌 범위 표시 (캐릭터 크기에 맞게)
            if self.is_transformed:
                # 변신 상태일 때는 변신 캐릭터 충돌 범위
                draw_rectangle(
                    self.x - TRANSFORM_COLLISION_W // 2 + cam_ox,
                    self.y - TRANSFORM_COLLISION_H // 2 + cam_oy,
                    self.x + TRANSFORM_COLLISION_W // 2 + cam_ox,
                    self.y + TRANSFORM_COLLISION_H // 2 + cam_oy
                )
            else:
                # 기본 상태일 때는 기본 캐릭터 충돌 범위
                draw_rectangle(
                    self.x - CHARACTER_COLLISION_W // 2 + cam_ox,
                    self.y - CHARACTER_COLLISION_H // 2 + cam_oy,
                    self.x + CHARACTER_COLLISION_W // 2 + cam_ox,
                    self.y + CHARACTER_COLLISION_H // 2 + cam_oy
                )

            # 발 위치 표시 (노란색 작은 점)
            draw_rectangle(self.x - 2 + cam_ox, self.y - 2 + cam_oy, self.x + 2 + cam_ox, self.y + 2 + cam_oy)
        except Exception:
            pass

    def take_damage(self, damage):
        try:
            if self.invincible:
                print("무적 상태라서 데미지를 받지 않습니다!")
                return

            self.health -= damage
        except Exception:
            self.health = getattr(self, 'health', 0) - damage
        print(f"Player took {damage} dmg. HP={self.health}")
        if self.health <= 0:
            self.health = 0
            self.is_dead = True  # 죽음 플래그 설정
            print("Player died")
        else:
            # 무적 상태 진입
            self.invincible = True
            self.invincible_timer = 0.0  # 타이머 초기화

    def use_potion(self):
        # 포션 기능 추가 (hp 50)
        if self.hp_potion_count > 0:
            # 체력이 이미 최대치면 사용 불가
            if self.health >= self.max_health:
                print("[포션] 체력이 이미 최대입니다!")
                return False

            # 포션 사용
            self.hp_potion_count -= 1
            heal_amount = 50
            self.health = min(self.health + heal_amount, self.max_health)

            print(f"[포션 사용] 체력 {heal_amount} 회복! 현재 체력: {self.health}/{self.max_health}, 남은 포션: {self.hp_potion_count}")

            # 포션 사용 효과음 재생
            try:
                import dungeon_mode
                if dungeon_mode.se_potion:
                    dungeon_mode.se_potion.play()
            except Exception as e:
                print(f"[SE] potion.wav 재생 실패: {e}")

            return True
        else:
            print("[포션] 포션이 없습니다!")
            return False

    def handle_event(self, event):
        if event.type == SDL_KEYDOWN:
            key = event.key
            if key == SDLK_UP:
                self.key_map['UP'] = True
                if not self.is_transformed:
                    self.dir = 'UP'
            elif key == SDLK_DOWN:
                self.key_map['DOWN'] = True
                if not self.is_transformed:
                    self.dir = 'DOWN'
            elif key == SDLK_LEFT:
                self.key_map['LEFT'] = True
                if not self.is_transformed:
                    self.dir = 'LEFT'
                else:
                    self.dir = 'LEFT'  # 변신 상태에서도 방향 변경
            elif key == SDLK_RIGHT:
                self.key_map['RIGHT'] = True
                if not self.is_transformed:
                    self.dir = 'RIGHT'
                else:
                    self.dir = 'RIGHT'  # 변신 상태에서도 방향 변경
            elif key == SDLK_SPACE:
                self.state_machine.handle_state_event(('SPACE', None))
            elif key == SDLK_x:
                # X 키로 변신/변신 해제
                self.toggle_transform()
            elif key == SDLK_a:
                # 공격 키 처리
                now = time.time()
                if self.state_machine.cur_state is self.ATTACK or self.state_machine.cur_state is self.TRANSFORM_ATTACK:
                    self.next_attack_request = True
                else:
                    # 공격 시작
                    if now - self.last_attack_end_time <= self.attack_combo_window:
                        self.attack_stage = 2
                    else:
                        self.attack_stage = 1
                    self.state_machine.handle_state_event(('ATTACK', None))
        elif event.type == SDL_KEYUP:
            key = event.key
            if key == SDLK_UP:
                self.key_map['UP'] = False
            elif key == SDLK_DOWN:
                self.key_map['DOWN'] = False
            elif key == SDLK_LEFT:
                self.key_map['LEFT'] = False
            elif key == SDLK_RIGHT:
                self.key_map['RIGHT'] = False

    # 캐릭터의 공격범위 만들기
    def get_bb(self):

        # 공격 상태가 아니면 None 반환
        if not self.is_transformed:
            # 기본 캐릭터
            if self.state_machine.cur_state is not self.ATTACK:
                return None

            # 방향에 따른 공격 범위 설정 (칼이 뻗는 범위)
            attack_reach = 60  # 공격 범위
            attack_width = 40   # 공격 폭

            # 각 방향 별로 각기 적용
            if self.dir == 'DOWN':
                return (self.x - attack_width // 2,
                       self.y - attack_reach,
                       self.x + attack_width // 2,
                       self.y)
            elif self.dir == 'UP':
                return (self.x - attack_width // 2,
                       self.y,
                       self.x + attack_width // 2,
                       self.y + attack_reach)
            elif self.dir == 'LEFT':
                return (self.x - attack_reach,
                       self.y - attack_width // 2,
                       self.x,
                       self.y + attack_width // 2)
            elif self.dir == 'RIGHT':
                return (self.x,
                       self.y - attack_width // 2,
                       self.x + attack_reach,
                       self.y + attack_width // 2)
        else:
            # 변신 캐릭터
            if self.state_machine.cur_state is not self.TRANSFORM_ATTACK:
                return None

            # 변신 캐릭터는 공격 범위가 더 작음
            # 몸집이 작으니까
            attack_reach = 40  # 공격 범위
            attack_width = 30   # 공격 폭

            if self.dir == 'LEFT':
                return (self.x - attack_reach,
                       self.y - attack_width // 2,
                       self.x,
                       self.y + attack_width // 2)
            elif self.dir == 'RIGHT':
                return (self.x,
                       self.y - attack_width // 2,
                       self.x + attack_reach,
                       self.y + attack_width // 2)

        return None
