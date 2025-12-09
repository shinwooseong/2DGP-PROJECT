# 여기에 플레이어 객체를 저장해서 모든 모드가 공유하게 하기!
from pico2d import load_wav

player = None
tiled_map = None

# 효과음 변수 (모든 모드에서 공유)
se_attack = None  # 플레이어 공격 효과음
se_monster_hit = None  # 몬스터 피격 효과음
se_potion = None  # 포션 사용 효과음
se_roll = None  # 구르기 효과음
se_check = None  # UI 체크 효과음
se_trans_attack = None  # 변신 공격 효과음
se_queen_shot = None  # 여왕벌 샷 효과음
se_bee_fly = None  # 벌 날아오는 효과음
shop_entrance_sound = None  # 상점 입장 효과음

# 효과음 관리
def init_all_sounds():
    global se_attack, se_monster_hit, se_potion, se_roll, se_check, se_trans_attack
    global se_queen_shot, se_bee_fly, shop_entrance_sound

    sound_list = [
        ('se_roll', 'Sound/dash.wav', 64),
        ('se_attack', 'Sound/attack.wav', 64),
        ('se_monster_hit', 'Sound/monster_hit.wav', 64),
        ('se_potion', 'Sound/potion.wav', 64),
        ('se_check', 'Sound/check.wav', 64),
        ('se_trans_attack', 'Sound/trans_attack.wav', 14),
        ('se_queen_shot', 'Sound/queen_shot2.wav', 64),
        ('se_bee_fly', 'Sound/bee_fly.wav', 64),
        ('shop_entrance_sound', 'Sound/shop_entrance.wav', 64),
    ]

    for var_name, file_path, volume in sound_list:
        try:
            sound = load_wav(file_path)
            if hasattr(sound, 'set_volume'):
                sound.set_volume(volume)
            globals()[var_name] = sound
            print(f"[SERVER] {var_name} ({file_path}) 로드 완료")
        except Exception as e:
            print(f"[SERVER] {var_name} ({file_path}) 로드 실패: {e}")

def init_roll_sounds():
    """하위 호환성을 위해 유지"""
    init_all_sounds()
