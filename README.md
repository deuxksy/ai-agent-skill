# AI Agent Skill

개인 자동화 AI Agent Skill 플러그인.

## Skill 목록

| Skill | 설명 |
| :--- | :--- |
| `deploy-android-wifi` | WiFi ADB로 Android 기기에 React Native 앱 빌드/배포 자동화 |
| `security-audit` | 크로스 플랫폼 보안 취약점 및 업데이트 점검 (brew, npm, pip, mise 등) |
| `korean-translation-verify` | Gemma API로 한국어 기술 문서 번역 품질 검증 |
| `openwrt-initd` | OpenWrt init.d 백그라운드 서비스 설치 (procd 감시) |
| `hot-game-deals-n-news` | Steam/Epic/GOG 게임 할인, 무료 게임, 뉴스 체크 |
| `exchange-rate-tracker` | USD/KRW, USD/VND 환율 수집 및 그래프 시각화 |
| `proxmox-vm-create` | pvesh(REST API)로 Proxmox template 복제 VM 생성 자동화 (사양 확장 + product_uuid 방어) |

## 설치

```
claude plugin marketplace add deuxksy/ai-agent-skill
claude plugin install deuxksy@zzizily
```

## 사용

```
/zzizily:<skill-name>
```
