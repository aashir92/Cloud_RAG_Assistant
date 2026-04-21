"""Generate a mock enterprise IT knowledge base for local RAG testing."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict


ROOT_DIR = Path(__file__).resolve().parent
DATA_DIR = ROOT_DIR / "data"
LOG_DIR = ROOT_DIR / "logs"
LOG_FILE = LOG_DIR / "data_generation.log"


def setup_logging() -> None:
    """Configure console and file logging."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[logging.FileHandler(LOG_FILE, encoding="utf-8"), logging.StreamHandler()],
    )


def build_documents() -> Dict[str, str]:
    """Return markdown documents for IT infrastructure and cloud operations."""
    return {
        "server_configuration_protocol.md": """# Server Configuration Protocol

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
""",
        "api_rate_limiting_policy.md": """# API Rate Limiting and Retry Policy

## Purpose
Prevent abuse, protect backend services, and maintain fair usage across internal and partner clients.

## Rate Limit Tiers
- Internal service accounts: 300 requests/minute per client ID.
- Partner integrations: 120 requests/minute per client ID.
- Anonymous traffic: 30 requests/minute per source IP.

## Enforcement Rules
- Use API gateway token bucket enforcement.
- Return HTTP 429 with `Retry-After` headers on threshold breach.
- Apply burst capacity at 2x sustained limit for up to 10 seconds.

## Retry Guidance
- Clients should use exponential backoff with jitter.
- Do not retry non-idempotent POST requests without idempotency keys.
- Escalate to SRE if 429 rates exceed 5 percent for 15 minutes.
""",
        "security_compliance_sop.md": """# Security Compliance SOP

## Policy Statement
All infrastructure changes must align with SOC 2 controls and internal security governance.

## Mandatory Security Controls
- Enforce MFA for all privileged admin accounts.
- Rotate secrets every 90 days or immediately after incident exposure.
- Encrypt data at rest with platform-managed keys and in transit with TLS 1.2+.
- Track all production changes via approved change tickets.

## Incident Response
1. Classify incident severity (SEV-1 to SEV-4).
2. Isolate impacted systems and preserve forensic evidence.
3. Notify security operations and incident commander.
4. Publish containment status updates every 30 minutes for SEV-1.
5. Complete post-incident review within 5 business days.

## Enforcement
Teams that fail mandatory controls are blocked from production deployment until remediation evidence is approved.
""",
        "cloud_deployment_runbook.md": """# Cloud Deployment Runbook

## Objective
Define release, validation, and rollback procedures for cloud-native services.

## Pre-Deployment Gates
- CI pipelines must pass tests, lint, and image vulnerability scans.
- Infrastructure-as-code plans must be peer-reviewed and approved.
- Deployment window must be scheduled with stakeholder visibility.

## Deployment Procedure
1. Deploy to staging and run synthetic health checks.
2. Release to production using canary rollout (10%, 25%, 50%, 100%).
3. Monitor latency, error rates, and saturation indicators.
4. Halt rollout automatically on SLO breach.

## Rollback Protocol
- Trigger rollback when error rate doubles baseline for 10+ minutes.
- Revert to previous stable container image and IaC revision.
- Communicate rollback status in incident channel and status page.
""",
        "access_management_standard.md": """# Access Management and Secrets Rotation Standard

## Scope
Applies to IAM users, service accounts, and platform automation identities.

## Access Provisioning
- Follow role-based access control and least privilege.
- Require manager approval for privileged role assignments.
- Use just-in-time elevation for production admin actions.

## Credential and Secret Hygiene
- Store credentials only in approved secret manager systems.
- Rotate database and API credentials every 90 days.
- Disable dormant accounts after 30 days of inactivity.
- Revoke all access within 4 hours of employee offboarding.

## Auditing
- Run monthly access recertification by system owners.
- Log all authentication events and retain for 365 days.
""",
    }


def write_documents(documents: Dict[str, str]) -> int:
    """Write markdown files to disk and return count."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    created = 0
    for filename, content in documents.items():
        path = DATA_DIR / filename
        path.write_text(content.strip() + "\n", encoding="utf-8")
        logging.info("Wrote knowledge base file: %s", path)
        created += 1
    return created


def main() -> None:
    """Generate the mock IT knowledge base."""
    setup_logging()
    logger = logging.getLogger("data_generation")
    logger.info("Starting dataset generation in %s", DATA_DIR)
    document_count = write_documents(build_documents())
    logger.info("Completed dataset generation. Files created: %d", document_count)


if __name__ == "__main__":
    main()
