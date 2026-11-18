#!/usr/bin/env python3
"""
환율 그래프 생성 스크립트
USD 기준 6개 통화(KRW, VND, JPY, CNY, EUR, GBP) 환율 xychart 생성
"""

import json
from datetime import datetime
from pathlib import Path

DATA_FILE = Path(__file__).parent.parent / "references" / "exchange-rates.json"
OUTPUT_DIR = Path(__file__).parent.parent / "output"

# 통화별 표시 설정 (USD 기준: 1 USD = N 통화)
CURRENCIES = {
    "KRW": {"unit": "원",    "fmt": "{:,.1f}", "color": "#1E88E5"},
    "VND": {"unit": "동",    "fmt": "{:,.0f}", "color": "#E53935"},
    "JPY": {"unit": "엔",    "fmt": "{:,.1f}", "color": "#43A047"},
    "CNY": {"unit": "위안",  "fmt": "{:,.2f}", "color": "#8E24AA"},
    "EUR": {"unit": "유로",  "fmt": "{:,.2f}", "color": "#F4511E"},
    "GBP": {"unit": "파운드", "fmt": "{:,.2f}", "color": "#00897B"},
}

def load_data():
    """환율 데이터 로드 → {통화: 엔트리 리스트}"""
    if not DATA_FILE.exists():
        print("No data file found")
        return {}

    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    return {ccy: data.get(f"{ccy.lower()}_rates", []) for ccy in CURRENCIES}

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

def _fmt_bound(value):
    """xychart y-axis 경계값 포맷 (EUR/GBP 등 소수 통화 대응)"""
    return f"{value:g}"

def generate_xychart(rates, points=8):
    """Mermaid xychart 생성 — 기준 통화 포인트 수와 일치하는 통화만 라인 추가"""
    available = {c: r[-points:] for c, r in rates.items() if r}
    if not available:
        return None

    base = next(iter(available.values()))
    base_len = len(base)
    matched = {c: r[-base_len:] for c, r in available.items() if len(r) >= base_len}
    x_labels = [f'"{r["date"][5:]} {r["time"]}"' for r in base]
    palette = ", ".join(CURRENCIES[c]['color'] for c in matched)

    output = []
    output.append("```mermaid")
    output.append(f"%%{{init: {{'theme': 'base', 'themeVariables': {{ 'xyChart': {{'plotColorPalette': '{palette}'}}}}}}}}%%")
    output.append("xychart")
    output.append('    title "Exchange Rates (per 1 USD)"')
    output.append(f'    x-axis [{", ".join(x_labels)}]')

    for ccy, entries in matched.items():
        values = [e['rate'] for e in entries]
        pad = max((max(values) - min(values)) * 0.2, max(values) * 0.001, 0.01)
        output.append(f'    y-axis "{ccy}" {_fmt_bound(min(values) - pad)} --> {_fmt_bound(max(values) + pad)}')
        output.append(f'    line [{", ".join(_fmt_bound(v) for v in values)}]')

    output.append("```")

    return "\n".join(output)

def _parse_dt(entry):
    """JSON 엔트리에서 datetime 파싱 (date + time)"""
    try:
        return datetime.strptime(f"{entry['date']} {entry['time']}", "%Y-%m-%d %H:%M")
    except (KeyError, ValueError):
        return datetime.fromtimestamp(entry.get("timestamp", 0))


def generate_png_charts(rates, output_dir, points=8):
    """matplotlib PNG 그래프 생성 — 일별 + 추세선 (통화별)

    지연 import로 Mermaid 리포트 경로는 matplotlib 의존성 없이 동작.
    """
    import matplotlib
    matplotlib.use("Agg")  # 헤드리스 환경 (SteamOS 등)
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    import numpy as np

    plt.rcParams["axes.unicode_minus"] = False

    files = {}

    def _plot_pair(rates_list, title, color, trend_color, prefix):
        """단일 통화 일별 + 추세 PNG 2종 생성"""
        recent = rates_list[-points:]
        dates = [_parse_dt(r) for r in recent]
        values = [r["rate"] for r in recent]

        # 값 크기에 따라 주석 포맷 결정 (EUR/GBP 등 소수 통화 대응)
        annot_fmt = "{:,.2f}" if max(values) < 10 else "{:,.0f}"

        # 일별 그래프
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(dates, values, marker="o", linewidth=2, markersize=8, color=color)
        ax.set_title(f"{title} (Daily)", fontsize=16, fontweight="bold")
        ax.set_xlabel("Date", fontsize=12)
        ax.set_ylabel("Rate", fontsize=12)
        ax.grid(True, alpha=0.3)
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d %H:%M"))
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        fig.autofmt_xdate(rotation=45)
        for d, v in zip(dates, values):
            ax.annotate(annot_fmt.format(v), (d, v), xytext=(0, 10),
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
                    color=trend_color, linewidth=2, label="Trend")
            ax.legend()
        ax.set_title(f"{title} (Trend)", fontsize=16, fontweight="bold")
        ax.set_xlabel("Date", fontsize=12)
        ax.set_ylabel("Rate", fontsize=12)
        ax.grid(True, alpha=0.3)
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d %H:%M"))
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        fig.autofmt_xdate(rotation=45)
        fig.tight_layout()
        trend_path = output_dir / f"{prefix}_trend.png"
        fig.savefig(trend_path, dpi=300, bbox_inches="tight")
        plt.close(fig)
        files[f"{prefix}_trend"] = trend_path

    for ccy, conf in CURRENCIES.items():
        ccy_rates = rates.get(ccy) or []
        if len(ccy_rates) >= 2:
            _plot_pair(ccy_rates, f"USD/{ccy}", conf["color"], "#FF6F00", ccy.lower())

    return files


def generate_report(rates):
    """환율 리포트 생성"""
    if not any(rates.values()):
        return "데이터 없음"

    output = []
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    output.append(f"**환율 리포트** ({now})")
    output.append("━" * 40)

    output.append("\n**현재 환율**")

    for ccy, conf in CURRENCIES.items():
        ccy_rates = rates.get(ccy) or []
        if not ccy_rates:
            continue
        latest = ccy_rates[-1]
        date_str = f"{latest['date']} {latest['time']}"
        values = [r['rate'] for r in ccy_rates]
        sparkline = generate_sparkline(values)
        trend = get_trend(values)
        output.append(f"- **USD/{ccy}** ({date_str}): {conf['fmt'].format(latest['rate'])}{conf['unit']} {sparkline} {trend}")

    xychart = generate_xychart(rates)
    if xychart:
        output.append("\n**7일 추세 그래프**")
        output.append(xychart)

    output.append("\n**7일 통계**")

    for ccy, conf in CURRENCIES.items():
        ccy_rates = rates.get(ccy) or []
        if len(ccy_rates) >= 7:
            week = [r['rate'] for r in ccy_rates[-7:]]
            output.append(f"- {ccy}: {conf['fmt'].format(min(week))} ~ {conf['fmt'].format(max(week))} (평균 {conf['fmt'].format(sum(week)/len(week))}) {conf['unit']}")

    output.append("━" * 40)

    return "\n".join(output)

def main():
    """메인 실행"""
    rates = load_data()

    if not any(rates.values()):
        print("데이터 없음")
        return

    report = generate_report(rates)
    print("\n" + report)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    report_file = OUTPUT_DIR / f"exchange_rate_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"\n저장됨: {report_file}")

    # PNG 그래프 (matplotlib, 통화별 데이터 2포인트 이상 시)
    png_files = generate_png_charts(rates, OUTPUT_DIR)
    if png_files:
        for path in png_files.values():
            print(f"PNG: {path}")

if __name__ == "__main__":
    main()
