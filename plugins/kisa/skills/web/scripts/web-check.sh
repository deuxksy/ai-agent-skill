#!/bin/sh
# KISA WEB 외부 실측 점검 (읽기 전용) — usage: web-check.sh <도메인>
D="${1:?usage: web-check.sh <도메인>}"
run() { echo "@@CMD@@ $1"; eval "$1" 2>&1; echo "@@END@@"; }

echo "@@META@@ domain=$D date=$(date '+%Y-%m-%d %H:%M:%S %Z')"

echo "@@SEC@@ WEB-04 디렉터리 리스팅 방지 설정"
run "curl -s -o /dev/null -w '%{http_code}\n' https://$D/static/"
run "curl -s -o /dev/null -w '%{http_code}\n' https://$D/assets/"

echo "@@SEC@@ WEB-05 지정하지 않은 CGI/ISAPI 실행 제한"
run "curl -s -o /dev/null -w '%{http_code}\n' https://$D/cgi-bin/test.cgi"

echo "@@SEC@@ WEB-06 상위 디렉터리 접근 제한 (path traversal)"
run "curl -s -o /dev/null -w '%{http_code}\n' --path-as-is https://$D/../../etc/passwd"

echo "@@SEC@@ WEB-07 경로 내 불필요한 파일 (백업·소스 노출)"
run "for f in .git/config .env .bak index.html.bak web.config.bak; do printf '/%s ' \"\$f\"; curl -s -o /dev/null -w '%{http_code}\n' https://$D/\$f; done"

echo "@@SEC@@ WEB-10 불필요한 프록시 설정 (오픈 프록시 여부)"
run "curl -s -o /dev/null -w '%{http_code}\n' 'https://$D/proxy?url=http://example.com'"

echo "@@SEC@@ WEB-13 설정 파일 노출 제한"
run "for f in nginx.conf application.yml web.xml server.xml; do printf '/%s ' \"\$f\"; curl -s -o /dev/null -w '%{http_code}\n' https://$D/\$f; done"

echo "@@SEC@@ WEB-14 경로 내 파일 접근 통제 (관리 경로·Actuator)"
run "for p in admin manager console actuator actuator/env actuator/heapdump actuator/configprops swagger swagger-ui.html druid/index.html; do printf '/%s ' \"\$p\"; curl -s -o /dev/null -w '%{http_code}\n' https://$D/\$p; done"

echo "@@SEC@@ WEB-16 헤더 정보 노출 제한 (Server·X-Powered-By)"
run "curl -sI https://$D/ | grep -iE 'server:|x-powered-by:' || echo '(버전 헤더 없음)'"

echo "@@SEC@@ WEB-18 WebDAV 비활성화 (PROPFIND)"
run "curl -s -o /dev/null -w '%{http_code}\n' -X PROPFIND https://$D/"

echo "@@SEC@@ WEB-20 SSL/TLS 활성화·취약 프로토콜"
run "echo | openssl s_client -connect $D:443 -tls1_3 2>/dev/null | grep -E 'Protocol *:|Cipher *:' | head -2 || echo 'TLS1.3 거부'"
run "echo | openssl s_client -connect $D:443 -tls1_2 2>/dev/null | grep -E 'Protocol *:|Cipher *:' | head -2 || echo 'TLS1.2 거부'"
run "echo | openssl s_client -connect $D:443 -tls1_1 2>/dev/null | grep -E 'Protocol *:|alert|error' | head -2 || echo 'TLS1.1 거부'"
run "echo | openssl s_client -connect $D:443 -tls1 2>/dev/null | grep -E 'Protocol *:|alert|error' | head -2 || echo 'TLS1.0 거부'"
run "echo | openssl s_client -connect $D:443 2>/dev/null | openssl x509 -noout -subject -issuer -dates"

echo "@@SEC@@ WEB-21 HTTP → HTTPS 리디렉션"
run "curl -sI http://$D/ | head -5"

echo "@@SEC@@ WEB-22 에러 페이지 관리 (정보 노출)"
run "curl -s https://$D/kisa-404-probe-nonexistent | head -30"
