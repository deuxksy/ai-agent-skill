---
name: ai
description: "AI 시스템 보안 점검 (KECO 별첨6 체크리스트 ①~⑮). 읽기 전용 kubectl로 AI 워크로드 SA·RBAC·NetworkPolicy·모니터링·백업·이미지 출처·API 인증·취약점 스캐너를 점검 후 충족/조치계획 판정과 증빙 리포트 생성. `/kisa:ai [namespace...]`."
---

# AI System Security Audit (KECO 별첨6 체크리스트)

AI 인프라(vllm·embedding·reranker·pgvector 등)를 읽기 전용 kubectl로 점검하여 기후에너지환경부 AI 도입 체크리스트(별첨6) ①~⑮의 반영여부를 확인한다.

## 핵심 프로세스

```text
사전 조건 확인 → AI 워크로드 식별 → 체크리스트 실측 8개 섹션 (읽기 전용) → 항목별 판정 → 증빙 리포트 md 생성
```

## 사용법

```bash
/kisa:ai                    # 기본 대상: mgmt-system, llm-prod
/kisa:ai mgmt-system        # 단일 namespace
/kisa:ai ns-a ns-b          # 복수 namespace 지정
```

- 인자 없이 호출하면 기본값(mgmt-system·llm-prod — ecoai 프로덕션 환경 값)으로 실행한다. 다른 클러스터 점검 시 `KUBECONFIG`와 대상 namespace를 먼저 조정한다

## 절차

### 1. 사전 조건

```bash
export KUBECONFIG=~/.kube/mgmt.config   # 접속 클러스터에 맞게 조정
```

- 읽기 전용(`get`·`describe`·`logs`)만 사용 — 변경 금지

### 2. AI 워크로드 식별

대상 namespace의 워크로드에서 AI 계열(deploy·sts)을 식별한다. grep 패턴은 클러스터에 존재하는 워크로드에 맞게 조정한다.

```bash
kubectl get deploy,sts -n <ns> \
  -o custom-columns='NAME:.metadata.name,SA:.spec.template.spec.serviceAccountName,R:.spec.replicas,IMAGE:.spec.template.spec.containers[*].image'
```

- 앱 계층(rag-api 등)은 AI 인프라 대상에서 제외 — 식별 결과를 리포트 대상 표로 기록한다

### 3. 체크리스트 실측 (전부 읽기 전용)

각 섹션의 명령을 워크로드 식별 결과에 맞게 실행한다. ①~⑮와 섹션의 대응은 [references/checklist-mapping.md](references/checklist-mapping.md) 참조.

| 섹션 | 체크리스트 | 핵심 명령 |
| :--- | :--- | :--- |
| 1. SA·RBAC | ⑩ 과도한 권한·④ 학습데이터 접근통제 | `kubectl get sa,role,rolebinding -n <ns>` + deploy/sts SA 컬럼 조회 |
| 2. NetworkPolicy | ⑧ 경계보안 | `kubectl get networkpolicy -n <ns>` |
| 3. 서비스 타입·Ingress | ⑧·⑨ 통신구간 보호 | `kubectl get svc,ingress -n <ns>` + `dig +short <ingress 도메인>` |
| 4. 모니터링·로깅 | ⑥ | `kubectl get deploy,sts -n monitoring` + AI 파드 `logs --tail=5` |
| 5. 백업·PVC | ⑬ 복구방안·① 신뢰 출처 | `kubectl get cronjobs -A` + `kubectl get pvc -A \| grep <ns>` |
| 6. 이미지 출처 | ⑤ 모델·라이브러리 출처 | deploy/sts 이미지 `sort -u` 조회 — 공식 레지스트리 여부 |
| 7. API 인증 | ⑦ 입·출력 보안 | 식별한 ingress 도메인에 `curl` 무인증 GET — 401/403이면 인증 적용, 200이면 무인증 공개. POST(빈 JSON)는 상태 변경 가능하므로 사용자 승인 후에만 |
| 8. 취약점 스캐너 | ⑫ | 스캐너 파드 상태 조회 (예: `kubectl get pods -A \| grep -i trivy`) |

- `-n`은 중복 지정 불가 — 전체 조회가 필요하면 `-A` 후 grep 필터
- API 인증은 **GET으로 실측** — vLLM 등 일부 서버는 HEAD(`curl -sI`)를 405로 거부한다
- 스캐너 관리 API 호출에 관리자 자격증명이 필요하면 문서에 평문 기입 금지 — 파드 상태로 판정

### 4. 판정

각 항목을 3분류로 판정한다 (기준 상세는 [references/checklist-mapping.md](references/checklist-mapping.md)):

| 판정 | 의미 |
| :--- | :--- |
| **충족** | 실측 결과가 양호 조건을 문자 그대로 충족 |
| **조치계획** | 미적용·부재 — 실측 사실 기록 후 조치계획으로 분류 |
| **비대상** | kubectl 인프라 점검 대상 아님 (②③⑪⑭⑮ 문서 계층 — 리포트 조치계획란에서 관리) |

### 5. 증빙 리포트

출력 경로: **`./report/ai-<클러스터식별>-<YYMMDDhhmm>.md`** (`report/` 없으면 생성)

형식은 linux·web 스킬과 동일한 구조(메타 헤더 → 섹션 → 항목별 판정·명령·결과):

```markdown
# <클러스터/환경> AI 시스템 보안 점검 증빙 (별첨6 ①~⑮)
- 대상: <namespace 목록> — <워크로드 표 (이름·SA·replica·이미지)>
- 기준: 기후에너지환경부 AI 도입 체크리스트 별첨6
- 실행: <YYYY-MM-DD KST>, 읽기 전용 kubectl
- 요약: **충족 N · 조치계획 M · 비대상 K**
## 1. 워크로드 SA·권한 (체크리스트 ⑩·④)
### ⑩ 과도한 권한 제한 — 판정: **조치계획**
명령: · 결과: (원문 블록)
```

## 안전 규칙

- **읽기 전용만 실행** — kubectl get·describe·logs와 무인증 curl GET만 기본 실행. POST는 상태 변경 가능(GPU 작업 생성·행 생성)하므로 사용자 승인 후에만 제한 실행
- 판정은 실측 사실 기반 — 추측으로 충족 판정 금지
- 증빙에는 자격증명·세션 쿠키가 남지 않는지 확인 후 산출물 저장
- 조치(remediation)는 별도 작업 — 이 스킬은 진단만

## 참고

- 점검 체계: 기후에너지환경부 AI 도입 체크리스트 별첨6 (①~⑮)
- 체크리스트 ↔ 섹션 매핑·판정 기준: [references/checklist-mapping.md](references/checklist-mapping.md)
- 관련 스킬: `kisa:db`(벡터 DB·RDB 점검), `security:system-audit`(패키지 CVE)
