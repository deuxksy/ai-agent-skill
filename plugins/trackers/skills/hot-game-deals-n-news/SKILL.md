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
- **Steam Featured API:** `https://store.steampowered.com/api/featuredcategories?cc=kr` — specials, top_sellers, new_and_trending의 할인 타이틀 한 번에 조회
- 연간 메이저 세일: Spring (3월), Summer (6-7월), Autumn (11월), Winter (12월)
- ⚠️ **가격 데이터 주의:** Steam API `price_overview.initial`/`final`은 원 단위(USD 기준 센트, KRW 기준 원). 하지만 `featuredcategories` API의 `original_price`/`final_price`는 이미 원 단위이므로 **/100 나누기 금지**. 나누면 가격이 100배 작아짐. 
- ⚠️ **appdetails 응답 구조:** `data[str(aid)]["data"]` 안에 `name`이 포함되지만, `price_overview` 필터를 요청하면 `name`이 응답에 없을 수 있음. 이름이 필요하면 필터에서 `price_overview,name`을 함께 지정할 것.

### 2. 위시리스트 할인
- Steam API로 위시리스트 게임 할인 체크
- API 키: `references/api-keys.md` 참조
- ⚠️ **위험:** `dynamicstore/userdata` 엔드포인트는 로그인 없이 빈 위시리스트 반환. 개별 appdetails 체크는 N개 게임에 대해 N회 요청 필요 → 서브에이전트 타임아웃(600s) 위험. 
- **권장 접근:** 위시리스트 체크는 SteamDB 위시리스트 페이지(`https://steamdb.info/calculator/76561198002874693/`)를 브라우저로 확인하거나, `featuredcategories` API의 specials/top_sellers 결과로 대체. 개별 게임 가격 확인이 필요할 때는 반드시 타임아웃 5초로 설정하고 최대 10개까지만 순차 확인.

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

- **리스트 형태** (테이블 X) — **절대 마크다운 테이블(`| col | col |`) 사용 금지.** Discord에서 렌더링 안 됨. 모든 정보는 `- **게임명** — 가격` 형태의 불릿 리스트로 작성.
- 이모지로 카테고리 구분:
  - 🔥 핫 딜
  - 💸 세일
  - 🎁 무료
  - 📰 뉴스
- Epic/GOG 무료 게임 결과에도 테이블 대신 불릿 리스트 사용. 서브에이전트에도 이 규칙을 context로 전달할 것.

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

## ⚠️ Pitfalls (실전에서 발견)

1. **Steam appdetails 순차 조회 타임아웃:** 위시리스트 N개 게임을 하나씩 `appdetails` API로 확인하면 N×(응답시간)으로 서브에이전트 600s 제한 초과. 반드시 `featuredcategories` API로 한 번에 조회하거나 최대 10개 제한.
2. **`dynamicstore/userdata` 위시리스트 빈 응답:** 로그인 세션 없이 호출하면 `rgWishlist: []` 반환. Steam은 공개 위시리스트 API를 제공하지 않음.
3. **가격 단위 혼동:** `featuredcategories` API의 price 필드도 KRW(cc=kr)에서는 원×100 단위로 옴 (예: Cyberpunk 6600000 = ₩66,000). 표시할 때 **/100 필요**. appdetails의 `price_overview`도 센트/원×100. (2026-08-08 실측 확인 — 기존 "나누기 금지" 주석은 USD 기준 오류였음)
4. **서브에이전트에 테이블 지시 누락:** 서브에이전트가 Epic/GOG 무료 게임을 마크다운 테이블로 반환하는 경우 있음. context에 "테이블 금지, 불릿 리스트만"을 반드시 포함할 것.
5. **Steam specials 페이지 브라우저 로딩:** JS 렌더링 지연으로 DOM에 `tab_item` 요소가 바로 안 나타남. 스크롤 후 재검사 필요하지만 API 호출이 더 안정적.
6. **`references/my-steam-games.json` 재생성 (2026-08-24):** 파일이 한동안 부재했으나(2026-08-08 확인), 2026-08-24에 Steam API(`IPlayerService/GetOwnedGames`)로 재생성함. 재생성 스크립트: `/opt/data/tmp/fetch_steam_games.py` (sops에서 STEAM_API_KEY/STEAM_USER_ID 로드). 1,077개 게임 보유. 파일이 다시 없어지면 이 스크립트로 재생성할 것.
7. **인벤 RSS URL 변경:** `https://www.inven.co.kr/webzine/news/?iskin=rss`는 RSS가 아닌 HTML 반환. 국내 뉴스는 HTML 파싱하거나 해외 RSS(PC Gamer, RPS 정상 동작)로 대체.
8. **GOG partner/free_games는 상시 무료 목록:** 해당 페이지(2026-08-24 확인)는 한정 기브어웨이가 아닌 상시 무료 게임 48종 목록임(내장 `gogData.products` JSON에서 파싱 가능). 기간 한정 무료는 홈 페이지 배너에서 확인 필요.
9. **Epic freeGamesPromotions API 유효:** `https://store-site-backend-static-ipv4.ak.epicgames.com/freeGamesPromotions?locale=ko&country=KR&allowCountries=KR` — 현재/예정 무료 게임 날짜+할인율 정상 반환. 브라우저 접근은 Cloudflare 차단됨.
