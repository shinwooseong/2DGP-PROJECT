from pico2d import *
import game_framework
import play_mode # 시작 모드를 play_mode로 변경

# 스크린 크기는 main_chracter 모듈에서 가져옴
import main_chracter

open_canvas(main_chracter.SCREEN_W, main_chracter.SCREEN_H)
# game_framework를 실행하고 시작 모드를 지정
game_framework.run(play_mode)
close_canvas()