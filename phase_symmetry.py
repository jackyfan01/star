# phase_symmetry.py
# 以望日（φ=180°）为对称中心的月相标注系统
# 李承风 | 2026年1月16日

from skyfield.api import load, Topos
import numpy as np
from datetime import datetime, timedelta

ts = load.timescale()
eph = load('de421.bsp')
earth = eph['earth']
sun = eph['sun']
moon = eph['moon']

CHANGAN = Topos('34.3 N', '108.9 E')

def lunar_phase_angle(jd):
    """
    计算月相角 φ ∈ [0, 360)°
    - 0°: 合朔（新月）
    - 180°: 望（满月）
    """
    t = ts.tt_jd(jd)
    sun_pos = sun.at(t).ecliptic_position().au
    moon_pos = moon.at(t).ecliptic_position().au
    
    lambda_sun = np.arctan2(sun_pos[1], sun_pos[0]) * 180 / np.pi % 360
    lambda_moon = np.arctan2(moon_pos[1], moon_pos[0]) * 180 / np.pi % 360
    
    phi = (lambda_moon - lambda_sun) % 360
    return phi

def assign_nayin_hexagram(phi):
    """
    根据相位角 φ 分配纳甲卦象与天干（以望日为对称中心）
    
    先天八卦对称关系：
      - 震（45°）↔ 巽（315°）
      - 艮（225°）↔ 兑（135°）
      - 乾（180°）↔ 坤（0°/360°）
    
    月相分配：
      - 上半月（φ < 180°）：昏见为主 → 震、兑、乾
      - 下半月（φ > 180°）：旦见为主 → 巽、艮、坤
    """
    bounds = {
        'zhen':   ( 30,  60),   # 震: 45°
        'dui':    (120, 150),  # 兑: 135°
        'qian':   (165, 195),  # 乾: 180°
        'gen':    (210, 240),  # 艮: 225°
        'xun':    (300, 330),  # 巽: 315°
        'kun':    (345,  15),   # 坤: 0°/360°
    }
    
    for name, (low, high) in bounds.items():
        if low <= phi <= high:
            mapping = {
                'zhen': ('震', '辛'),
                'dui':  ('兑', '丁'),
                'qian': ('乾', '甲'),
                'xun':  ('巽', '癸'),
                'gen':  ('艮', '丙'),
                'kun':  ('坤', '乙'),
            }
            return mapping[name]
    
    return (None, None)

def is_evening_or_morning(jd, location=CHANGAN):
    """
    判断月亮在当日是否黄昏或平明可见
    返回: 'evening', 'morning', 'both', 'none'
    """
    t_utc = ts.tt_jd(jd).utc_datetime()
    t0 = ts.utc(t_utc.year, t_utc.month, t_utc.day)
    t1 = ts.utc(t_utc.year, t_utc.month, t_utc.day + 1)
    
    obs = earth + location
    
    try:
        t_sun, y_sun = obs.find_discrete(t0, t1, sun)
        sun_rise = t_sun[y_sun == 1][0].utc_datetime() if len(t_sun[y_sun == 1]) > 0 else None
        sun_set  = t_sun[y_sun == -1][0].utc_datetime() if len(t_sun[y_sun == -1]) > 0 else None
    except:
        return 'none'
    
    try:
        t_moon, y_moon = obs.find_discrete(t0, t1, moon)
        rises = [t.utc_datetime() for t, y in zip(t_moon, y_moon) if y == 1]
        sets  = [t.utc_datetime() for t, y in zip(t_moon, y_moon) if y == -1]
        moon_rise = rises[0] if rises else None
        moon_set  = sets[0] if sets else None
    except:
        return 'none'
    
    if not all([sun_rise, sun_set, moon_rise, moon_set]):
        return 'none'
    
    dusk_start = sun_set
    dusk_end = sun_set + timedelta(minutes=60)
    
    dawn_start = sun_rise - timedelta(minutes=60)
    dawn_end = sun_rise
    
    evening = moon_rise <= dusk_end and moon_set >= dusk_start
    morning = moon_rise <= dawn_end and moon_set >= dawn_start
    
    if evening and morning:
        return 'both'
    elif evening:
        return 'evening'
    elif morning:
        return 'morning'
    else:
        return 'none'

def annotate_lunar_state(date_utc, location=CHANGAN):
    """
    主函数：输入UTC日期，输出以望日为中心的月相标注
    
    返回字典包含：
      - phase_angle: 相位角 φ
      - symmetry_offset: 距离望日的偏移（-180 ~ +180）
      - hexagram: 卦名（震、兑、乾、巽、艮、坤）
      - tiangan: 天干
      - visibility: 可见性
      - is_pivot: 是否为转换点（望/晦）
    """
    jd = ts.utc(date_utc.year, date_utc.month, date_utc.day).tt
    phi = lunar_phase_angle(jd)
    
    sym_offset = ((phi - 180 + 180) % 360) - 180
    
    hexagram, tiangan = assign_nayin_hexagram(phi)
    
    visibility = is_evening_or_morning(jd, location)
    
    is_pivot = False
    if 165 <= phi <= 195:
        is_pivot = True
    elif phi <= 15 or phi >= 345:
        is_pivot = True
    
    return {
        "date": date_utc.strftime("%Y-%m-%d"),
        "phase_angle": round(phi, 2),
        "sym_offset_from_full": round(sym_offset, 2),
        "hexagram": hexagram,
        "tiangan": tiangan,
        "visibility": visibility,
        "is_pivot": is_pivot,
        "cycle_half": "upper" if phi < 180 else "lower"
    }

if __name__ == "__main__":
    test1 = datetime(727, 3, 15)
    print("望日测试:", annotate_lunar_state(test1))
    
    test2 = datetime(727, 3, 3)
    print("初三测试:", annotate_lunar_state(test2))
    
    test3 = datetime(727, 3, 23)
    print("廿三测试:", annotate_lunar_state(test3))
    
    test4 = datetime(727, 3, 30)
    print("晦日测试:", annotate_lunar_state(test4))
