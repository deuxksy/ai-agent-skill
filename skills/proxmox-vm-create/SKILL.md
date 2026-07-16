---
name: proxmox-vm-create
description: "Template 복제 + guest OS 설정으로 Proxmox VE VM 생성. template 복제, 사양 확장(sockets/cores/memory/net/disk), product_uuid + machine-id 방어, config 검증, guest OS 설정(netplan/hostname/disk/swap/sysctl/limits/machine-id). Provisioning 계층: qm(학습)→pvesh(테스트)→HTTP REST API(최종, VM lifecycle만). Guest exec 계층: qm guest exec / MCP execute_vm_command(HTTP /agent = exec 불가, 정보 명령만). Use when Proxmox cluster 노드 전체에 반복 VM provisioning이 필요할 때."
---

# Proxmox VM 생성 (pvesh 기반)

## Overview

Proxmox template 복제 → 사양 확장 → product_uuid/machine-id 방어 → verify → 게스트 OS 설정의 재사용 가능 자동화 패턴. `qm` CLI 대신 **`pvesh`(Proxmox REST API)** 기반 — cluster 어느 노드 쉘에서든 cross-node VM 조작 가능하고 자동화에 적합.

## When to Use

Proxmox 클러스터에 신규 VM 생성?
template(keco-base 등) 복제로 VM 만드는가?
여러 노드에 분산 배치해야 하는가?

Use cases:
- template 기반 worker VM 양산
- 사양 확정 후 동일 스펙 VM 반복 생성
- cross-node 배치(`--target` 지정)

NOT for:
- template 자체 생성/수정 (수동)
- GPU passthrough / PCI 할당 (별도 복잡 스펙)

> 게스트 OS 설정(netplan/hostname/disk/swap/sysctl/limits/machine-id)은 **하단 Guest OS 설정 섹션**에서 qm guest exec(노드 쉘) / MCP execute_vm_command(외부)로 자동화. HTTP API는 exec 불가(`/agent` 정보명령만) → 게스트 설정 제외.

## Core Pattern

3단계 + verify. 각 단계 응답 패턴이 상이 → 성공 판정 기준이 다름.

```text
1. clone   (create/POST) → 동기 progress + UPID (source 노드)
2. config  (set/PUT)     → 무응답 (즉시 적용)
3. resize  (set/PUT)     → 동기 progress + UPID (target 노드)
4. verify  (get/GET)     → YAML 응답 → 정합 확증
```

**핵심 원칙**: 응답 패턴은 HTTP method가 아니라 **작업의 sync/async 성격**으로 결정. config(즉시 적용)는 무응답, clone/resize(시간 소요)는 동기 대기 후 UPID. **set 무응답은 성공 단정 금지 → 반드시 get으로 verify.**

## Quick Reference

| 단계 | 명령 | 성공 판정 |
| :--- | :--- | :--- |
| clone | `pvesh create /nodes/{src-node}/qemu/{template-vmid}/clone --newid {newid} --name {name} --full 1 --target {dst-node}` | progress 100% + UPID |
| config | `pvesh set /nodes/{소속노드}/qemu/{newid}/config --sockets N --cores N --memory MB --cpu host --numa 1 --agent 1 --net0 '...' --net1 '...' --onboot 0 --smbios1 "uuid=$(uuidgen)"` | **무응답 → get verify 필수** |
| resize | `pvesh set /nodes/{소속노드}/qemu/{newid}/resize --disk scsi0 --size {G}` | `Resizing image: 100%` + UPID |
| verify | `pvesh get /nodes/{소속노드}/qemu/{newid}/config --output-format yaml \| grep -E 'sockets\|cores\|memory\|cpu\|numa\|agent\|net[01]\|scsi0\|onboot\|smbios1'` | Expected 값 정합 |

## 노드 경로 규칙

- **clone**: source template 소재 노드 경로 (`/nodes/{src-node}/qemu/{template-vmid}/clone`), `--target`로 배치 노드 지정
- **config/resize/verify**: VM **소속 노드**(= target) 경로 (`/nodes/{dst-node}/qemu/{newid}/...`)
- cluster 공유 config라 cluster 어느 노드 쉘에서든 호출 가능 (경로만 소속 노드로)

## 게스트 접근 경로 (네트워크 2계층)

**[실측 2026-06-20]** 네트워크 2계층 — 이전 "vnet100=NAT+SNAT, 포트포워딩 필요" 정정:

| 인터페이스 | 역할 | 호스트→게스트 접근 |
| :--- | :--- | :--- |
| **ens19 / vmbr10** (10.10.10.0/24) | 언더레이 관리망 (호스트 직접 브리지) | **직접 SSH OK** (`ssh kls@10.10.10.12x`) |
| **ens18 / vnet100** (172.20.100.0/16) | EVPN/VXLAN 오버레이 (zone evpn01), K8s 서비스망 | 호스트에서 BGP 경유만 (직접 TCP FAIL) |

→ **DNAT 포트포워딩(20040/20050) 불필요**. ens19(vmbr10)로 관리 직접 접근. cluster 호스트 자신은 ens18 직접 접근 불가 → 호스트 작업은 ens19 직접 SSH 또는 `qm guest exec`(virtio-serial, IP 무관).

## product_uuid + machine-id 방어 (template 복제 Blocker)

template 복제 시 `smbios1 uuid`가 상속 → **product_uuid(DMI) 중복** (K8s join 실패 원인). **machine-id**도 동일한 SMBIOS uuid 기반이므로 함께 방어.

**기동 전 선제 (product_uuid)**: config 단계에 `--smbios1 "uuid=$(uuidgen)"` 포함 → `/sys/class/dmi/id/product_uuid` 고유.

**기동 후 수동 (machine-id)**: 복제 게스트는 `/etc/machine-id`가 이미 채워져 있어 SMBIOS uuid 변경이 자동 반영 안 됨. 게스트 기동 후 **수동 재생성** (product_uuid와 일치 정책 권장):

```bash
# template uuid 확인
pvesh get /nodes/{src-node}/qemu/{template-vmid}/config --output-format yaml | grep smbios1
# config에서 uuid 재할당(기동 전) 후, 게스트에서 machine-id 고유화 (1줄 guest exec)
qm guest exec {id} -- bash -c 'rm -f /etc/machine-id /var/lib/dbus/machine-id && systemd-machine-id-setup && cp /etc/machine-id /var/lib/dbus/machine-id'
# verify — product_uuid vs machine-id
qm guest exec {id} -- cat /sys/class/dmi/id/product_uuid
qm guest exec {id} -- cat /etc/machine-id
```

> `systemd-machine-id-setup`은 빈 machine-id에서만 SMBIOS uuid 매핑 — 복제 게스트(이미 채워짐)는 삭제 후 재생성 필요. 115/116 실측: machine-id 고유화 후 K8s join Blocker 해소.
>
> **기존 worker(105/106/107/111)는 template uuid 상속 machine-id 미고유화** — 107 실측 `/etc/machine-id=db0236803ae347a7a7f6ff794a4aa03b`(= 100 smbios1 uuid 그대로). 과거 생성이라 방어 미적용(운영 중이라 작동은 하나 이론적 K8s 중복 Blocker). **신규 VM(115/116)은 반드시 고유화** — 본 방어가 그 필요성 입증.

## Guest OS 설정 — 게스트 접근 계층

VM 부팅 후 게스트 내부 OS 설정. **agent=1 선행 필수**(config 단계 `--agent 1` — virtio-serial channel 생성). qm/MCP 계층은 실행 환경·한계가 상이 → 상황별 선택. HTTP API는 exec 불가(상단 HTTP REST API 매핑).

### 접근 계층 (3-layer)

| 계층 | 도구 | 실행 환경 | shell 구문 | 용도 |
| :--- | :--- | :--- | :--- | :--- |
| **1. qm guest exec** | `qm guest exec {id} -- ...` | 소속 노드 쉘 | O (bash) | 기본. IP 무관 virtio-serial. 복붙 시 1줄 단위 |
| **2. MCP execute_vm_command** | `mcp__proxmox__execute_vm_command` | 외부(Mac/MCP) | **X (단일 명령)** | 외부 원격. **읽기(get) 위주** — 기존 장비 조사 |
| **3. HTTP API** | clone/config/resize (POST/PUT) + `/agent` 정보명령 (GET) | 외부(HTTP) | — (exec 불가) | **VM lifecycle 자동화** 한정. 게스트 exec 불가(하단) |

**선택 기준(게스트 설정)**: 노드 쉘 있으면 **1(qm guest exec)**, 외부는 **2(MCP execute_vm_command, 단일/읽기)**. **HTTP API(3)는 게스트 exec 불가** → 게스트 설정 자동화는 qm 또는 MCP만. HTTP API는 VM lifecycle(clone/config/resize) 자동화 영역.

### 핵심 원칙: 1줄 단위 실행
긴 `&&` 체인은 터미널 복붙 시 **newline 잘림 → bash syntax error**. 각 명령을 **독립 1줄 guest exec**로 분할. (MCP 계층은 애초에 단일 명령만 — 하단)

### 시퀀스 (K8s worker 기준, 115/116 실측)

| 단계 | 명령 | 비고 |
| :--- | :--- | :--- |
| agent 확인 | `qm guest cmd {id} ping` | virtio-serial 동작 |
| netplan | base64 주입 → `/etc/netplan/50-cloud-init.yaml` | IP 충돌 회피 (하단) |
| cloud-init disable | `99-disable-network-config.cfg`(`network: {config: disabled}`) | 재부팅 시 netplan 보존 (template IP 충돌 근본, 하단) |
| hostname | `qm guest exec {id} -- hostnamectl set-hostname {fqdn}` | |
| disk 확장 | `qm guest exec {id} -- growpart /dev/sda 2` 후 `resize2fs /dev/sda2` | lsblk 실측 우선 (sda1=BIOS boot) |
| swap off | `qm guest exec {id} -- swapoff -a` + `/etc/fstab` swap 라인 제거 | K8s 필수 |
| machine-id | `systemd-machine-id-setup` 재생성 + dbus 동기화 | product_uuid 방어 섹션 |
| guest-agent start | `qm guest exec {id} -- systemctl start qemu-guest-agent` | socket-activated unit (enable 양성 실패 → start) |
| sysctl | br_netfilter + bridge-nf-call-iptables/ip6tables + ip_forward + inotify — **1줄씩** | K8s 노드 필수 |
| limits | `* soft/hard nofile 65535` | |
| verify | product_uuid + machine-id 유일성 + 적용값 | |

### netplan base64 안전 주입 (newline 잘림 회피)
긴 YAML은 heredoc/복붙이 newline 잘림 → **base64 인코딩 후 게스트에서 디코딩**:

```bash
NETPLAN_B64=$(printf 'network:\n  ethernets:\n    ens18:\n      addresses: [{NET0_CIDR}]\n      nameservers: {addresses: [8.8.8.8,1.1.1.1], search: [{DOMAIN}]}\n      routes: [{to: default, via: {GW}}]\n    ens19:\n      addresses: [{NET1_CIDR}]\n  version: 2\n' | base64 -w0)
qm guest exec {id} -- bash -c "echo $NETPLAN_B64 | base64 -d > /etc/netplan/50-cloud-init.yaml"
qm guest exec {id} -- netplan apply
```

### MCP execute_vm_command 한계 (기존 장비 조사 계층)
`mcp__proxmox__execute_vm_command`는 **execve 기반 단일 명령** — shell metacharacter(`&&`, `|`, `>`, `$(...)`) 미지원. 복잡 파이프/리다이렉트 불가. **읽기(조사) 위주 사용**, 기존 운영 장비는 읽기만:

```text
# OK (단일 명령, 읽기)
execute_vm_command(vmid=107, command="cat /etc/netplan/50-cloud-init.yaml")
execute_vm_command(vmid=107, command="lsblk -o NAME,SIZE,FSTYPE,MOUNTPOINT")
execute_vm_command(vmid=107, command="cat /etc/machine-id")

# FAIL (shell 구문) → qm guest exec(노드 쉘)만 (HTTP /agent도 exec 불가)
execute_vm_command(command="lsblk && df -h")                # && 미지원
execute_vm_command(command="cat /etc/hosts | grep worker")  # | 미지원
```

> 복잡 스크립트·쓰기(set)는 qm guest exec(노드 쉘)만 — **HTTP /agent는 exec 불가**(9.1.1 실측). 기존 운영 장비(105/106/107/111)는 **읽기만**, 신규(116)는 쓰기 허용.

### cross-node (pvesh agent)
`qm guest exec`는 **소속 노드 쉘**에서만. cross-node 자동화는 HTTP `/agent` endpoint (상단 HTTP API 매핑).

## HTTP REST API 매핑 (VM lifecycle 자동화)

pvesh/qm은 Proxmox 노드 쉘 의존(CLI 래퍼). **VM lifecycle(clone/config/resize)은 HTTP REST API로 외부 자동화 가능** — API token 인증, 노드 쉘 불필요. **단, 게스트 exec는 HTTP 불가**(하단).

| pvesh / qm | HTTP endpoint | Method | 실측 |
| :--- | :--- | :--- | :--- |
| `pvesh create .../clone` | `/api2/json/nodes/{node}/qemu/{src}/clone` | POST | (pvesh 검증) |
| `pvesh set .../config` | `/api2/json/nodes/{node}/qemu/{id}/config` | PUT | (pvesh 검증) |
| `pvesh set .../resize` | `/api2/json/nodes/{node}/qemu/{id}/resize` | PUT | (pvesh 검증) |
| `pvesh get .../config` | `/api2/json/nodes/{node}/qemu/{id}/config` | GET | ✅ 9.1.1 실측 (107 config 조회 OK) |
| `qm guest exec` | **HTTP 매핑 불가** | — | ❌ `/agent` exec 미지원 (하단) |

**인증**: Proxmox API Token (Token ID `user@realm!tokenid` + Secret), `Authorization: PVEAPIToken=...` header. 비인터랙티브 자동화.

**[실측 2026-06-22] HTTP /agent = exec 불가**: Proxmox 9.1.1 `/api2/json/nodes/{node}/qemu/{id}/agent`의 `command` param은 **정보명령만**(ping/network-get-interfaces/get-osinfo/get-time/get-users/shutdown/fstrim/suspend-*). `exec` 미지원, `/agent/exec` 전용 endpoint도 부재. → **HTTP API로 게스트 명령 실행 불가**. 게스트 설정은 qm guest exec(노드 쉘) 또는 MCP execute_vm_command만.

```bash
# OK — GET config (인증/응답 정상)
curl -sk -H "Authorization: PVEAPIToken=$TOKEN" \
  https://{node}:8006/api2/json/nodes/{node}/qemu/{id}/config

# FAIL — /agent exec (command 'exec' not in enum)
curl -sk -H "Authorization: PVEAPIToken=$TOKEN" -d 'command=exec' \
  -d 'command[]=/bin/bash' -d 'command[]=-c' -d 'command[]=hostname' \
  https://{node}:8006/api2/json/nodes/{node}/qemu/{id}/agent
# → errors: command 'exec' does not have a value in the enumeration
#   'ping,network-get-interfaces,get-osinfo,shutdown,fstrim,suspend-*,...'
```

> MCP `execute_vm_command`는 동작(107 실측 cat 성공)하나 **HTTP `/agent` 경유가 아님** — QMP socket 또는 노드 `qm` CLI 래핑(구현 의존). HTTP API로 게스트 설정 자동화는 불가하므로, **게스트 자동화의 최종형은 qm guest exec(노드 쉘) 또는 MCP**.

**왜 HTTP API (범위 한정)**: VM lifecycle(clone/config/resize)은 외부 호출 가능(CI/연동). **게스트 설정은 노드 쉘(qm) 또는 MCP** — HTTP `/agent` exec 한계로 게스트 자동화 범위 밖.

## Common Pitfalls

| Issue | Solution |
| :--- | :--- |
| config set 무응답 = 실패로 오인 | pvesh PUT 성공은 무응답이 정상 → get으로 정합 확증 |
| product_uuid 중복 (K8s join 실패) | config에 `--smbios1 "uuid=$(uuidgen)"` 선제 적용 (기동 전) |
| **machine-id 중복** | 복제 게스트는 `/etc/machine-id` 수동 재생성(`systemd-machine-id-setup`) — SMBIOS uuid 변경만으로 자동 반영 안 됨 |
| 노드 경로 404 | clone은 source 노드 경로, config/resize는 **소속(target) 노드** 경로 |
| net param 파싱 에러 | `--net0 'virtio,bridge=vnet100,firewall=1,queues=16'` 쉘 인용 (콤마) |
| boolean 값 | API는 `1`/`0` (`--full 1`, `--onboot 0`) — `true`/`false` 아님 |
| cloud-init 없는 template | IP/hostname netplan 수동 (guest exec) |
| 동시 기동 IP 충돌 | template netplan이 static이면 직렬 기동 + 콘솔 netplan 수정 |
| **IP 충돌 근본 (template 복제)** | template의 cloud-init `90-installer-network.cfg`(subiquity)에 기존 VM IP(예: mgmt-01 172.20.100.10) 박힘 → 복제 상속 → 첫 부팅 충돌. cloud-init 비활성화(`99-disable-network-config.cfg`) 또는 guest exec로 netplan 즉시 고정. **운영 패턴 2종 실측**: 115=disable 적용 / 107·111=disable 없이 `50-cloud-init.yaml` 수동 고정(90-installer-network.cfg 잔존) |
| **firewall 값 오인** | `firewall=1`은 Proxmox 방화벽 "연결 플래그"(자동 차단 아님). 실제 차단은 datacenter/node/VM 룰. NAT SSH timeout 원인 아님 — 반드시 실측 config(qm config)로 확인, memory/추정 맹신 금지 |
| **guest exec newline 잘림** | 긴 `&&` 체인 금지, 1줄 단위 분할. 긴 파일은 base64 주입 |
| **MCP execute_vm_command shell 미지원** | 단일 명령만. `&&`/`|`/`>` FAIL → 읽기 위주 사용. 복잡 스크립트·쓰기는 qm guest exec(노드 쉘)만 |
| **HTTP /agent exec 미지원** | Proxmox 9.1.1 `/agent`는 정보명령(ping/network-get-interfaces/get-osinfo/shutdown)만 — guest exec 불가(실측). HTTP API로 게스트 설정 불가 → qm guest exec(노드) 또는 MCP만 |
| **게스트 접근 = ens19(vmbr10) 직접** | NAT/포트포워딩 불필요(실측 정정). 호스트→게스트는 ens19 직접 SSH 또는 guest exec. ens18(vnet100)은 호스트 직접 접근 불가(EVPN/BGP 경유) |

## Full Template (worker VM 생성 예시)

```bash
# Variables
SRC_NODE=ecoai-cluster-01        # template 소재 노드
TMPL=100                          # template VMID
NEWID=116                         # 신규 VMID
NAME=keco-worker-06
DST_NODE=ecoai-cluster-02         # 배치(소속) 노드
DISK_SIZE=2048G                   # qm 단위 G=GiB, 2048G=2TiB

# 1. clone (source 노드 경로, --target 배치) — 동기 progress + UPID
pvesh create /nodes/$SRC_NODE/qemu/$TMPL/clone \
  --newid $NEWID --name $NAME --full 1 --target $DST_NODE

# 2. config 확장 (소속 노드 경로) — 무응답 = 성공
pvesh set /nodes/$DST_NODE/qemu/$NEWID/config \
  --sockets 2 --cores 12 --memory 32768 \
  --cpu host --numa 1 --agent 1 \
  --net0 'virtio,bridge=vnet100,firewall=1,queues=16' \
  --net1 'virtio,bridge=vmbr10,firewall=1,queues=16' \
  --onboot 0 --smbios1 "uuid=$(uuidgen)"

# 3. resize (소속 노드, 동기 + UPID)
pvesh set /nodes/$DST_NODE/qemu/$NEWID/resize --disk scsi0 --size $DISK_SIZE

# 4. verify — 무응답 단계 정합 확증
pvesh get /nodes/$DST_NODE/qemu/$NEWID/config --output-format yaml | grep -E 'sockets|cores|memory|cpu|numa|agent|net[01]|scsi0|onboot|smbios1'
```

> config에 `--cpu host --numa 1 --agent 1` 포함(공식 필수). 게스트 OS 설정은 상단 Guest OS 섹션(qm/MCP 게스트 접근 계층).

## qm CLI vs pvesh (학습 기록)

| 항목 | qm (CLI) | pvesh (REST API) |
| :--- | :--- | :--- |
| clone | `qm clone $TMPL $NEWID --full --target $DST` | `pvesh create .../clone --newid ... --full 1 --target ...` |
| config | `qm set $NEWID --cores 12 ...` (로컬 자동) | `pvesh set .../config ...` (소속 노드 경로 명시) |
| resize | `qm resize $NEWID scsi0 2048G` | `pvesh set .../resize --disk scsi0 --size 2048G` |
| cross-node | 로컬 노드 우선 | cluster 어디서나 경로 지정 |
| 자동화 적합 | 낮음 (출력 파싱) | 높음 (구조화 응답) |
| 성공 판정 | exit code + 출력 | set=무응답 → get verify |

## Key Rules

- **set(PUT) 무응답은 성공 단정 금지** → get으로 정합 확증
- **product_uuid + machine-id 이중 방어**: config `--smbios1 uuid=$(uuidgen)`(기동 전) + 게스트 machine-id 수동 재생성(기동 후)
- **clone은 source 노드, config/resize는 소속 노드** 경로
- **게스트 접근**: qm guest exec(노드 쉘, 기본) / MCP execute_vm_command(외부, 읽기, 단일 명령). HTTP API는 exec 불가(/agent 정보명령만) → 게스트 자동화는 qm 또는 MCP
- **승인 게이트**: VM 생성(POST/PUT)은 사용자 승인 후 실행 (Proxmox API 규칙: Read 자유 / Create·Update·Delete 승인)
- **onboot=0**: rollout 중 자동기동 방지, join/검증 완료 후 onboot=1
