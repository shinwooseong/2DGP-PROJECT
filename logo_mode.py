from pico2d import *
import game_framework
import title_mode  # 다음 모드인 title_mode를 임포트합니다.
import main_chracter

image = None
logo_start_time = 0.0


def init():
    global image, logo_start_time
    image = load_image('UI/moonlighter_logo.png')

    logo_start_time = get_time()  # 2. 시작 시간을 기록합니다.


def finish():
    global image
    del image  # 3. 리소스를 해제합니다.


def update(dt):  # game_framework가 dt를 전달해줍니다.
    # 4. 2초가 지났는지 확인합니다.
    if get_time() - logo_start_time >= 2.0:
        # 5. 2초가 지나면 title_mode로 변경합니다.
        game_framework.change_mode(title_mode)


def draw():
    clear_canvas()
    if image:
        logo_w = int(main_chracter.SCREEN_W * 0.7)
        logo_h = int(main_chracter.SCREEN_H * 0.7)
        image.draw(main_chracter.SCREEN_W // 2, main_chracter.SCREEN_H // 2,
                   logo_w, logo_h)
    update_canvas()


def handle_events():
    # 로고 화면에서는 이벤트를 무시합니다.
    events = get_events()


def pause(): pass


def resume(): pass