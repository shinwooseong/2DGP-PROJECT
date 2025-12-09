from pico2d import *
from sdl2 import SDL_KEYDOWN, SDLK_ESCAPE, SDLK_u
import random

import game_framework
import game_world
import server

import main_chracter

SCREEN_W, SCREEN_H = main_chracter.SCREEN_W, main_chracter.SCREEN_H

backpack_image = None
loot_images = {}  # loot1 ~ loot4 이미지 딕셔너리
number_font = None
small_font = None  # 작은 글씨 폰트
npc_text_image = None  # NPC_text.png 이미지

# 현재 플레이어 참조
current_player = None


def init():
    global backpack_image, loot_images, number_font, small_font, npc_text_image

    try:
        backpack_image = load_image('UI/backpack_in.png')
    except Exception as e:
        print(f"배낭 이미지 로드 오류: {e}")
        backpack_image = None

    # LOOT 이미지들 로드 (loot1 ~ loot4)
    loot_images = {}
    for i in range(1, 5):
        loot_img = load_image(f'LOOT/loot{i}.png')
        loot_images[f'loot{i}'] = loot_img

    # 숫자 폰트 로드
    number_font = load_font('UI/use_font/MaruBuri-Bold.ttf', 32)

    # 작은 글씨 폰트 로드
    small_font = load_font('UI/use_font/MaruBuri-Bold.ttf', 18)

    # NPC_text.png 이미지 로드
    try:
        npc_text_image = load_image('UI/NPC_text.png')
    except Exception as e:
        print(f"NPC_text.png 로드 오류: {e}")
        npc_text_image = None


def finish():
    global backpack_image, loot_images, number_font, small_font, npc_text_image
    if backpack_image:
        del backpack_image
    loot_images = {}
    number_font = None
    small_font = None
    npc_text_image = None


def handle_events():
    events = get_events()
    for event in events:
        if event.type == SDL_KEYDOWN:
            if event.key == SDLK_u or event.key == SDLK_ESCAPE:
                game_framework.pop_mode()


def update(dt):
    pass


def set_player(player):
    # 프레이어 참조하기
    global current_player
    current_player = player


def draw():
    clear_canvas()
    game_world.render()

    # 배낭 UI 그리기
    if backpack_image:
        center_x = SCREEN_W // 2 - 120  # 더 왼쪽으로 이동
        center_y = SCREEN_H // 2

        # 배낭 이미지 크기
        img_w = backpack_image.w
        img_h = backpack_image.h

        # 스케일 계산
        scale_w = (SCREEN_W * 0.6) / img_w
        scale_h = (SCREEN_H * 0.6) / img_h
        scale = min(scale_w, scale_h)

        draw_w = int(img_w * scale)
        draw_h = int(img_h * scale)

        # 배낭 그리기
        backpack_image.draw(center_x, center_y, draw_w, draw_h)

        # 배낭을 4등분해서 전리품 표시
        if server.player and loot_images:
            # 4등분 영역 계산
            slot_width = draw_w // 2
            slot_height = draw_h // 2

            # 시작 위치 (배낭 좌측 상단)
            start_x = center_x - draw_w // 2
            start_y = center_y + draw_h // 2

            # 각 슬롯 중앙 위치 계산
            slots = [
                (start_x + slot_width // 2, start_y - slot_height // 2),      # 좌상
                (start_x + slot_width // 2 + slot_width, start_y - slot_height // 2),  # 우상
                (start_x + slot_width // 2, start_y - slot_height // 2 - slot_height),  # 좌하
                (start_x + slot_width // 2 + slot_width, start_y - slot_height // 2 - slot_height)  # 우하
            ]

            # loot1 ~ loot4 순서대로 그리기
            loot_keys = ['loot1', 'loot2', 'loot3', 'loot4']

            for i, loot_key in enumerate(loot_keys):
                if loot_key in loot_images:
                    slot_x, slot_y = slots[i]
                    loot_count = current_player.loot_inventory.get(loot_key, 0)

                    # 전리품 이미지 그리기
                    loot_img = loot_images[loot_key]
                    img_size = int(min(slot_width, slot_height) * 0.6)

                    # 이미지를 약간 위로 올려서 숫자와 겹치지 않게
                    img_y = slot_y + 20
                    loot_img.draw(slot_x, img_y, img_size, img_size)

                    # 개수 표시 (이미지 아래)
                    if number_font:
                        text_y = slot_y - 40
                        number_font.draw(slot_x - 20, text_y, f"{loot_count}", (255, 255, 255))

    # NPC_text.png 이미지와 설명 그리기 (배낭 오른쪽)
    if npc_text_image and server.player:
        # NPC_text.png 이미지 위치 및 크기
        npc_text_x = SCREEN_W // 2 + 350
        npc_text_y = SCREEN_H // 2
        npc_text_w = 420
        npc_text_h = 480

        # NPC_text.png 그리기
        npc_text_image.draw(npc_text_x, npc_text_y, npc_text_w, npc_text_h)

        # NPC_text.png 위에 게임 설명 그리기 (검은색 작은 글씨)
        if small_font:
            descriptions = [
                "[ 게임 설명서 ]",
                "",
                "조작법:",
                "A 키 - 공격",
                "S 키 - 물약 (HP 50)",
                "Z 키 - 귀환 (200원)",
                "",
                "마을 NPC:",
                "요정 - 전리품 3개씩",
                "       체력한계 +50",
                "대장장이 - 전리품 판매",
                "",
                "상점: 물약 구매",
                "",
                "던전:",
                "전리품 랜덤 드롭",
                "사망 시 1/3 손실",
                "",
                "보스:",
                "꿀 먹으면 기절",
                "기절 중 공격!"
            ]

            text_x = npc_text_x - 40
            text_y = npc_text_y + 180

            for line in descriptions:
                small_font.draw(text_x, text_y, line, (0, 0, 0))
                text_y -= 16

    update_canvas()


def pause():
    pass


def resume():
    pass