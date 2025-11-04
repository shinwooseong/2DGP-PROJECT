# game_framework.py
import time

stack = None # 모드 스택
running = True
frame_time = 0.0

def run(start_mode):
    global running, stack, frame_time
    running = True
    stack = [start_mode]
    start_mode.init()

    current_time = time.time()

    while running:
        now = time.time()
        frame_time = now - current_time
        current_time = now

        # 스택의 맨 위 모드(현재 모드)를 실행
        stack[-1].handle_events()
        stack[-1].update(frame_time) # dt(frame_time)를 전달
        stack[-1].draw()

    # 스택에 남아있는 모든 모드를 종료
    while (len(stack) > 0):
        stack[-1].finish()
        stack.pop()

def quit():
    global running
    running = False

def change_mode(mode):
    global stack
    if (len(stack) > 0):
        stack[-1].finish()
        stack.pop()
    stack.append(mode)
    mode.init()

def push_mode(mode):
    global stack
    if (len(stack) > 0):
        stack[-1].pause()
    stack.append(mode)
    mode.init()

def pop_mode():
    global stack
    if (len(stack) > 0):
        stack[-1].finish()
        stack.pop()
    if (len(stack) > 0):
        stack[-1].resume()