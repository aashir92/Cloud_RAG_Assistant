# Server Configuration Protocol

## Purpose
Define standard Linux server hardening and baseline configuration controls for production workloads.

## Baseline Controls
- Enforce SSH key-only authentication; disable password login.
- Disable root SSH access and use a least-privilege sudo workflow.
- Enable unattended security updates and weekly patch windows.
- Configure host-based firewall to allow only required service ports.

## Service Standardization
- All services must run under dedicated non-root service accounts.
- Systemd units must include restart policies and resource limits.
- Application logs must be forwarded to centralized observability pipelines.

## Verification Checklist
1. Validate CIS benchmark controls for OS image.
2. Confirm endpoint protection and EDR agent are active.
3. Confirm timezone, NTP sync, and auditd policies.
4. Record host metadata in CMDB before release.
