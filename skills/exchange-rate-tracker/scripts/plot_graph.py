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

def _parse_dt(entry):
    """JSON 엔트리에서 datetime 파싱 (date + time)"""
    try:
        return datetime.strptime(f"{entry['date']} {entry['time']}", "%Y-%m-%d %H:%M")
    except (KeyError, ValueError):
        return datetime.fromtimestamp(entry.get("timestamp", 0))


def generate_png_charts(krw_rates, vnd_rates, output_dir, points=8):
    """matplotlib PNG 그래프 생성 — 일별 + 추세선 (KRW/VND)

    workspace create_graphs.py 로직을 실제 JSON 데이터 기반으로 이식.
    지연 import로 Mermaid 리포트 경로는 matplotlib 의존성 없이 동작.
    """
    import matplotlib
    matplotlib.use("Agg")  # 헤드리스 환경 (SteamOS 등)
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    import numpy as np

    if not krw_rates or len(krw_rates) < 2:
        return None

    # 한국어 폰트 (NanumGothic 우선, 미설치 시 fallback 경고만)
    import matplotlib.font_manager as fm
    available = {f.name for f in fm.fontManager.ttflist}
    for font in ["NanumGothic", "Noto Sans CJK KR", "Noto Sans CJK JP", "Malgun Gothic"]:
        if font in available:
            plt.rcParams["font.family"] = font
            break
    plt.rcParams["axes.unicode_minus"] = False

    files = {}

    def _plot_pair(rates, title, color, trend_color, prefix):
        """단일 통화 일별 + 추세 PNG 2종 생성"""
        recent = rates[-points:]
        dates = [_parse_dt(r) for r in recent]
        values = [r["rate"] for r in recent]

        # 일별 그래프
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(dates, values, marker="o", linewidth=2, markersize=8, color=color)
        ax.set_title(f"{title} (일별)", fontsize=16, fontweight="bold")
        ax.set_xlabel("날짜", fontsize=12)
        ax.set_ylabel("환율", fontsize=12)
        ax.grid(True, alpha=0.3)
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d %H:%M"))
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        fig.autofmt_xdate(rotation=45)
        for d, v in zip(dates, values):
            ax.annotate(f"{v:,.0f}", (d, v), xytext=(0, 10),
                        textcoords="offset points", ha="center", fontsize=10, fontweight="bold")
        fig.tight_layout()
        daily_path = output_dir / f"{prefix}_daily.png"
        fig.savefig(daily_path, dpi=300, bbox_inches="tight")
        plt.close(fig)
        files[f"{prefix}_daily"] = daily_path

        # 추세 그래프 (회귀선)
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(dates, values, marker="s", linewidth=3, markersize=8, color=color)
        if len(values) >= 2:
            z = np.polyfit(range(len(values)), values, 1)
            p = np.poly1d(z)
            ax.plot(dates, p(range(len(values))), "--", alpha=0.7,
                    color=trend_color, linewidth=2, label="추세선")
            ax.legend()
        ax.set_title(f"{title} (추세)", fontsize=16, fontweight="bold")
        ax.set_xlabel("날짜", fontsize=12)
        ax.set_ylabel("환율", fontsize=12)
        ax.grid(True, alpha=0.3)
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d %H:%M"))
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        fig.autofmt_xdate(rotation=45)
        fig.tight_layout()
        trend_path = output_dir / f"{prefix}_trend.png"
        fig.savefig(trend_path, dpi=300, bbox_inches="tight")
        plt.close(fig)
        files[f"{prefix}_trend"] = trend_path

    _plot_pair(krw_rates, "USD/KRW", "#1E88E5", "#FF6F00", "krw")
    if vnd_rates and len(vnd_rates) >= 2:
        _plot_pair(vnd_rates, "USD/VND", "#E53935", "#FF6F00", "vnd")

    return files


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

    # PNG 그래프 (matplotlib, 데이터 2포인트 이상 시)
    png_files = generate_png_charts(krw_rates, vnd_rates, OUTPUT_DIR)
    if png_files:
        for key, path in png_files.items():
            print(f"PNG: {path}")

if __name__ == "__main__":
    main()
