import os
from pico2d import load_image

class Background:
    def __init__(self, image_path):
        if not os.path.isfile(image_path):
            raise FileNotFoundError(f"Background image file not found: {image_path}")
        self.image = load_image(image_path)
        self.width = self.image.w
        self.height = self.image.h

    def draw(self):
        self.image.draw(self.width // 2, self.height // 2)
