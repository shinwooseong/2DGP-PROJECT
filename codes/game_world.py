# layer 0: 배경
# layer 1: 중간 (Player, Monsters)
# layer 2: UI
world = [[], [], []]

def add_object(o, depth=1):
    world[depth].append(o)

def add_objects(ol, depth=1):
    world[depth] += ol

def remove_object(o):
    for layer in world:
        if o in layer:
            layer.remove(o)
            return
    raise ValueError('Cannot delete non existing object')

def all_objects():
    for layer in world:
        for o in layer:
            yield o

def clear():
    for o in all_objects():
        del o
    for layer in world:
        layer.clear()

def update(dt):
    for o in all_objects():
        o.update(dt) # 모든 객체의 update에 dt 전달

def render():
    for layer in world:
        for o in layer:
            o.draw()

# 특정 레이어의 객체들을 가져오는 함수 (예: 충돌 처리용)
def objects_at_layer(layer_index):
    return world[layer_index]