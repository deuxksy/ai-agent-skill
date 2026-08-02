---
name: deploy-android-wifi
description: Use when WiFi ADB로 연결된 Android 기기에 React Native 앱을 배포. Metro server 실행, gradle 빌드, 설치, adb reverse port forwarding을 자동 처리.
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
1. adb devices 로 기기 연결 확인 → WiFi 우선 선택, 없으면 USB fallback
2. Metro 서버 실행 (백그라운드, 없으면)
3. 선택된 기기에만 gradle installDebug 빌드 & 설치
4. adb reverse tcp:8081 tcp:8081 포트 포워딩 (WiFi 기기만)
5. 결과 보고
```

## Implementation

### 1. 기기 연결 확인 & 선택 (WiFi 우선)

```bash
adb devices
```

**기기 선택 로직 (필수 준수):**

1. `adb devices` 출력에서 IP:PORT 패턴(`\d+\.\d+\.\d+\.\d+:\d+`)이 있으면 → **WiFi 기기로 선택**
2. WiFi 기기가 없으면 → USB 기기로 fallback
3. 대상 기기가 없으면 사용자에게 `adb connect` 요청

선택된 기기 ID를 이후 모든 단계에서 사용.

### 2. Metro 서버 시작 (백그라운드)

```bash
# Metro가 이미 실행 중인지 확인
curl -s http://localhost:8081/status > /dev/null 2>&1

# 실행 중이 아니면 백그라운드로 시작
npx react-native start
# → run_in_background 로 실행
```

### 3. Gradle 빌드 & 설치 (선택된 기기에만)

```bash
# ANDROID_SERIAL로 대상 기기 지정 → 1대에만 설치
ANDROID_SERIAL=<selected-device-id> ./gradlew app:installDebug -x lint -PreactNativeDevServerPort=8081
```

**필수:** `ANDROID_SERIAL` 환경변수로 1단계에서 선택한 기기만 설치.
이 변수 없으면 연결된 **모든 기기**에 설치됨 (의도치 않은 USB 동시 설치 방지).

**주의:** `npx react-native run-android` 대신 직접 gradle 실행.
`run-android`는 Windows 환경에서 `gradlew.bat` 경로 인식 실패 이슈 있음.

### 4. adb reverse 포트 포워딩 (WiFi 기기만)

```bash
adb -s <wifi-device-id> reverse tcp:8081 tcp:8081
```

**WiFi 기기에만 필요** — USB 기기는 호스트 Metro 서버에 직접 접근 가능하므로 생략.
WiFi 기기는 포트 포워딩 없으면 "Unable to load script" 에러 발생.

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

## Device Selection (핵심 로직)

```
adb devices 파싱 → IP:PORT 패턴 있으면 WiFi 선택
                → 없으면 USB 기기 선택
                → 둘 다 없으면 사용자에게 adb connect 요청
```

| 상황 | 선택 | adb reverse |
| :--- | :--- | :--- |
| WiFi + USB 둘 다 연결 | WiFi (IP:PORT 패턴) | WiFi에만 설정 |
| WiFi만 연결 | WiFi | 설정 |
| USB만 연결 | USB | 불필요 (생략) |
| 아무것도 없음 | 사용자에게 connect 요청 | - |
