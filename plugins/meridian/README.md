# meridian Plugin

SSH/Tailscale 경유 원격 Meridian-X 미디어 수집 및 파이프라인 관리 스킬을 제공하는 미디어 도메인 플러그인입니다.

## 포함 스킬 (1)

- **`meridian-pipeline`**: 원격 서버 Meridian-X 파이프라인 실행 (수집, 필터, 라벨, 동기화, 정리, 분류, 리포트)

## 설치 방법

```bash
claude plugin install meridian@zzizily
```

## 사용법

```
meridian pipeline          # 전체 파이프라인 실행 (기본 호스트: eve)
meridian xxxclub 수집       # xxxclub source 수집
meridian report             # 상태 리포트
meridian pipeline --host mo # mo 서버에서 실행
```
