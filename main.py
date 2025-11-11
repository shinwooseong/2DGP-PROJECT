import sys
import os
# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'codes'))

from pico2d import *
from codes import game_framework
from codes import shop_mode as start_mode
from codes import main_chracter

open_canvas(main_chracter.SCREEN_W, main_chracter.SCREEN_H, sync=True)
# game_framework를 실행하고 시작 모드를 지정
game_framework.run(start_mode)
close_canvas()
