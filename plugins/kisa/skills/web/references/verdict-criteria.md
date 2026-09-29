# WEB-01~WEB-26 판정 기준

KISA 주요정보통신기반시설 기술적 취약점 분석·평가 방법 상세가이드 2026 "III. 웹 서비스" 기준.
환경별 적용: nginx(ingress-nginx 포함)는 nginx 항목 직접 적용, **Undertow는 Tomcat 항목의 유사 적용** (설정 위치는 Spring property `server.undertow.*`·`server.*`·`spring.servlet.multipart.*`로 대체). KISA 가이드는 Apache·IIS·nginx·Tomcat·WebtoB만 수록.

## 판정 원칙

- 양호 조건을 실측 결과가 문자 그대로 충족할 때만 양호
- 확인 불가·설정 부재는 취약 (보수적 판정)
- 대상 기능 자체가 없으면 해당없음 — 근거(탐색 결과·아키텍처) 기록
- 외부 실측(스크립트) + 서버측 확인(kubectl·설정 파일) 조합으로 판정. 한쪽만으로 충분하면 병행 불필요

## 1. 계정 관리

| 코드 | 항목 | 양호 조건 | 취약 예 |
| :--- | :--- | :--- | :--- |
| WEB-01 | Default 관리자 계정명 변경 | 기본 관리자 계정(admin·administrator·manager) 미사용, 식별 어려운 개별 계정 사용 | 기본 admin 계정 그대로 사용 |
| WEB-02 | 취약한 비밀번호 사용 제한 | 비밀번호 정책(길이 8+·복잡도·만료) 설정 (Keycloak realm policy, DB 연동 시 DB 정책) | 정책 미설정, 기본값 사용 |
| WEB-03 | 비밀번호 파일 권한 관리 | htpasswd 등 비밀번호 파일 소유자 root·권한 600 이하 | 일반 사용자 읽기 가능, 웹 경로 노출 |

## 2. 서비스 관리

| 코드 | 항목 | 양호 조건 | 취약 예 |
| :--- | :--- | :--- | :--- |
| WEB-04 | 디렉터리 리스팅 방지 | 디렉터리 URL 접근 시 403/404 (목록 미노출) | 200 + 파일 목록 응답 |
| WEB-05 | CGI/ISAPI 실행 제한 | 지정 외 CGI 경로 실행 안 함 (404) | cgi-bin 스크립트 실행 |
| WEB-06 | 상위 디렉터리 접근 제한 | `../` traversal 시도 차단 (400/403/404) | 시스템 파일 내용 응답 |
| WEB-07 | 경로 내 불필요한 파일 제거 | 백업(`.bak`)·`.git`·`.env`·소스 파일 전부 404 | 백업·소스 파일 200 응답 |
| WEB-08 | 업로드·다운로드 용량 제한 | 업로드 용량 제한 설정 (nginx: `client_max_body_size`, Spring: `spring.servlet.multipart.max-file-size`) | 무제한(기본 무제한·1m 아닌 명시적 무제한) |
| WEB-09 | 프로세스 권한 제한 | 웹서버 프로세스 비루트 실행 (컨테이너: securityContext runAsNonRoot) | root 실행 |
| WEB-10 | 불필요한 프록시 설정 제한 | 임의 URL 프록시 거부 — 지정 backend만 전달 | 오픈 프록시 동작 |
| WEB-11 | 경로 설정 | DocumentRoot·서비스 경로가 의도된 최소 범위 | 웹 루트가 시스템 경로 포함 |
| WEB-12 | 링크 사용 금지 | 심볼릭 링크 추적 비활성 (nginx 기본 off) | FollowSymLinks 활성으로 웹루트 밖 접근 |
| WEB-13 | 설정 파일 노출 제한 | 웹 경로로 설정 파일 접근 404 | nginx.conf·application.yml 200 응답 |
| WEB-14 | 경로 내 파일 접근 통제 | 관리·민감 경로 비인가 접근 차단 (401/403/404) | actuator/env·admin 페이지 익명 200 |
| WEB-15 | 불필요한 스크립트 매핑 제거 | 사용하지 않는 핸들러·서블릿 매핑 없음 | 불필요 매핑 잔존 |
| WEB-16 | 헤더 정보 노출 제한 | `Server`·`X-Powered-By`에 버전 정보 없음 | `Server: nginx/1.25.3` 등 버전 노출 |
| WEB-17 | 가상 디렉토리 삭제 | 불필요한 alias·가상 경로 없음 | 운영 미사용 경로 매핑 잔존 |
| WEB-18 | WebDAV 비활성화 | PROPFIND 등 DAV 메서드 거부 (405) | DAV 메서드 허용 |
| WEB-19 | SSI 사용 제한 | SSI 옵션 비활성 | SSI 실행 허용 |

## 3. 보안 설정

| 코드 | 항목 | 양호 조건 | 취약 예 |
| :--- | :--- | :--- | :--- |
| WEB-20 | SSL/TLS 활성화 | 전 구간 HTTPS, TLS 1.2+만 허용 (1.0/1.1 거부), 유효 인증서 | TLS 1.0/1.1 협상 성공, 만료 인증서 |
| WEB-21 | HTTP 리디렉션 | HTTP 요청 301/308 → HTTPS | HTTP 그대로 200 응답 |
| WEB-22 | 에러 페이지 관리 | 에러 페이지에 서버 정보·스택트레이스 미노출 | 예외 스택·버전·경로 노출 |
| WEB-23 | LDAP 알고리즘 적절한 구성 | LDAP 사용 시 안전 구성 (서명·채널 바인딩·비익명 바인드) / 미사용 시 해당없음 | 익명 바인드 허용 |
| WEB-24 | 별도 업로드 경로·권한 | 업로드 경로 분리·실행 권한 제한 (웹루트 밖, 실행 제외) | 웹루트 내 업로드 + 실행 허용 |

## 4. 패치 및 로그 관리

| 코드 | 항목 | 양호 조건 | 취약 예 |
| :--- | :--- | :--- | :--- |
| WEB-25 | 주기적 보안 패치 | 웹서버·런타임 버전이 최신 안정판 (이미지 스캔 결과 증빙 가능) | 알려진 CVE 미패치 버전 |
| WEB-26 | 로그 디렉터리·파일 권한 | 접속·오류 로그 기록, 로그 접근 통제 (컨테이너: 표준출력→수집 구조로 대체 판정) | 로그 미기록, 일반 사용자 열람 가능 |

## 환경별 설정 위치 대응

| 점검 대상 | nginx | Tomcat | Undertow (Spring Boot) |
| :--- | :--- | :--- | :--- |
| 헤더 숨김 (WEB-16) | `server_tokens off` | Connector `server=" "` | `server.server-header` (미설정 시 기본값 확인) |
| 업로드 용량 (WEB-08) | `client_max_body_size` | Connector `maxPostSize` | `spring.servlet.multipart.max-file-size` |
| 에러 페이지 (WEB-22) | `error_page` 지시자 | web.xml `<error-page>` | `server.error.include-stacktrace=never` 등 |
| 디렉터리 리스팅 (WEB-04) | `autoindex off` | web.xml DefaultServlet `listings=false` | 기본 미제공 (Welcome file 없으면 403/404) |
| 관리 계정 (WEB-01) | htpasswd | tomcat-users.xml | 앱 계정 체계 (Keycloak 연동 등) |
