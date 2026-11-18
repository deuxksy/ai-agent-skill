#!/usr/bin/env python3
"""
환율 수집 스크립트
USD 기준 6개 통화(KRW, VND, JPY, CNY, EUR, GBP) 환율을 조회해서 JSON 파일로 저장
"""

import json
import requests
from datetime import datetime
from pathlib import Path

# 데이터 파일 경로
DATA_FILE = Path(__file__).parent.parent / "references" / "exchange-rates.json"

# 통화별 표시 포맷 (USD 기준: 1 USD = N 통화)
CURRENCIES = {
    "KRW": "{:,.2f}원",
    "VND": "{:,.0f}동",
    "JPY": "{:,.2f}엔",
    "CNY": "{:,.2f}위안",
    "EUR": "{:,.2f}유로",
    "GBP": "{:,.2f}파운드",
}

def fetch_rates():
    """무료 환율 API 사용 - CURRENCIES 전체 수집"""
    try:
        url = "https://api.exchangerate-api.com/v4/latest/USD"
        response = requests.get(url, timeout=10)
        data = response.json()
        return {ccy: data['rates'].get(ccy) for ccy in CURRENCIES}
    except Exception as e:
        print(f"Error fetching rates: {e}")
        return {}

def load_data():
    """기존 데이터 로드"""
    if DATA_FILE.exists():
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        return {f"{c.lower()}_rates": [] for c in CURRENCIES}

def save_rates(rates):
    """환율 데이터 저장 (통화별 키: krw_rates, vnd_rates, jpy_rates)"""
    data = load_data()
    now = datetime.now()

    for ccy, rate in rates.items():
        if not rate:
            continue
        entry = {
            "date": now.strftime("%Y-%m-%d"),
            "time": now.strftime("%H:%M"),
            "rate": round(rate, 2),
            "timestamp": int(now.timestamp())
        }
        data.setdefault(f"{ccy.lower()}_rates", []).append(entry)
        print(f"{ccy}: {entry}")

    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return rates

def main():
    """메인 실행"""
    print(f"Fetching exchange rates at {datetime.now()}")

    print("Using ExchangeRate API...")
    rates = fetch_rates()

    if any(rates.values()):
        save_rates(rates)
        for ccy, rate in rates.items():
            if rate:
                print(f"USD/{ccy}: {CURRENCIES[ccy].format(rate)}")
        return rates
    else:
        print("Failed to fetch exchange rates")
        return None

if __name__ == "__main__":
    main()
