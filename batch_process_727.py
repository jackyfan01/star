# batch_process_727.py
# 批量处理公元727年全年月相数据（365天）
# 输出CSV + 对称性初步统计

import pandas as pd
from datetime import datetime, timedelta
from phase_symmetry_offline import annotate_lunar_state

def generate_date_range(year=727):
    """生成全年UTC日期列表（无时区偏移，Skyfield内部处理为TT/UTC）"""
    start = datetime(year, 1, 1)
    end = datetime(year, 12, 31)
    dates = []
    current = start
    while current <= end:
        dates.append(current)
        current += timedelta(days=1)
    return dates

def main():
    print("🚀 开始处理公元727年全年月相数据...")
    dates = generate_date_range(727)
    results = []

    for i, date in enumerate(dates, 1):
        try:
            state = annotate_lunar_state(date)
            results.append(state)
            if i % 30 == 0:
                print(f"  已处理 {i}/365 天...")
        except Exception as e:
            print(f"⚠️  错误于 {date}: {e}")
            results.append({
                "date": date.strftime("%Y-%m-%d"),
                "phase_angle": None,
                "sym_offset_from_full": None,
                "hexagram": None,
                "tiangan": None,
                "visibility": "error",
                "is_pivot": False,
                "cycle_half": None
            })

    df = pd.DataFrame(results)
    
    output_file = "lunar_phases_727_ad.csv"
    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"\n✅ 数据已保存至: {output_file}")
    
    print("\n🔍 初步对称性统计（以望日为中心）:")
    
    hex_counts = df['hexagram'].value_counts()
    print("\n卦象分布:")
    print(hex_counts)
    
    dui_days = df[df['hexagram'] == '兑']['sym_offset_from_full'].abs().mean()
    gen_days = df[df['hexagram'] == '艮']['sym_offset_from_full'].abs().mean()
    print(f"\n兑卦平均距望日: {dui_days:.1f}°")
    print(f"艮卦平均距望日: {gen_days:.1f}°")
    print(f"→ 对称偏差: {abs(dui_days - gen_days):.1f}°")
    
    zhen_days = df[df['hexagram'] == '震']['sym_offset_from_full'].abs().mean()
    kun_days = df[df['hexagram'] == '坤']['sym_offset_from_full'].abs().mean()
    print(f"\n震卦平均距望日: {zhen_days:.1f}°")
    print(f"坤卦平均距望日: {kun_days:.1f}°")
    print(f"→ 对称偏差: {abs(zhen_days - kun_days):.1f}°")
    
    pivot_count = df['is_pivot'].sum()
    print(f"\n全年乾坤转换点（望/晦）天数: {pivot_count}")
    
    vis_dist = df['visibility'].value_counts()
    print(f"\n可见性分布:\n{vis_dist}")

if __name__ == "__main__":
    main()
