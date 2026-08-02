# 환율 API 정보

## 지원 통화

- **USD/KRW** (달러/원화)
- **USD/VND** (달러/베트남 동화)

## 백업 API

### ExchangeRate-API (무료)
- **URL:** https://www.exchangerate-api.com/
- **제한:** 하루 1,500회
- **데이터:** USD/KRW, USD/VND 포함
- **API:** `https://api.exchangerate-api.com/v4/latest/USD`

## 데이터 저장

- **파일:** `references/exchange-rates.json`
- **형식:**
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

## 출력

- **그래프:** `output/exchange_rate_YYYYMMDD.txt`
- **형식:** GitHub Markdown 호환
