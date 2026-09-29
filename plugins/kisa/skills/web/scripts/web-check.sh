#!/bin/sh
# KISA WEB 외부 실측 점검 (읽기 전용) — usage: web-check.sh <도메인>
# 도메인은 hostname 문자(A-Za-z0-9.-)만 허용 — 명령 삽입 방지. eval 미사용.
D="${1:?usage: web-check.sh <도메인>}"
case "$D" in
  *[!A-Za-z0-9.-]*|'') echo "ERROR: 도메인에 허용되지 않은 문자가 포함됨: $D" >&2; exit 2 ;;
esac

CURL="curl -sS --connect-timeout 5 --max-time 10"

sec() { echo; echo "@@SEC@@ $1"; }

echo "@@META@@ domain=$D date=$(date '+%Y-%m-%d %H:%M:%S %Z')"

sec "WEB-04 디렉터리 리스팅 방지 설정"
echo "@@CMD@@ curl https://\$D/static/ https://\$D/assets/ (http_code)"
for p in static assets; do
  printf '/%s ' "$p"; $CURL -o /dev/null -w '%{http_code}\n' "https://$D/$p/"
done
echo "@@END@@"

sec "WEB-05 지정하지 않은 CGI/ISAPI 실행 제한"
echo "@@CMD@@ curl https://\$D/cgi-bin/test.cgi (http_code)"
$CURL -o /dev/null -w '%{http_code}\n' "https://$D/cgi-bin/test.cgi"
echo "@@END@@"

sec "WEB-06 상위 디렉터리 접근 제한 (path traversal)"
echo "@@CMD@@ curl --path-as-is https://\$D/../../etc/passwd (http_code)"
$CURL -o /dev/null -w '%{http_code}\n' --path-as-is "https://$D/../../etc/passwd"
echo "@@END@@"

sec "WEB-07 경로 내 불필요한 파일 (백업·소스 노출)"
echo "@@CMD@@ for f in .git/config .env .bak index.html.bak web.config.bak; do curl https://\$D/\$f; done"
for f in .git/config .env .bak index.html.bak web.config.bak; do
  printf '/%s ' "$f"; $CURL -o /dev/null -w '%{http_code}\n' "https://$D/$f"
done
echo "@@END@@"

sec "WEB-10 불필요한 프록시 설정 (오픈 프록시 여부)"
echo "@@CMD@@ curl 'https://\$D/proxy?url=http://example.com' (http_code)"
$CURL -o /dev/null -w '%{http_code}\n' "https://$D/proxy?url=http://example.com"
echo "@@END@@"

sec "WEB-13 설정 파일 노출 제한"
echo "@@CMD@@ for f in nginx.conf application.yml web.xml server.xml; do curl https://\$D/\$f; done"
for f in nginx.conf application.yml web.xml server.xml; do
  printf '/%s ' "$f"; $CURL -o /dev/null -w '%{http_code}\n' "https://$D/$f"
done
echo "@@END@@"

sec "WEB-14 경로 내 파일 접근 통제 (관리 경로·Actuator)"
echo "@@CMD@@ for p in admin manager console actuator actuator/env actuator/heapdump actuator/configprops swagger swagger-ui.html druid/index.html; do curl https://\$D/\$p; done"
for p in admin manager console actuator actuator/env actuator/heapdump actuator/configprops swagger swagger-ui.html druid/index.html; do
  printf '/%s ' "$p"; $CURL -o /dev/null -w '%{http_code}\n' "https://$D/$p"
done
echo "@@END@@"

sec "WEB-16 헤더 정보 노출 제한 (Server·X-Powered-By)"
echo "@@CMD@@ curl -I https://\$D/ | grep -iE 'server:|x-powered-by:'"
$CURL -I "https://$D/" 2>&1 | grep -iE 'server:|x-powered-by:' || echo '(버전 헤더 없음)'
echo "@@END@@"

sec "WEB-18 WebDAV 비활성화 (PROPFIND)"
echo "@@CMD@@ curl -X PROPFIND https://\$D/ (http_code)"
$CURL -o /dev/null -w '%{http_code}\n' -X PROPFIND "https://$D/"
echo "@@END@@"

# TLS 1.0/1.1: OpenSSL 3+ 클라이언트가 -tls1_1/-tls1 미지원이면
# "no protocols available"이 증거에 남는다 — 이는 클라이언트 제약이며 서버 판정 불가.
sec "WEB-20 SSL/TLS 활성화·취약 프로토콜"
for v in tls1_3 tls1_2 tls1_1 tls1; do
  echo "@@CMD@@ echo | openssl s_client -connect \$D:443 -$v 2>&1 | grep -E 'Protocol|Cipher|alert|error|no protocols' | head -2"
  echo | openssl s_client -connect "$D:443" "-$v" 2>&1 | grep -E 'Protocol *:|Cipher *:|alert|error|no protocols' | head -2
  echo "@@END@@"
done
echo "@@CMD@@ echo | openssl s_client -connect \$D:443 2>/dev/null | openssl x509 -noout -subject -issuer -dates"
echo | openssl s_client -connect "$D:443" 2>/dev/null | openssl x509 -noout -subject -issuer -dates
echo "@@END@@"

sec "WEB-21 HTTP → HTTPS 리디렉션"
echo "@@CMD@@ curl -I http://\$D/ | head -5"
$CURL -I "http://$D/" 2>&1 | head -5
echo "@@END@@"

sec "WEB-22 에러 페이지 관리 (정보 노출)"
echo "@@CMD@@ curl https://\$D/kisa-404-probe-nonexistent | head -30"
$CURL "https://$D/kisa-404-probe-nonexistent" 2>&1 | head -30
echo "@@END@@"
