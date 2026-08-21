---
name: license
description: Use when 산출물(APK/IPA/번들)에 포함되는 오픈소스 라이선스 전수 조사가 필요할 때. 소스맵·gradle·Podfile.lock 실측 기반으로 licenses.md 문서를 생성.
---

# License Inventory

## Overview

저작권 관리를 위해 **실제 산출물에 포함되는 라이브러리·에셋의 라이선스 전수 목록**을 조사해 문서화하는 Skill.

package.json 전체 의존성 같은 선언값 추정이 아니라, 아래 4계층 **실측** 기반:

1. JS 번들 — Metro release 소스맵 `sources` (번들에 포함된 모듈만)
2. Android native — gradle release 런타임 클래스패스 (APK 포함 아티팩트)
3. iOS — `Podfile.lock` 최상위 pod + `Pods/<Pod>/LICENSE` 원문
4. npm 메타데이터 — `node_modules/<pkg>/package.json` (설치된 실제 버전)

빌드·배포 도구(fastlane, GPP, Metro 빌드타임, babel, sharp)는 산출물 미포함이므로 제외.

## When to Use

- "라이선스 조사", "오픈소스 조사", "저작권 관리" 요청 시
- 앱 출시 전 고지(Attribution) 의무·Copyleft 포함 여부 확인 필요 시
- 의존성 대량 변경 후 컴플라이언스 재점검 시

## Prerequisites

- React Native 프로젝트 (`android/`, `ios/` 디렉토리 존재)
- Android: release 빌드 1회 이상 완료 (소스맵 생성용)
- iOS: `pod install` 완료 (`Podfile.lock` 존재)

## Workflow

```text
1. JS 번들 실측 — 소스맵 sources에서 node_modules 패키지 추출
2. Android native 실측 — gradle RuntimeClasspath 의존성 트리
3. iOS 실측 — Podfile.lock + LICENSE 원문 대조
4. npm 라이선스 확인 — 설치 버전 기준
5. 에셋 확인 — 폰트, Lottie JSON
6. licenses.md 문서화 — 분포 요약 + 고지 의무 + 재생성 명령
```

## Implementation

### 1. JS 번들 — Metro 소스맵

```bash
# 소스맵 존재 확인 (variant는 프로젝트 release variant로 치환)
ls android/app/build/generated/sourcemaps/react/prodRelease/

# sources에서 node_modules 패키지 추출
node -e "const m=JSON.parse(require('fs').readFileSync('<소스맵경로>','utf8'));const s=new Set();for(const x of m.sources){const r=x.match(/node_modules\/(@[^/]+\/[^/]+|[^/]+)/);if(r)s.add(r[1]);}console.log([...s].sort().join('\n'))"
```

- 이 결과가 "번들에 실제 포함된 JS 패키지" 전체 (직접 + transitive)
- package.json dependencies에 있어도 여기 없으면 번들 미포함

### 2. Android native — gradle 런타임 클래스패스

```bash
cd android && ./gradlew :app:dependencies --configuration prodReleaseRuntimeClasspath --console=plain -q
# group:artifact:version 추출 (해정 화살표 -> 기준으로 실제 반영 버전 확인)
grep -oE '[a-zA-Z0-9._-]+:[a-zA-Z0-9._-]+:[a-zA-Z0-9._+,>-]+' <출력> | sort -u
```

- `<releaseVariant>RuntimeClasspath` = APK에 포함되는 아티팩트
- 트리 내 다중 버전 표기는 빌드 시 단일 버전으로 해정되므로 `group:artifact` 단위로 관리

### 3. iOS — Podfile.lock + LICENSE 원문

```bash
grep -E '^  - [A-Za-z]' ios/Podfile.lock   # 최상위 pod 전체
find ios/Pods/<Pod> -maxdepth 1 -iname 'licen*'  # LICENSE 원문 경로
```

- LICENSE 탐색은 `ls | grep` 대신 `find -maxdepth 1 -iname 'licen*'` — COPYING 등 변형 파일명 커버

### 4. npm 라이선스

```bash
node -e "const p=require('<패키지>/package.json');console.log(p.name,p.version,p.license)"
```

- `license` 필드와 LICENSE 원문이 다르면 **원문 우선**

### 5. 에셋

| 에셋 | 확인 포인트 |
| :--- | :--- |
| 폰트 | SIL OFL 1.1 등 — 고지 의무 있음 |
| Lottie JSON | lottiefiles 출처별 상이 — 미확인 시 ⚠️ 표기 |

## 산출물 구조 (licenses.md)

프로젝트 문서 규칙에 맞는 위치에 작성:

```text
- YAML frontmatter + 문서 타입 명시
- 라이선스 분포 요약 표 — Copyleft(GPL/LGPL/AGPL) 포함 여부를 최상단에 명시
- 계층별 상세 표 (패키지 / 버전 / 라이선스 / 확인 방법)
- 고지(Attribution) 의무 요약:
  Apache-2.0 = 전문+저작권·NOTICE / MIT = 저작권 문구 /
  BSD-3-Clause = 조건+면책 / BSL-1.0 = 저작권 문구 / SIL OFL 1.1 = 폰트 고지
- 관리 항목 TODO (미확인 항목, 제거 검토 대상)
- 재생성 방법 — 위 4계층 실측 명령을 그대로 기록
```

## Common Mistakes

| 실수 | 결과 | 해결 |
| :--- | :--- | :--- |
| package.json 전체 의존성 기준 조사 | 미번들 패키지까지 과다 포함 | 소스맵 `sources` 실측 기준 |
| Metro를 포함으로 처리 | 빌드 도구 오포함 | 제외 — 단 `metro-runtime`(번들 내장 폴리필)만 예외 포함 |
| autolink 모듈 누락 | Maven 좌표 없어 gradle 트리에 안 나옴 | npm 소스 빌드 모듈로 별도 섹션 구성 |
| JS import 0개 = 미포함으로 판단 | 네이티브만 포함된 경우 누락 (예: inappbrowser) | "미사용이나 native 포함" 표기 + 제거 검토 대상 분류 |
| transitive 전부 MIT 가정 | BSD-3 등 예외 누락 (hoist-non-react-statics 사례) | 패키지별 개별 확인 |
| `ls \| grep -i licen` 탐색 | COPYING 등 변형명 누락 | `find -maxdepth 1 -iname 'licen*'` |
| 에셋 제외 | 폰트(LICENSE 고지 의무) 누락 | 폰트·Lottie 별도 섹션 |

## 검증 기준

- Copyleft(GPL/LGPL/AGPL) 포함 0건이면 "0건"으로 명시적 기록
- 각 계층 조사가 실측 기반인지 선언값 기반인지 표에 구분 표기
- 의존성 변경 시 재생성 명령으로 동일 결과 재현 가능해야 함
