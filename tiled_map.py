# tiled_map.py
import json
import os
from pico2d import load_image, get_canvas_width, get_canvas_height


class TiledMap:
    def __init__(self, json_path, use_camera=False):
        # 1. JSON 맵 파일 로드
        with open(json_path) as f:
            self.map_data = json.load(f)

        # 2. 기본 맵 속성 저장
        self.tile_width = self.map_data['tilewidth']
        self.tile_height = self.map_data['tileheight']
        self.map_width_tiles = self.map_data['width']
        self.map_height_tiles = self.map_data['height']

        self.map_width_px = self.map_width_tiles * self.tile_width
        self.map_height_px = self.map_height_tiles * self.tile_height

        # (수정) 화면 크기 저장
        self.screen_w = get_canvas_width()
        self.screen_h = get_canvas_height()

        # 카메라 사용 여부 저장
        self.use_camera = use_camera

        if use_camera:
            # 카메라 사용 시에는 스케일을 1.0으로 고정 (원본 크기)
            self.scale = 1.0
            self.offset_x = 0
            self.offset_y = 0
        else:
            # 카메라 미사용 시에는 화면에 맞게 스케일 조정
            self.scale_x = self.screen_w / self.map_width_px
            self.scale_y = self.screen_h / self.map_height_px
            self.scale = min(self.scale_x, self.scale_y)

            # 맵이 그려질 실제 크기
            scaled_map_width = self.map_width_px * self.scale
            scaled_map_height = self.map_height_px * self.scale

            # 맵을 중앙에 그리기 위한 오프셋
            self.offset_x = (self.screen_w - scaled_map_width) / 2
            self.offset_y = (self.screen_h - scaled_map_height) / 2

        # 3. 타일셋 이미지 로드
        tileset_info = self.map_data['tilesets'][0]
        tileset_image_path = tileset_info['image']
        tileset_image_path = tileset_image_path.replace('\\', '/')

        # 파일명만 추출
        image_filename = os.path.basename(tileset_image_path)
        map_dir = os.path.dirname(json_path)

        # 여러 경로를 시도
        paths_to_try = [
            os.path.join(map_dir, tileset_image_path),  # 원본 경로
            os.path.join(map_dir, image_filename),  # 같은 폴더
            tileset_image_path,  # 상대 경로 그대로
            image_filename  # 파일명만
        ]

        self.tileset_image = None
        for path in paths_to_try:
            try:
                normalized_path = os.path.normpath(path)
                self.tileset_image = load_image(normalized_path)
                break
            except:
                continue

        if self.tileset_image is None:
            raise IOError(f"Tileset을 로드할 수 없습니다. 시도한 경로들: {paths_to_try}")

        self.tileset_cols = tileset_info['columns']

        # 4. 그릴 레이어(들) 데이터 저장 (기존 코드와 동일)
        self.layers_data = []
        for layer in self.map_data['layers']:
            if layer['type'] == 'tilelayer':
                self.layers_data.append(layer['data'])

    def draw(self):
        """기본 draw 메서드 (카메라 미사용 시 - 화면에 맞게 스케일링)"""
        for layer_data in self.layers_data:
            for y in range(self.map_height_tiles):
                for x in range(self.map_width_tiles):
                    map_index = (self.map_height_tiles - 1 - y) * self.map_width_tiles + x
                    tile_id = layer_data[map_index]
                    if tile_id == 0: continue
                    src_x = ((tile_id - 1) % self.tileset_cols) * self.tile_width
                    src_y = ((tile_id - 1) // self.tileset_cols) * self.tile_height
                    src_y = self.tileset_image.h - src_y - self.tile_height

                    dest_x = (x * self.tile_width + self.tile_width // 2) * self.scale + self.offset_x
                    dest_y = (y * self.tile_height + self.tile_height // 2) * self.scale + self.offset_y

                    self.tileset_image.clip_draw(
                        src_x, src_y, self.tile_width, self.tile_height,
                        dest_x, dest_y,
                        self.tile_width * self.scale, self.tile_height * self.scale
                    )

    def draw_with_camera(self, camera_x, camera_y):
        """카메라 기준으로 렌더링"""
        # 카메라 오프셋 계산 (플레이어를 화면 중앙에 배치)
        cam_offset_x = self.screen_w // 2 - camera_x
        cam_offset_y = self.screen_h // 2 - camera_y

        for layer_data in self.layers_data:
            for y in range(self.map_height_tiles):
                for x in range(self.map_width_tiles):
                    map_index = (self.map_height_tiles - 1 - y) * self.map_width_tiles + x
                    tile_id = layer_data[map_index]
                    if tile_id == 0: continue

                    src_x = ((tile_id - 1) % self.tileset_cols) * self.tile_width
                    src_y = ((tile_id - 1) // self.tileset_cols) * self.tile_height
                    src_y = self.tileset_image.h - src_y - self.tile_height

                    # 월드 좌표를 화면 좌표로 변환 (카메라 적용)
                    world_x = x * self.tile_width + self.tile_width // 2
                    world_y = y * self.tile_height + self.tile_height // 2

                    screen_x = world_x + cam_offset_x
                    screen_y = world_y + cam_offset_y

                    # 화면 밖의 타일은 그리지 않음 (최적화)
                    if (screen_x + self.tile_width // 2 < 0 or screen_x - self.tile_width // 2 > self.screen_w or
                        screen_y + self.tile_height // 2 < 0 or screen_y - self.tile_height // 2 > self.screen_h):
                        continue

                    self.tileset_image.clip_draw(
                        src_x, src_y, self.tile_width, self.tile_height,
                        screen_x, screen_y,
                        self.tile_width, self.tile_height
                    )

    def get_collision_boxes(self):
        """Collisions 레이어(objectgroup)에서 충돌 박스 추출"""
        boxes = []

        # 'Collisions' objectgroup 찾기
        for layer in self.map_data['layers']:
            if layer.get('name') == 'Collisions' and layer['type'] == 'objectgroup':
                for obj in layer.get('objects', []):
                    # 객체의 좌표와 크기 (Tiled에서는 y=0이 위쪽)
                    x = obj['x']
                    y = obj['y']
                    width = obj['width']
                    height = obj['height']

                    # Tiled 좌표계: y=0이 위쪽, 아래로 갈수록 y 증가
                    # Pico2D 좌표계: y=0이 아래쪽, 위로 갈수록 y 증가
                    pico2d_bottom = self.map_height_px - y - height
                    pico2d_top = self.map_height_px - y

                    if self.use_camera:
                        # 카메라 사용 시: 월드 좌표계로 저장 (스케일/오프셋 적용 안 함)
                        left = x
                        bottom = pico2d_bottom
                        right = x + width
                        top = pico2d_top
                    else:
                        # 카메라 미사용 시: 스케일과 오프셋 적용
                        left = x * self.scale + self.offset_x
                        bottom = pico2d_bottom * self.scale + self.offset_y
                        right = (x + width) * self.scale + self.offset_x
                        top = pico2d_top * self.scale + self.offset_y

                    boxes.append((left, bottom, right, top))
                    print(f"충돌 박스 추가: x={x}, y={y}, w={width}, h={height} -> Pico2D: ({left:.1f}, {bottom:.1f}, {right:.1f}, {top:.1f})")
                break

        return boxes

    def update(self, dt):
        pass