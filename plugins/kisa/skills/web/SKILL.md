---
name: web
description: "웹 서비스 보안 취약점 점검 (KISA WEB-01~WEB-26). 외부 실측(curl·openssl) + 서버측 설정 확인(ingress-nginx·Spring Boot Undertow)으로 양호/취약 판정과 증빙 리포트 생성. `/kisa:web <domain>`."
---

# Web Service Security Audit (KISA WEB-01~WEB-26)

대상 웹 서비스에 읽기 전용 명령만 실행해 KISA 주요정보통신기반시설 취약점 점검 체계(WEB-01~WEB-26)로 판정한다.

## 핵심 프로세스

```text
도메인 확인 → 외부 점검 스크립트 실행 (읽기 전용) → 서버측 보완 점검 (kubectl·설정) → 항목별 판정 → 증빙 리포트 md 생성
```

## 사용법

```bash
/kisa:web www.example.com           # 단일 도메인 (https 기본)
/kisa:web api.example.com manager.example.com   # 다중 도메인 순차
```

## 절차

### 1. 대상 확인

- `<domain>`은 접속 가능한 서비스 도메인. `curl -sI https://<domain>/`로 응답 확인
- 웹서버 계층 파악: 응답 헤더·인증 구조로 nginx/Tomcat/Undertow 등 계층 식별 (KISA 가이드는 Apache·IIS·nginx·Tomcat·WebtoB 수록 — Undertow는 Tomcat 항목의 유사 적용, 설정은 Spring property로 대체 점검)

### 2. 외부 점검 실행 (전부 읽기 전용)

```bash
sh scripts/web-check.sh <domain> > /tmp/web-check-<domain>-raw.txt
```

- 커버 항목: WEB-04~07·10·13·14·16·18·20~22 (경로 탐색·헤더·TLS·리디렉션·에러 페이지)
- 스크립트는 `@@SEC@@`(항목) / `@@CMD@@`(명령) / `@@END@@` 마커로 명령·결과 원문을 남긴다
- 사용 명령: `curl`(GET·HEAD·PROPFIND)·`openssl s_client` — 서버 상태 변경 없음

### 3. 서버측 보완 점검 (K8s 환경)

외부 점검 불가 항목은 인프라 접근 수단에 따라 보완한다:

| 항목 | kubectl 명령 (읽기 전용) |
| :--- | :--- |
| WEB-08 업로드 용량 | `kubectl -n ingress-nginx get cm ingress-nginx-controller -o yaml \| grep -i body-size` |
| WEB-09 프로세스 권한 | `kubectl get deploy <웹서버-deploy> -o jsonpath='{.spec.template.spec.containers[0].securityContext}'` |
| WEB-11·17 경로·가상디렉토리 | `kubectl get ingress -A` |
| WEB-25 패치 | `kubectl get deploy -o custom-columns='NAME:.metadata.name,IMAGE:.spec.template.spec.containers[*].image'` |
| WEB-26 로그 | `kubectl logs deploy/<웹서버-deploy> --tail=5` |
| WEB-01~03·23 계정·인증 | 관리 콘솔(Keycloak 등) 확인 — 판정 보류 가능 |

- K8s가 아닌 베어메탈: 서버 접속 후 웹서버 설정 파일(nginx.conf·server.xml·application.yml)을 `cat`·`grep`으로 확인

### 4. 판정

각 WEB 항목의 양호/취약 조건은 [references/verdict-criteria.md](references/verdict-criteria.md) 참조. 요약:

| 그룹 | 항목 | 대표 양호 조건 |
| :--- | :--- | :--- |
| 계정 (WEB-01~03) | 관리자 계정·비밀번호 정책 | 기본 계정명 미사용, 비밀번호 정책 설정 |
| 서비스 (WEB-04~19) | 리스팅·CGI·traversal·불필요 파일·헤더·DAV·SSI | 탐색 경로 전부 404/403, 버전 헤더 미노출 |
| 보안 설정 (WEB-20~24) | SSL/TLS·리디렉션·에러 페이지·업로드 | TLS 1.2+만 허용, HTTP→HTTPS 리디렉션, 스택트레이스 미노출 |
| 패치·로그 (WEB-25~26) | 웹서버 버전·로그 | 최신 안정판, 접속 로그 기록 |

**판정 원칙**: linux 스킬과 동일 — 양호 조건을 문자 그대로 충족할 때만 양호, 확인 불가·부재는 취약(보수적). 대상 기능이 존재하지 않으면 해당없음 (근거 기록). 확인 수단이 없는 관리 콘솔 항목은 **미점검**으로 판정 보류 가능.

### 5. 증빙 리포트

출력 경로: **`./report/web-<domain>-<YYMMDDhhmm>.md`** (`report/` 없으면 생성)

형식은 linux 스킬과 동일한 구조(메타 헤더 → KISA 그룹 → 항목별 판정·명령·결과)에 웹 계층 메타를 추가한다.

메타 헤더 — 대상 계층·기준 명시:

```markdown
# <domain> 웹 서비스 정보보안점검 증빙
- 대상 (계층): ① ingress-nginx — K8s 인그레스 (KISA nginx 항목 직접 적용)
              ② Spring Boot embedded Undertow — Tomcat 항목의 유사 적용 (Spring property 대체 점검)
- 기준: KISA 2026 상세가이드 III. 웹 서비스 + 기후에너지환경부 보안성검토매뉴얼 Ⅱ-1
- 실행: <YYYY-MM-DD KST>, 읽기 전용 명령 (curl·openssl s_client·kubectl get)
- 요약: **양호 N · 취약 M · 해당없음 K** (미점검 항목 병기)
```

매뉴얼 Ⅱ-1 ↔ WEB 코드 매핑 (자체보안대책·확인서 회신 시 사용):

| 매뉴얼 Ⅱ-1 대항목 | KISA 대응 |
| :--- | :--- |
| 시큐어 코딩 및 보안취약점 제거 대책 | WEB-04~19·22·24·25·26 (웹서버 설정 계열) + 정적분석(행안부) |
| 로그인 SSL 암호화 및 관리자페이지 통제 | WEB-01~03 (계정) + WEB-20·21 (SSL) + WEB-23 (인증) + 접근통제 실측 |

항목 포맷 — `관점:` 라인으로 확인 대상을 먼저 밝힌다:

```markdown
### WEB-14 경로 내 파일의 접근 통제 — 판정: **양호**
관점: 관리·민감 경로 비인가 접근 차단 (401/403/404)
명령:
```bash
<실측 명령>
```
결과:
```text
<명령 출력 원문>
```
```

## 안전 규칙

- **읽기 전용만 실행** — GET·HEAD 요청과 설정 조회 외 서버 조작 금지. 공격 시나리오(PROPFIND·traversal)는 탐지 목적 1회 요청으로 한정
- 판정은 실측 사실 기반 — 추측으로 양호 판정 금지
- 증빙에는 자격증명·세션 쿠키가 남지 않는지 확인 후 산출물 저장
- 조치(remediation)는 별도 작업 — 이 스킬은 진단만

## 참고

- 점검 항목 체계: KISA 주요정보통신기반시설 취약점 점검 가이드 2026 "III. 웹 서비스" (WEB-01~26)
- KISA 가이드 미수록 컨테이너(Undertow)는 Tomcat 항목 관점 유지 + Spring property(`server.undertow.*`·`server.*`)로 점검 방법 변환
- SQLi·XSS 등 애플리케이션 취약점·시큐어코딩은 본 스킬 범위 외 (행정안전부 소프트웨어 개발 보안 가이드)
- 판정 기준 상세: [references/verdict-criteria.md](references/verdict-criteria.md)
- 관련 스킬: `linux`(U-01~73), `security:code-audit`(애플리케이션 코드)
