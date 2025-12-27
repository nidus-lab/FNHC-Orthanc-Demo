# Future Work (Prioritized)
[Home](README.md) | [Overview](system-overview.md) | [Data Flows](data-flows.md) | [Security Controls](security-controls.md) | [Risk Register](risk-register.md) | [Gap Analysis](gap-analysis.md) | [Future Work](future-work.md)

## Network and Transport
- Enable DICOM TLS on Orthanc and PACS peers (lack of TLS support across PACS/Orthanc peers makes remediation almost impossible today)
- Firewall rules to restrict DICOM ports to `wg` subnet; deny public ingress to DICOM
- Strengthen Caddy TLS (TLS 1.2/1.3 only, modern ciphers), HSTS, and security headers

## Secrets and Config
- Rotate all committed credentials (Postgres, Keycloak, Orthanc auth service) with a vault instead of `.env`

## Platform Hardening
- Pin images with digests; add image signing/verification
- Host OS hardening: CIS baseline, auto security updates, minimal SSH surface

## Observability and Backups
- Centralized logs (Loki/ELK), metrics (Prometheus), alerts; retain audit logs per compliance
- Nightly encrypted backups for Orthanc data with periodic restore tests

## Process and Compliance
- Formalize incident response, change management, access reviews
- Business Associate Agreements for any vendor with PHI access

## Rollback Process
- Ability to automatically rollback on bad config