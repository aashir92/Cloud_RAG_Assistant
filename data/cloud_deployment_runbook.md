# Cloud Deployment Runbook

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
