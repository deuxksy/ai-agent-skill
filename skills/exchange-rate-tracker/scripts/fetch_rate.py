#!/usr/bin/env python3
"""
환율 수집 스크립트
USD/KRW, USD/VND 환율을 조회해서 JSON 파일로 저장
"""

import json
import requests
from datetime import datetime
from pathlib import Path
import time

# 데이터 파일 경로
DATA_FILE = Path(__file__).parent.parent / "references" / "exchange-rates.json"

def fetch_fallback_rates():
    """백업: 무료 환율 API 사용 - KRW, VND 모두 수집"""
    try:
        url = "https://api.exchangerate-api.com/v4/latest/USD"
        response = requests.get(url, timeout=10)
        data = response.json()
        krw_rate = data['rates'].get('KRW')
        vnd_rate = data['rates'].get('VND')
        return krw_rate, vnd_rate
    except Exception as e:
        print(f"Error fetching fallback rates: {e}")
        return None, None

def load_data():
    """기존 데이터 로드"""
    if DATA_FILE.exists():
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        return {"krw_rates": [], "vnd_rates": []}

def save_rates(krw_rate, vnd_rate):
    """환율 데이터 저장 (KRW, VND)"""
    data = load_data()
    now = datetime.now()

    if krw_rate:
        krw_entry = {
            "date": now.strftime("%Y-%m-%d"),
            "time": now.strftime("%H:%M"),
            "rate": round(krw_rate, 2),
            "timestamp": int(now.timestamp())
        }
        data["krw_rates"].append(krw_entry)
        print(f"KRW: {krw_entry}")

    if vnd_rate:
        vnd_entry = {
            "date": now.strftime("%Y-%m-%d"),
            "time": now.strftime("%H:%M"),
            "rate": round(vnd_rate, 2),
            "timestamp": int(now.timestamp())
        }
        data["vnd_rates"].append(vnd_entry)
        print(f"VND: {vnd_entry}")

    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return {"krw": krw_rate, "vnd": vnd_rate}

def main():
    """메인 실행"""
    print(f"Fetching exchange rates at {datetime.now()}")

    print("Using ExchangeRate API...")
    krw_rate, vnd_rate = fetch_fallback_rates()

    if krw_rate and vnd_rate:
        entry = save_rates(krw_rate, vnd_rate)
        print(f"USD/KRW: {krw_rate:,.2f}원")
        print(f"USD/VND: {vnd_rate:,.0f}동")
        return entry
    else:
        print("Failed to fetch exchange rates")
        return None

if __name__ == "__main__":
    main()
