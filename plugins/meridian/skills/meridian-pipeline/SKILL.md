---
name: meridian-pipeline
description: SSH/Tailscale 경유 원격 서버에서 Meridian-X 파이프라인(수집, 필터, 라벨, 동기화, 정리, 분류)을 실행. source 수집, 전체 pipeline, 개별 명령어 모두 지원.
---

# Meridian Pipeline (Remote SSH)

## Overview

Tailscale 네트워크 내 원격 서버에 SSH 접속하여 Meridian-X 미디어 파이프라인을 실행.
토렌트 수집(collect)부터 파일 분류(classify)까지 전체 수명주기 관리.

## When to Use

- "meridian pipeline", "pipeline 실행", "수집해줘" 요청 시
- "transmission", "filter", "label", "sync", "tidy", "classify" 개별 명령어 요청 시
- source 지정 수집: "xxxclub 수집", "onejav 수집" 요청 시
- 원격 서버 미디어 관리 작업 전반

## Prerequisites

- 대상 서버가 Tailscale 네트워크에 연결되어 있을 것 (hostname resolving 가능)
- SSH 키 기반 인증 설정 완료
- 대상 서버에 `uv`, Meridian-X 프로젝트 설치됨

## SSH 접속 규칙

### 호스트 결정

- 사용자가 명시적으로 호스트를 지정하면 그 값을 사용
- 미지정 시 기본값: `eve`
- Tailscale hostname만 사용 (IP 금지)

### SSH 옵션

```bash
ssh -o ConnectTimeout=15 <host>
```

- 반드시 `ConnectTimeout` 설정 (타임아웃 시 사용자에게 호스트 오프라인 알림)
- SSH non-interactive shell이므로 PATH 수동 설정 필수

### 원격 명령어 실행 템플릿

모든 원격 명령은 아래 형식 고정:

```bash
ssh <host> 'export PATH="$HOME/.cargo/bin:$PATH" && cd ~/git/Meridian-X && uv run meridian <command> [options]'
```

## Commands

Meridian-X 명령어와 대응하는 사용자 요청 패턴:

| 명령어 | 설명 | 사용자 요청 예시 |
| :--- | :--- | :--- |
| `pipeline` | 전체 파이프라인 (filter→label→sync→tidy→classify) | "pipeline", "전체 실행" |
| `transmission` | 토렌트 수집 (전체 source) | "수집", "collect", "transmission" |
| `transmission --source <src>` | 특정 source 수집 | "xxxclub 수집", "onejav 수집" |
| `filter` | 기존 토렌트 필터링 (광고 제외) | "filter", "필터" |
| `label` | 토렌트에 메이커 코드 라벨 설정 | "label", "라벨" |
| `sync` | Transmission labels → Jellyfin Tags 동기화 | "sync", "동기화" |
| `tidy` | 원격 파일 정리 (정크 삭제→Flatten→파일명 정리) | "tidy", "정리" |
| `classify` | 미디어 파일 분류 | "classify", "분류" |
| `report` | 디스크 사용량 + Transmission 상태 | "report", "리포트", "상태" |
| `transmission --dry-run` | 수집 미리보기 (실제 전송 없음) | "미리보기", "dry-run" |

## Workflow

### 1. 호스트 접속 확인

```bash
ssh -o ConnectTimeout=15 <host> 'echo ok'
```

접속 실패 시 사용자에게 알리고 중단:
- "호스트 `<host>` 에 접속할 수 없습니다. Tailscale 연결 상태를 확인해주세요."

### 2. 명령어 실행

사용자 요청을 명령어로 매핑 후 실행:

```bash
ssh <host> 'export PATH="$HOME/.cargo/bin:$PATH" && cd ~/git/Meridian-X && uv run meridian <command> [options]'
```

### 3. 결과 보고

실행 출력의 핵심 요약을 한국어로 보고:
- Filter: 제외된 토렌트 수
- Label: 라벨링된 수
- Sync: 업데이트된 항목 수
- Tidy: 삭제/Flatten/정리 건수
- Classify: 분류된 파일 수와 대상 폴더
- Collect: 신규 전송 수
- Report: 디스크 사용량, 토렌트 상태

## Common Mistakes

| 실수 | 결과 | 해결 |
| :--- | :--- | :--- |
| SSH에 PATH 설정 누락 | `command not found: uv` | `export PATH="$HOME/.cargo/bin:$PATH"` 필수 |
| ConnectTimeout 미설정 | 무한 대기 | 반드시 `ConnectTimeout=15` 설정 |
| 프로젝트 경로 오타 | `no such file or directory` | `~/git/Meridian-X` 경로 고정 |
| 호스트 미지정 시 eve 사용 누락 | 잘못된 서버에 실행 | 미지정 시 기본값 `eve` 사용 |
