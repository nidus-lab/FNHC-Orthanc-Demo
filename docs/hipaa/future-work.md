# Future Work (Prioritized)
[Home](README.md) | [Overview](system-overview.md) | [Data Flows](data-flows.md) | [Security Controls](security-controls.md) | [Risk Register](risk-register.md) | [Gap Analysis](gap-analysis.md) | [Future Work](future-work.md)

## Identity and MFA
- VPN (WireGuard / wg-easy)
  - Integrate UI auth with Keycloak OIDC and enforce MFA (TOTP/WebAuthn)
  - Alternatively, distribute client configs via out-of-band channel and enforce device certificates + per-user keys with rotation
- Orthanc
  - Continue using Keycloak for Orthanc Explorer 2; require MFA via realm policy
  - Ensure `orthanc-auth-service` tokens are short-lived and scoped

## Network and Transport
- Enforce DICOM over VPN only, or enable DICOM TLS on Orthanc and PACS peers
- Firewall rules to restrict DICOM ports to `wg` subnet; deny public ingress to DICOM
- Strengthen Caddy TLS (TLS 1.2/1.3 only, modern ciphers), HSTS, and security headers

## Secrets and Config
- Remove secrets from repo; use a vault and per-env `.env` templates from CI/CD
- Rotate all committed credentials (Postgres, Keycloak, Orthanc auth service)

## Platform Hardening
- Pin images with digests; add image signing/verification
- Host OS hardening: CIS baseline, auto security updates, minimal SSH surface

## Observability and Backups
- Centralized logs (Loki/ELK), metrics (Prometheus), alerts; retain audit logs per compliance
- Nightly encrypted backups for Orthanc data with periodic restore tests

## Process and Compliance
- Formalize incident response, change management, access reviews
- Business Associate Agreements for any vendor with PHI access