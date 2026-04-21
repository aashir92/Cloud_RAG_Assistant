# Access Management and Secrets Rotation Standard

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
