---
name: hot-game-deals-n-news
description: 게임 세일, 무료 게임, 뉴스를 체크해서 보고하는 스킬. Use when (1) 데일리 게임 알림 cron job 실행, (2) 사용자가 게임 세일/할인/무료 게임 요청, (3) 게임 뉴스 요약 요청, (4) 위시리스트 할인 체크 요청. 항상 한국어로 응답.
---

# Hot Game Deals & News

게임 세일, 무료 게임, 뉴스를 체크해서 리스트 형태로 보고하는 스킬.

## 체크 항목

### 1. Steam 세일
- **SteamDB:** https://steamdb.info/upcoming/ - 예정된 세일
- **IsThereAnyDeal:** https://isthereanydeal.com/ - 가격 히스토리
- 연간 메이저 세일: Spring (3월), Summer (6-7월), Autumn (11월), Winter (12월)

### 2. 위시리스트 할인
- Steam API로 위시리스트 게임 할인 체크
- API 키: `references/api-keys.md` 참조

### 3. 무료 게임
- **Epic Games:** https://store.epicgames.com/free-games
- **GOG:** https://www.gog.com/partner/free_games
- **Steam:** 무료 주말/프로모션
- **itch.io:** https://itch.io/games/free

### 4. 한국 판매처
- **다이렉트게임즈 (DirectG):** https://directg.net/
- 한국어 번역 게임 할인 정보

### 5. 게임 뉴스
**해외 (번역):**
- Kotaku, IGN, PC Gamer, Eurogamer, Rock Paper Shotgun

**국내 (요약):**
- 인벤, 디스이즈게임

## 출력 형식

- **리스트 형태** (테이블 X)
- 이모지로 카테고리 구분:
  - 핫 딜
  - 세일
  - 무료
  - 뉴스

## 스케줄

- **매일 오전 9시 (GMT+7)** cron job으로 자동 실행
- cron 설정: `0 2 * * *` (UTC 02:00 = GMT+7 09:00)

## 전송 채널

- **Slack:** #hot-game-deals-news (https://zzizily.slack.com/archives/C0AKUCX02KS)

## 필터링 규칙

- **보유 게임 제외:** `references/my-steam-games.json`에 있는 게임은 할인 알림에서 제외
- 이미 소유한 게임은 알림 불필요

## 사용자 취향 (참고용)

- **좋아:** 전략/전술 (XCOM, 커맨도스), 전술 RPG (FFT, Tactics Ogre), 벨트스크롤 액션, 2D 스텔스
- **별로:** 순수 JRPG, 로그라이크, Dead Cells 스타일
- **한국어 지원 필수** (공식/비공식 모두 OK)

## Resources

### references/
- `api-keys.md` - Steam, IsThereAnyDeal API 키
- `sources.md` - 상세 소스 URL 목록
