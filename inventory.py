from pico2d import *
from sdl2 import SDL_KEYDOWN, SDLK_ESCAPE, SDLK_u
import random

import game_framework
import game_world

import main_chracter

SCREEN_W, SCREEN_H = main_chracter.SCREEN_W, main_chracter.SCREEN_H

backpack_image = None
loot_images = []  # LOOT 폴더의 이미지들

# 배낭 데이터 (전역)
inventory_items = {}

# 배낭 UI 설정
INVENTORY_SLOTS = 6  # 배낭 슬롯 개수
SLOT_SIZE = 48  # 각 슬롯 크기 (픽셀)
SLOT_SPACING = 8  # 슬롯 간격


def init():
    global backpack_image, loot_images, inventory_items
    try:
        backpack_image = load_image('UI/backpack_in.png')
    except Exception as e:
        print(f"배낭 이미지 로드 오류: {e}")
        backpack_image = None

    # LOOT 폴더의 이미지들 로드
    loot_images = []
    for i in range(1, 5):
        loot_img = load_image(f'LOOT/loot{i}.png')
        loot_images.append(loot_img)


    # inventory_items 초기화하지 않기! (데이터 보존)
    # 이미 초기화된 경우만 빈 딕셔너리로 설정
    if not inventory_items:
        inventory_items = {}


def finish():
    global backpack_image, loot_images, inventory_items
    if backpack_image:
        del backpack_image
    loot_images = []
    inventory_items = {}


def handle_events():
    events = get_events()
    for event in events:
        if event.type == SDL_KEYDOWN:
            if event.key == SDLK_u or event.key == SDLK_ESCAPE:
                game_framework.pop_mode()


def update(dt):
    pass


def add_item(item_type, quantity=1):
    # 배낭에 아이템 추가하기
    if item_type not in inventory_items:
        inventory_items[item_type] = 0
    inventory_items[item_type] += quantity
    print(f"[INVENTORY] {item_type} x{quantity} 추가됨 (총: {inventory_items[item_type]})")


def get_inventory_items():
    # 배낭 아이템 반환
    return inventory_items.copy()


def draw():
    clear_canvas()
    game_world.render()

    # 배낭 UI 그리기
    if backpack_image:
        center_x = SCREEN_W // 2
        center_y = SCREEN_H // 2

        # 배낭 이미지 크기
        img_w = backpack_image.w
        img_h = backpack_image.h

        # 스케일 계산
        scale_w = (SCREEN_W * 0.9) / img_w
        scale_h = (SCREEN_H * 0.9) / img_h
        scale = min(scale_w, scale_h)

        draw_w = int(img_w * scale)
        draw_h = int(img_h * scale)
        backpack_image.draw(center_x, center_y, draw_w, draw_h)

        # 배낭 우측 상단에 전리품 표시
        loot_display_x = center_x + (draw_w // 2) - 150
        loot_display_y = center_y - (draw_h // 2) + 80

        # 아이템 그리기
        if loot_images:
            current_items = get_inventory_items()
            print(f"[배낭 표시] 현재 배낭 데이터: {current_items}, 로드된 이미지: {len(loot_images)}개")

            if current_items:
                item_index = 0
                for item_type, quantity in current_items.items():
                    if item_index >= 4:
                        break

                    # 각 아이템을 가로로 배치
                    icon_x = loot_display_x + item_index * 100
                    icon_y = loot_display_y

                    # LOOT 이미지 선택
                    loot_img = loot_images[item_index % len(loot_images)]

                    # 아이콘 배경 (진한 갈색)
                    icon_size = int(60 * scale)
                    draw_rectangle(
                        icon_x - icon_size // 2, icon_y - icon_size // 2,
                        icon_x + icon_size // 2, icon_y + icon_size // 2
                    )

                    # LOOT 이미지 그리기
                    try:
                        loot_img.draw(icon_x, icon_y, int(icon_size * 0.8), int(icon_size * 0.8))
                        print(f"[슬롯 {item_index}] {item_type}x{quantity} 그려짐 at ({icon_x}, {icon_y})")
                    except Exception as e:
                        print(f"✗ LOOT 이미지 그리기 오류: {e}")

                    # 개수 텍스트 (우측 하단)
                    if quantity > 0:
                        try:
                            font = load_font(None, int(18 * scale))
                            font.draw(
                                int(icon_x + icon_size // 2 - 15),
                                int(icon_y - icon_size // 2 + 8),
                                str(quantity),
                                (255, 255, 0)
                            )
                            print(f"[텍스트] 개수 {quantity} 표시")
                        except Exception as e:
                            print(f"✗ 텍스트 그리기 오류: {e}")

                    item_index += 1
            else:
                print(f"[배낭] 수집한 아이템 없음")
        else:
            print(f"[배낭] LOOT 이미지 로드 실패")

    update_canvas()


def pause():
    pass


def resume():
    pass