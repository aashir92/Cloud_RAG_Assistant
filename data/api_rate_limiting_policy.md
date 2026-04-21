# API Rate Limiting and Retry Policy

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
