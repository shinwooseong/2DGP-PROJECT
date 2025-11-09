import os
from pico2d import load_image
import main_chracter

class Background:
    def __init__(self, image_path='Scene Overview.png'):
        self.image = load_image(image_path)
        self.width = self.image.w
        self.height = self.image.h

    def draw(self):
        # 화면 크기에 맞춰 배경 그리기
        screen_w = main_chracter.SCREEN_W
        screen_h = main_chracter.SCREEN_H
        self.image.draw(screen_w // 2, screen_h // 2, screen_w, screen_h)
