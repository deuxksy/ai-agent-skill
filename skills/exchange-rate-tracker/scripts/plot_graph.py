#!/usr/bin/env python3
"""
환율 그래프 생성 스크립트
USD/KRW, USD/VND 환율 xychart 생성
"""

import json
from datetime import datetime
from pathlib import Path

DATA_FILE = Path(__file__).parent.parent / "references" / "exchange-rates.json"
OUTPUT_DIR = Path(__file__).parent.parent / "output"

def load_data():
    """환율 데이터 로드"""
    if not DATA_FILE.exists():
        print("No data file found")
        return None, None

    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    return data.get("krw_rates", []), data.get("vnd_rates", [])

def generate_sparkline(values, bars=8):
    """스파크라인 생성 (유니코드 블록)"""
    if not values or len(values) < 2:
        return "▁"

    recent = values[-bars:]
    min_val = min(recent)
    max_val = max(recent)
    range_val = max_val - min_val

    spark_chars = ['▁', '▂', '▃', '▄', '▅', '▆', '▇', '█']

    sparkline = ""
    for val in recent:
        if range_val > 0:
            idx = int((val - min_val) / range_val * (len(spark_chars) - 1))
        else:
            idx = 3
        sparkline += spark_chars[idx]

    return sparkline

def get_trend(values):
    """추세 분석 (상승/하락/보합)"""
    if not values or len(values) < 2:
        return "→"

    current = values[-1]
    previous = values[-2]
    diff = current - previous

    if diff > 0:
        return f"↑ +{diff:,.1f}"
    elif diff < 0:
        return f"↓ {diff:,.1f}"
    else:
        return "→"

def generate_xychart(krw_rates, vnd_rates, days=7):
    """Mermaid xychart 생성 (KRW + VND, 색상 구분)"""
    if not krw_rates:
        return None

    recent_krw = krw_rates[-(days*4):] if len(krw_rates) > days*4 else krw_rates
    recent_vnd = vnd_rates[-(days*4):] if vnd_rates and len(vnd_rates) > days*4 else vnd_rates

    krw_recent = recent_krw[-8:]
    x_labels = [f'"{r["date"][5:]} {r["time"]}"' for r in krw_recent]
    krw_values = [r['rate'] for r in krw_recent]

    vnd_values = None
    if recent_vnd and len(recent_vnd) >= 8:
        vnd_recent = recent_vnd[-8:]
        vnd_values = [r['rate'] for r in vnd_recent]

    min_krw = int(min(krw_values) - 10)
    max_krw = int(max(krw_values) + 10)

    output = []
    output.append("```mermaid")
    output.append("%%{init: {'theme': 'base', 'themeVariables': { 'xyChart': {'plotColorPalette': '#3b82f6, #ef4444'}}}}%%")
    output.append("xychart")
    output.append(f'    title "Exchange Rates (USD)"')
    output.append(f'    x-axis [{", ".join(x_labels)}]')
    output.append(f'    y-axis "KRW" {min_krw} --> {max_krw}')
    output.append(f'    line [{", ".join([str(v) for v in krw_values])}]')

    if vnd_values:
        min_vnd = int(min(vnd_values) - 100)
        max_vnd = int(max(vnd_values) + 100)
        output.append(f'    y-axis "VND" {min_vnd} --> {max_vnd}')
        output.append(f'    line [{", ".join([str(v) for v in vnd_values])}]')

    output.append("```")

    return "\n".join(output)

def generate_report(krw_rates, vnd_rates):
    """환율 리포트 생성"""
    if not krw_rates:
        return "데이터 없음"

    output = []
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    output.append(f"**환율 리포트** ({now})")
    output.append("━" * 40)

    output.append("\n**현재 환율**")

    if krw_rates:
        latest = krw_rates[-1]
        current_krw = latest['rate']
        date_str = f"{latest['date']} {latest['time']}"
        sparkline_krw = generate_sparkline([r['rate'] for r in krw_rates])
        trend_krw = get_trend([r['rate'] for r in krw_rates])
        output.append(f"- **USD/KRW** ({date_str}): {current_krw:,.1f}원 {sparkline_krw} {trend_krw}")

    if vnd_rates:
        latest = vnd_rates[-1]
        current_vnd = latest['rate']
        date_str = f"{latest['date']} {latest['time']}"
        sparkline_vnd = generate_sparkline([r['rate'] for r in vnd_rates])
        trend_vnd = get_trend([r['rate'] for r in vnd_rates])
        output.append(f"- **USD/VND** ({date_str}): {current_vnd:,.0f}동 {sparkline_vnd} {trend_vnd}")

    xychart = generate_xychart(krw_rates, vnd_rates)
    if xychart:
        output.append("\n**7일 추세 그래프**")
        output.append(xychart)

    output.append("\n**7일 통계**")

    if krw_rates and len(krw_rates) >= 7:
        week_krw = [r['rate'] for r in krw_rates[-7:]]
        output.append(f"- KRW: {min(week_krw):,.0f} ~ {max(week_krw):,.0f} (평균 {sum(week_krw)/len(week_krw):,.0f})")

    if vnd_rates and len(vnd_rates) >= 7:
        week_vnd = [r['rate'] for r in vnd_rates[-7:]]
        output.append(f"- VND: {min(week_vnd):,.0f} ~ {max(week_vnd):,.0f} (평균 {sum(week_vnd)/len(week_vnd):,.0f})")

    output.append("━" * 40)

    return "\n".join(output)

def main():
    """메인 실행"""
    krw_rates, vnd_rates = load_data()

    if not krw_rates and not vnd_rates:
        print("데이터 없음")
        return

    report = generate_report(krw_rates, vnd_rates)
    print("\n" + report)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    report_file = OUTPUT_DIR / f"exchange_rate_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"\n저장됨: {report_file}")

if __name__ == "__main__":
    main()
