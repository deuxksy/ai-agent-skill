---
name: license
description: Use when 산출물(APK/IPA/번들)에 포함되는 오픈소스 라이선스 전수 조사가 필요할 때. 소스맵·gradle·Podfile.lock 실측 기반으로 licenses.md 문서를 생성.
---

# License Inventory

실제 산출물에 포함되는 라이브러리·에셋의 라이선스 전수 조사. package.json 전체 의존성 같은 선언값이 아닌 아래 4계층 **실측** 기준. 빌드·배포 도구(fastlane, GPP, Metro 빌드타임, babel, sharp)는 산출물 미포함이므로 제외.

## 실측 방법 (4계층)

### 1. JS 번들 — Metro 소스맵 (번들에 포함된 모듈만)

```bash
# 소스맵: android/app/build/generated/sourcemaps/react/<releaseVariant>/*.map
node -e "const m=JSON.parse(require('fs').readFileSync('<소스맵>','utf8'));const s=new Set();for(const x of m.sources){const r=x.match(/node_modules\/(@[^/]+\/[^/]+|[^/]+)/);if(r)s.add(r[1]);}console.log([...s].sort().join('\n'))"
```

### 2. Android native — gradle 런타임 클래스패스 (APK 포함 아티팩트)

```bash
cd android && ./gradlew :app:dependencies --configuration <releaseVariant>RuntimeClasspath --console=plain -q
```

트리 내 다중 버전은 빌드 시 해정되므로 `group:artifact` 단위로 관리.

### 3. iOS — Podfile.lock + LICENSE 원문

```bash
grep -E '^  - [A-Za-z]' ios/Podfile.lock
find ios/Pods/<Pod> -maxdepth 1 -iname 'licen*'   # COPYING 등 변형명 커버
```

### 4. npm 메타데이터 (설치된 실제 버전)

```bash
node -e "const p=require('<패키지>/package.json');console.log(p.name,p.version,p.license)"
```

`license` 필드와 LICENSE 원문이 다르면 **원문 우선**.

## 함정

| 함정 | 대응 |
| :--- | :--- |
| package.json 전체 의존성 기준 조사 | 미번들 패키지 과다 포함 — 소스맵 실측 기준 |
| Metro를 포함으로 처리 | 빌드 도구라 제외 — `metro-runtime`(번들 내장 폴리필)만 예외 포함 |
| autolink 네이티브 모듈 누락 | Maven 좌표 없음 — npm 소스 빌드 모듈로 별도 섹션 구성 |
| JS import 0개 = 미포함 판단 | autolinking은 네이티브를 컴파일함 — "미사용이나 native 포함" 표기 후 제거 검토 |
| transitive 전부 MIT 가정 | hoist-non-react-statics(BSD-3) 사례 — 패키지별 개별 확인 |
| 에셋 제외 | 폰트(SIL OFL 고지 의무), Lottie JSON(출처별 상이 — 미확인 ⚠️ 표기) |

## 산출물 (licenses.md)

- Copyleft(GPL/LGPL/AGPL) 포함 여부 최상단 명시 — 0건이면 "0건"으로 명시적 기록
- 계층별 상세 표: 패키지 / 버전 / 라이선스 / 실측 vs 선언값 구분 표기
- 고지 의무 요약: Apache-2.0=전문+NOTICE · MIT=저작권 문구 · BSD-3-Clause=조건+면책 · BSL-1.0=저작권 문구 · SIL OFL=폰트 고지
- 관리 TODO (미확인 항목, 제거 검토 대상) + 재생성 방법 — 위 4계층 실측 명령을 그대로 기록해 의존성 변경 시 재실행 가능하게
