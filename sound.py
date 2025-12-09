from pico2d import load_music, load_wav

bgm_music = None
sfx_sounds = {}

def init():
    global bgm_music, sfx_sounds

    #  효과음 로딩해놓기
    sfx_data = [

    ]

    for key, path in sfx_data:
        sfx_sounds[key] = load_wav(path)
        sfx_sounds[key].set_volume(32)  # 0 ~ 128 사이 (소리 크기 조절)



def play_bgm(name):
    global bgm_music

    # BGM 파일 경로 매핑
    bgm_files = {
        'title': 'sound/music/title_theme.mp3',
        'village': 'sound/music/village_theme.mp3',
        'dungeon': 'sound/music/dungeon_theme.mp3',
        'boss': 'sound/music/boss_theme.mp3',
    }

    path = bgm_files.get(name)
    if not path:
        return

    try:
        bgm_music = load_music(path)
        bgm_music.set_volume(64)  # 배경음악 볼륨
        bgm_music.repeat_play()  # 무한 반복 재생
    except Exception as e:
        print(f"BGM 로드 실패 ({name}): {e}")


def play_sfx(name):
    if name in sfx_sounds:
        sfx_sounds[name].play()


def finish():
    global bgm_music, sfx_sounds
    del bgm_music
    sfx_sounds.clear()