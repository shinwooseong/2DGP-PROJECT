import json
from pico2d import load_image, load_image


class TiledMap:
    def __init__(self, json_path):
        # 1. JSON 맵 파일 로드
        with open(json_path) as f:
            self.map_data = json.load(f)

        # 2. 기본 맵 속성 저장
        self.tile_width = self.map_data['tilewidth']
        self.tile_height = self.map_data['tileheight']
        self.map_width_tiles = self.map_data['width']
        self.map_height_tiles = self.map_data['height']

        # 맵의 전체 픽셀 크기
        self.map_width_px = self.map_width_tiles * self.tile_width
        self.map_height_px = self.map_height_tiles * self.tile_height

        # 3. 타일셋 이미지 로드 (첫 번째 타일셋 기준)
        tileset_info = self.map_data['tilesets'][0]
        tileset_image_path = tileset_info['image']

        # Tiled는 .json 기준 상대 경로로 저장하므로, 실제 경로를 잘 맞춰야 합니다.
        # 예: 'map/tileset.png'
        try:
            self.tileset_image = load_image(tileset_image_path)
        except:
            # Tiled가 저장한 경로 그대로 다시 시도
            print(f"경고: {tileset_image_path} 로드 실패. 상위 폴더에서 다시 시도합니다.")
            # (만약 map 폴더 안에 json이 있다면)
            self.tileset_image = load_image(f"../{tileset_image_path}")

        self.tileset_cols = tileset_info['columns']

        # 4. 그릴 레이어(들) 데이터 저장
        self.layers_data = []
        for layer in self.map_data['layers']:
            if layer['type'] == 'tilelayer':
                self.layers_data.append(layer['data'])  # 타일 ID 리스트

    def draw(self):
        # (카메라 없는 버전)
        # 맵 전체를 순회하며 타일 그리기
        for layer_data in self.layers_data:
            for y in range(self.map_height_tiles):
                for x in range(self.map_width_tiles):

                    # 맵 타일 인덱스 (Tiled는 1부터 시작, 0은 '빈 타일')
                    # Tiled 맵은 y=0이 위쪽이므로 그릴 때 y좌표를 뒤집어줍니다.
                    map_index = (self.map_height_tiles - 1 - y) * self.map_width_tiles + x
                    tile_id = layer_data[map_index]

                    if tile_id == 0:
                        continue  # 빈 타일은 그리지 않음

                    # 타일셋에서 (src_x, src_y) 계산 (Tiled ID는 1부터 시작)
                    src_x = ((tile_id - 1) % self.tileset_cols) * self.tile_width
                    src_y = ((tile_id - 1) // self.tileset_cols) * self.tile_height
                    # (Pico2D는 y가 아래 기준이므로 타일셋 y좌표 뒤집기)
                    src_y = self.tileset_image.h - src_y - self.tile_height

                    # 맵에서의 타일 월드 좌표 (중심점 기준)
                    # 맵이 화면에 꽉 차므로, 월드 좌표 = 화면 좌표
                    dest_x = x * self.tile_width + self.tile_width // 2
                    dest_y = y * self.tile_height + self.tile_height // 2

                    self.tileset_image.clip_draw(
                        src_x, src_y, self.tile_width, self.tile_height,
                        dest_x, dest_y
                    )

    def get_collision_boxes(self):
        # Tiled에서 'Collisions'라는 이름의 'Object Layer'를 찾음
        boxes = []
        for layer in self.map_data['layers']:
            if layer['type'] == 'objectgroup' and layer['name'] == 'Collisions':
                for obj in layer['objects']:
                    # (Tiled는 y=0이 위쪽이므로 y좌표 변환)
                    tiled_y = obj['y']
                    tiled_height = obj['height']
                    pico2d_y = self.map_height_px - tiled_y - tiled_height

                    # (left, bottom, right, top) 형태로 저장
                    boxes.append((
                        obj['x'],
                        pico2d_y,
                        obj['x'] + obj['width'],
                        pico2d_y + obj['height']
                    ))
        return boxes

    def update(self, dt):
        pass