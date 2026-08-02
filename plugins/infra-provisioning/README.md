# infra-provisioning Plugin

머신 초기 설정(dotfiles/Tailscale), 시스템 업그레이드, Proxmox VE VM 생성 및 OpenWrt 백그라운드 서비스 등록 스킬을 제공하는 인프라 도메인 플러그인입니다.

## 🛠️ 포함 스킬 (4)

- **`setup`**: 초기 설정 (brew, stow, sops 복호화, Tailscale Aperture)
- **`system-upgrade`**: OS 패키지 업그레이드 (brew, apt, dnf, nix)
- **`proxmox-vm-create`**: Proxmox VE VM 프로비저닝 (qm ➔ pvesh ➔ REST API)
- **`openwrt-initd`**: OpenWrt init.d 백그라운드 서비스 설치 및 프로세스 감시

## 🚀 설치 방법

```bash
claude plugin install infra-provisioning@zzizily
```
