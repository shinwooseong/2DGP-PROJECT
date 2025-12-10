from pico2d import *
import game_framework
import title_mode as start_mode
import main_chracter
import server
import sys
import os

# PyInstaller로 빌드된 경우 리소스 경로 설정
if getattr(sys, 'frozen', False):
    # PyInstaller 번들 실행
    resource_path = sys._MEIPASS
else:
    # 일반 Python 실행
    resource_path = os.path.dirname(os.path.abspath(__file__))

# 리소스 경로를 현재 디렉토리로 변경
os.chdir(resource_path)

# 스크린 크기는 main_chracter 모듈에서 가져옴
open_canvas(main_chracter.SCREEN_W, main_chracter.SCREEN_H,sync=True)
# 게임 시작 전 플레이어를 딱 한 번만 생성하여 server에 저장
server.player = main_chracter.Main_character()

# 모든 효과음 초기화
server.init_all_sounds()

# game_framework를 실행하고 시작 모드를 지정
game_framework.run(start_mode)
close_canvas()