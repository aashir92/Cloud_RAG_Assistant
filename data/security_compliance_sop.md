# Security Compliance SOP

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
