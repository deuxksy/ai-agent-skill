---
name: exchange-rate-tracker
description: 달러-원화(KRW) 및 달러-베트남동화(VND) 환율을 추적하고 그래프로 시각화하는 스킬. Use when (1) 환율 조회 요청, (2) 환율 그래프 생성, (3) 환율 변동 알림, (4) cron job으로 정기 환율 수집. 항상 한국어로 응답.
---

# Exchange Rate Tracker

USD/KRW, USD/VND 환율을 추적하고 그래프로 시각화하는 스킬.

## 기능

### 1. 환율 수집
- **ExchangeRate API**를 통해 실시간 환율 조회
- **USD/KRW** (달러/원화)
- **USD/VND** (달러/베트남 동화)
- 하루 4번 자동 수집 (09:00, 12:00, 15:00, 18:00 GMT+7)
- 데이터를 JSON 파일로 저장

### 2. 그래프 생성
- Mermaid xychart 환율 변동 그래프
- 주간/월간 추이 그래프
- 스파크라인 (유니코드 블록)
- matplotlib PNG 일별/추세 그래프 (KRW/VND, 추세선 포함)

### 3. 알림
- 큰 변동 시 알림 (예: ±50원 이상)
- Slack/Telegram으로 전송

## 데이터 저장

`references/exchange-rates.json`에 저장:
```json
{
  "krw_rates": [
    {
      "date": "2026-03-06",
      "time": "09:00",
      "rate": 1485.50,
      "timestamp": 1772806800
    }
  ],
  "vnd_rates": [
    {
      "date": "2026-03-06",
      "time": "09:00",
      "rate": 25430,
      "timestamp": 1772806800
    }
  ]
}
```

## 스케줄

- **09:00 GMT+7** (UTC 02:00)
- **12:00 GMT+7** (UTC 05:00)
- **15:00 GMT+7** (UTC 08:00)
- **18:00 GMT+7** (UTC 11:00)

## Resources

### scripts/
- `fetch_rate.py` - 환율 수집 스크립트
- `plot_graph.py` - 그래프 생성 스크립트 (Mermaid xychart + matplotlib PNG)

### references/
- `api-info.md` - 하나은행 API 정보
