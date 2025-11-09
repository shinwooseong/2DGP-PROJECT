import os
from pico2d import load_image

class Background:
    def __init__(self, image_path='Scene_Overview.png'):
        self.image = load_image(image_path)
        self.width = self.image.w
        self.height = self.image.h

    def draw(self):
        self.image.draw(self.width // 2, self.height // 2)
#이미지 만들어야함