# tiled_map.py
import json
import os
from pico2d import load_image, get_canvas_width, get_canvas_height, clamp


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

        # 카메라 관련 초기값
        self.camera_x = 0
        self.camera_y = 0
        self.cam_offset_x = 0
        self.cam_offset_y = 0

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
        if self.use_camera:
            # 플레이어 위치 가져오기 (지연 임포트로 순환 참조 방지)
            import server
            if server.player:
                # 1. 카메라의 중심 좌표 목표 (플레이어 위치)
                target_cam_x = server.player.x
                target_cam_y = server.player.y

                # 맵이 화면보다 작을 경우에 대한 예외 처리
                if self.map_width_px < self.screen_w:
                    cam_x = self.map_width_px // 2
                else:
                    cam_x = clamp(self.screen_w // 2, target_cam_x, self.map_width_px - self.screen_w // 2)

                if self.map_height_px < self.screen_h:
                    cam_y = self.map_height_px // 2
                else:
                    cam_y = clamp(self.screen_h // 2, target_cam_y, self.map_height_px - self.screen_h // 2)

                # 3. 계산된 카메라 위치로 그리기
                # 저장해둔 카메라 위치/오프셋은 다른 객체들이 참조할 수 있게 보관
                self.camera_x = cam_x
                self.camera_y = cam_y
                self.cam_offset_x = self.screen_w // 2 - cam_x
                self.cam_offset_y = self.screen_h // 2 - cam_y
                self.draw_with_camera(cam_x, cam_y)
        else:
            # 기존의 고정된 화면 그리기 (전체 맵 축소)
            self._draw_static()

    def _draw_static(self):
        # 기존 draw() 로직을 이쪽으로 이동 (이름만 변경)
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
        # 화면 중앙을 기준으로 카메라 오프셋 계산
        cam_offset_x = self.screen_w // 2 - camera_x
        cam_offset_y = self.screen_h // 2 - camera_y

        # 화면에 보일 타일 범위만 계산 (최적화 - Culling)
        # 화면 왼쪽 끝의 월드 좌표 = camera_x - screen_w // 2
        view_left = camera_x - self.screen_w // 2
        view_right = camera_x + self.screen_w // 2
        view_bottom = camera_y - self.screen_h // 2
        view_top = camera_y + self.screen_h // 2

        # 인덱스로 변환 (여유분 1타일 추가)
        start_x = max(0, int(view_left // self.tile_width))
        end_x = min(self.map_width_tiles, int(view_right // self.tile_width) + 1)
        start_y = max(0, int(view_bottom // self.tile_height))
        end_y = min(self.map_height_tiles, int(view_top // self.tile_height) + 1)

        for layer_data in self.layers_data:
            for y in range(start_y, end_y):
                for x in range(start_x, end_x):
                    map_index = (self.map_height_tiles - 1 - y) * self.map_width_tiles + x
                    tile_id = layer_data[map_index]
                    if tile_id == 0: continue

                    src_x = ((tile_id - 1) % self.tileset_cols) * self.tile_width
                    src_y = ((tile_id - 1) // self.tileset_cols) * self.tile_height
                    src_y = self.tileset_image.h - src_y - self.tile_height

                    world_x = x * self.tile_width + self.tile_width // 2
                    world_y = y * self.tile_height + self.tile_height // 2

                    screen_x = world_x + cam_offset_x
                    screen_y = world_y + cam_offset_y

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

    def update_camera(self, player_x, player_y):
        if not self.use_camera:
            return
        target_cam_x = player_x
        target_cam_y = player_y

        if self.map_width_px < self.screen_w:
            cam_x = self.map_width_px // 2
        else:
            cam_x = clamp(self.screen_w // 2, target_cam_x, self.map_width_px - self.screen_w // 2)

        if self.map_height_px < self.screen_h:
            cam_y = self.map_height_px // 2
        else:
            cam_y = clamp(self.screen_h // 2, target_cam_y, self.map_height_px - self.screen_h // 2)

        self.camera_x = cam_x
        self.camera_y = cam_y
        self.cam_offset_x = self.screen_w // 2 - cam_x
        self.cam_offset_y = self.screen_h // 2 - cam_y
