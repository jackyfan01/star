# phase_symmetry_offline.py
# 以望日（φ=180°）为对称中心的月相标注系统（离线版）
# 使用简化算法计算月相角，无需下载大型星历表
# 李承风 | 2026年1月16日

from datetime import datetime, timedelta
import math

CHANGAN_LAT = 34.3
CHANGAN_LON = 108.9

def julian_day(year, month, day):
    """计算儒略日（简化算法）"""
    if month <= 2:
        year -= 1
        month += 12
    A = int(year / 100)
    B = 2 - A + int(A / 4)
    JD = int(365.25 * (year + 4716)) + int(30.6001 * (month + 1)) + day + B - 1524.5
    return JD

def lunar_phase_angle(jd):
    """
    计算月相角 φ ∈ [0, 360)°
    使用 Meeus 简化算法
    - 0°: 合朔（新月）
    - 180°: 望（满月）
    """
    T = (jd - 2451545.0) / 36525.0
    
    sun_mean_longitude = (280.46646 + T * (36000.76983 + 0.0003032 * T)) % 360
    moon_mean_longitude = (218.3164477 + T * (481267.88123421 - 0.0015786 * T)) % 360
    
    phi = (moon_mean_longitude - sun_mean_longitude) % 360
    return phi

def assign_nayin_hexagram(phi):
    """
    根据相位角 φ 分配纳甲卦象与天干（以望日为对称中心）
    
    对称规则：
      - 上半月（φ < 180°）：昏见为主 → 震、兑、乾
      - 下半月（φ > 180°）：旦见为主 → 巽、艮、坤
      - 以 180° 为反射轴：φ ↔ 360° - φ 应成对出现
    """
    bounds = {
        'zhen':   ( 15,  45),
        'dui':    ( 75, 105),
        'qian':   (165, 195),
        'gen':    (255, 285),
        'xun':    (215, 245),
        'kun':    (315, 345),
    }
    
    for name, (low, high) in bounds.items():
        if low <= phi <= high:
            mapping = {
                'zhen': ('震', '庚'),
                'dui':  ('兑', '丁'),
                'qian': ('乾', '甲'),
                'xun':  ('巽', '辛'),
                'gen':  ('艮', '丙'),
                'kun':  ('坤', '乙'),
            }
            return mapping[name]
    
    return (None, None)

def is_evening_or_morning_simplified(phase_angle):
    """
    根据月相角简化判断昏旦可见性
    返回: 'evening', 'morning', 'both', 'none'
    
    规律：
    - 上半月（0-180°）：昏见为主，月亮在日落后可见
    - 下半月（180-360°）：旦见为主，月亮在日出前可见
    - 望日附近：整夜可见 (both)
    - 朔日附近：整夜不可见 (none)
    """
    if phase_angle > 350 or phase_angle < 10:
        return 'none'
    elif phase_angle >= 170 and phase_angle <= 190:
        return 'both'
    elif phase_angle < 180:
        return 'evening'
    else:
        return 'morning'

def annotate_lunar_state(date_utc):
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
    jd = julian_day(date_utc.year, date_utc.month, date_utc.day)
    phi = lunar_phase_angle(jd)
    
    sym_offset = ((phi - 180 + 180) % 360) - 180
    
    hexagram, tiangan = assign_nayin_hexagram(phi)
    
    visibility = is_evening_or_morning_simplified(phi)
    
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
