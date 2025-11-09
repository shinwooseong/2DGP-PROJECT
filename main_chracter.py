import time
from pico2d import load_image
from sdl2 import SDLK_a, SDL_KEYDOWN, SDL_KEYUP, SDLK_UP, SDLK_DOWN, SDLK_LEFT, SDLK_RIGHT, SDLK_SPACE

from state_machine import StateMachine
import player_loader
import player_states


SCREEN_W, SCREEN_H = 1280, 736
SPRITE_W, SPRITE_H = 96, 80


# Idle, Walk, Roll, Attack 클래스 정의 모두 삭제하고 player_states 모듈로 이동

class Main_character:
    def __init__(self):
        # 1. 컴포넌트(로더) 생성
        self.loader = player_loader.PlayerLoader()

        # 2. 위치/상태
        self.x = SCREEN_W // 2
        self.y = SCREEN_H // 2
        self.dir = 'DOWN'
        self.frame = 0

        # 3. 스탯
        self.health = 200
        self.max_health = 200
        self.money = 0
        self.attack = 10

        # 4. 입력 맵
        self.key_map = {'UP': False, 'DOWN': False, 'LEFT': False, 'RIGHT': False}

        # 5. 타이밍
        self.frame_time_acc = 0.0
        self.roll_moved = 0.0

        # 모든 이미지 로딩 및 Y-Offset 계산 코드 삭제 (loader가 대신 하게 하기!)

        # 6. 공격 콤보 관리
        self.attack_stage = 1
        self.next_attack_request = False
        self.last_attack_end_time = 0.0
        self.attack_combo_window = 1.0

        # 7. 상태 인스턴스 (player_states에서 가져옴)
        self.IDLE = player_states.Idle(self)
        self.WALK = player_states.Walk(self)
        self.ROLL = player_states.Roll(self)
        self.ATTACK = player_states.Attack(self)

        # 8. 상태 머신
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

    def update(self, dt):
        try:
            self.state_machine.update(dt)
        except Exception:
            pass

    def draw(self):
        try:
            self.state_machine.draw()
        except Exception:
            pass

    def take_damage(self, damage):
        try:
            self.health -= damage
        except Exception:
            self.health = getattr(self, 'health', 0) - damage
        print(f"Player took {damage} dmg. HP={self.health}")
        if self.health <= 0:
            print("Player died")

    def handle_event(self, event):
        try:
            from sdl2 import SDLK_a, SDL_KEYDOWN, SDL_KEYUP, SDLK_UP, SDLK_DOWN, SDLK_LEFT, SDLK_RIGHT, SDLK_SPACE
        except Exception:
            pass
        if getattr(event, 'type', None) == SDL_KEYDOWN:
            key = getattr(event, 'key', None)
            if key == SDLK_UP:
                self.key_map['UP'] = True
                self.dir = 'UP'
            elif key == SDLK_DOWN:
                self.key_map['DOWN'] = True
                self.dir = 'DOWN'
            elif key == SDLK_LEFT:
                self.key_map['LEFT'] = True
                self.dir = 'LEFT'
            elif key == SDLK_RIGHT:
                self.key_map['RIGHT'] = True
                self.dir = 'RIGHT'
            elif key == SDLK_SPACE:
                try:
                    self.state_machine.handle_state_event(('SPACE', None))
                except Exception:
                    pass
            elif key == SDLK_a:
                # 공격 키 처리
                now = time.time()
                if self.state_machine.cur_state is self.ATTACK:
                    self.next_attack_request = True
                else:
                    # 공격 시작
                    if now - self.last_attack_end_time <= self.attack_combo_window:
                        self.attack_stage = 2
                    else:
                        self.attack_stage = 1
                    try:
                        self.state_machine.handle_state_event(('ATTACK', None))
                    except Exception:
                        pass
        elif getattr(event, 'type', None) == SDL_KEYUP:
            key = getattr(event, 'key', None)
            if key == SDLK_UP:
                self.key_map['UP'] = False
            elif key == SDLK_DOWN:
                self.key_map['DOWN'] = False
            elif key == SDLK_LEFT:
                self.key_map['LEFT'] = False
            elif key == SDLK_RIGHT:
                self.key_map['RIGHT'] = False