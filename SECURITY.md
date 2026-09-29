# Security Policy

## Supported versions

| Version | Supported |
|---------|-----------|
| 0.1.x   | Yes       |

## Threat model (P0)

Sortie Deck is typically run as a **local / trusted-network control plane**. Treat bearer tokens and the token signing secret as credentials.

### Token theft

- Workbench stores the opaque Bearer token in `localStorage` (`sortie_token`). Any XSS in the workbench origin can exfiltrate it.
- Tokens are HMAC-bound to `TDT_TOKEN_SECRET`. Stolen tokens remain valid until logout or expiry (~7 days) if the secret is unchanged.
- Mitigations: keep the workbench origin tight (CORS), avoid injecting untrusted HTML into the UI, set a strong `TDT_TOKEN_SECRET`, and prefer `TDT_ENV=production` with a non-default secret.

### Weak or missing signing secret

- Default development secret is `tdt-dev-secret`. It is **not** safe for shared or internet-facing deployments.
- When `TDT_ENV=production`, the API refuses to start without a non-default `TDT_TOKEN_SECRET`.
- Rotating the secret invalidates all outstanding signed tokens (clients must log in again).

### Artifact path traversal

- Artifact downloads resolve paths under `data/artifacts/`. Paths that escape the store root (e.g. `../`) are rejected.
- Download endpoints require an authenticated user.

### Logging

- Do not log raw `Authorization` headers or bearer token values. Prefer user id / username only in audit-style logs.

## Reporting a vulnerability

Please **do not** open a public GitHub issue for security-sensitive reports.

Prefer one of:

1. Email the maintainers (set a security contact in the repository settings / SECURITY contact when available).
2. Use GitHub **Private vulnerability reporting** if enabled on the repository.

Include:

- Description and impact
- Reproduction steps or PoC (non-destructive if possible)
- Affected versions / commit
- Whether a fix is already known

We aim to acknowledge reports within **7 days** and coordinate a fix and disclosure timeline.

## Safe harbor

Security research that follows this policy and avoids privacy violations, data destruction, and service disruption is appreciated. We will not pursue legal action for good-faith reports that comply with these guidelines.
