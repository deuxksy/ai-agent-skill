---
name: deploy-android-wifi
description: Use when deploying a React Native app to an Android device connected via WiFi ADB. Handles Metro server, gradle build, install, and adb reverse port forwarding automatically.
---

# Deploy Android WiFi

## Overview

WiFi ADB로 연결된 Android 기기에 React Native 앱을 빌드/배포하는 자동화 Skill.
Metro 서버 실행 → Gradle 빌드 → 기기 설치 → 포트 포워딩까지 한 번에 처리.

## When to Use

- "배포해줘", "디플로이", "deploy" 요청 시
- WiFi ADB로 기기가 이미 연결된 상태에서 배포 필요 시
- 코드 수정 후 기기에 반영 필요 시

## Prerequisites

- 사용자가 `adb connect <IP>:<PORT>` 완료한 상태
- Android 프로젝트에 `android/` 디렉토리 존재
- Node.js, JDK, Android SDK 설치됨

## Workflow

```
1. adb devices 로 기기 연결 확인
2. Metro 서버 실행 (백그라운드, 없으면)
3. gradle installDebug 빌드 & 설치
4. adb reverse tcp:8081 tcp:8081 포트 포워딩
5. 결과 보고
```

## Implementation

### 1. 기기 연결 확인

```bash
adb devices
```

- 대상 기기가 없으면 사용자에게 `adb connect` 요청
- 기본 대상: `10.101.101.120:34593` (SM-F731N)

### 2. Metro 서버 시작 (백그라운드)

```bash
# Metro가 이미 실행 중인지 확인
curl -s http://localhost:8081/status > /dev/null 2>&1

# 실행 중이 아니면 백그라운드로 시작
npx react-native start
# → run_in_background 로 실행
```

### 3. Gradle 빌드 & 설치

```bash
# android/ 디렉토리에서 직접 실행 (경로 인식 문제 회피)
cd <project-root>/android && ./gradlew app:installDebug -x lint -PreactNativeDevServerPort=8081
```

**주의:** `npx react-native run-android` 대신 직접 gradle 실행.
`run-android`는 Windows 환경에서 `gradlew.bat` 경로 인식 실패 이슈 있음.

### 4. adb reverse 포트 포워딩 (필수)

```bash
adb -s <device-id> reverse tcp:8081 tcp:8081
```

**WiFi 연결 시 필수** — 기기가 호스트 PC의 Metro 서버(8081)에 직접 접근 불가.
이 단계를 생략하면 "Unable to load script" 에러 발생.

### 5. 결과 보고

- 빌드 성공/실패 여부
- 설치된 기기 정보
- 에러 발생 시 Metro 로그 확인 (백그라운드 output 파일)

## Common Mistakes

| 실수 | 결과 | 해결 |
| :--- | :--- | :--- |
| adb reverse 생략 | Unable to load script | `adb -s <id> reverse tcp:8081 tcp:8081` |
| run-android 사용 | gradlew.bat 경로 인식 실패 | 직접 `cd android && ./gradlew` 실행 |
| Metro 미실행 | 기기에서 JS 번들 로드 실패 | Metro 백그라운드 실행 먼저 |
| adb connect 안 됨 | 기기 목록에 없음 | 사용자에게 connect 요청 |

## Device Selection

기기가 여러 대 연결된 경우:
1. WiFi 기기 우선 (`10.101.101.120` 패턴)
2.不确定하면 사용자에게 선택 요청
