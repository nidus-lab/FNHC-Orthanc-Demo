# Security Controls Mapped to HIPAA Security Rule
[Home](README.md) | [Overview](system-overview.md) | [Data Flows](data-flows.md) | [Security Controls](security-controls.md) | [Risk Register](risk-register.md) | [Gap Analysis](gap-analysis.md) | [Future Work](future-work.md)

This section maps observed controls in this repo to HIPAA safeguards. It is not exhaustive and focuses on technical measures reflected in configuration.

## Technical Safeguards (selected)
- Access Control
  - Keycloak SSO for Orthanc Explorer 2 (configured via `orthanc/docker-compose.yml`), client `orthanc`, realm `orthanc`
  - Orthanc Authorization Service enforces fine-grained access and token sharing
  - WireGuard (`wg-easy`) restricts network access to internal services
- Audit Controls
  - Caddy can log access; Orthanc produce logs. Centralized log aggregation is not configured in this repo.
- Integrity
  - Docker images pinned to versions for repeatability
  - Database integrity depends on Postgres configuration; no checksums configured in repo
- Person or Entity Authentication
  - Keycloak provides user authentication for Orthanc UI
- Transmission Security
  - HTTPS via Caddy for public endpoints
  - DICOM ingress intended over WireGuard VPN

## Additional Controls
- Network Segmentation: WireGuard `wg` network and `dnsmasq` split-horizon DNS
- Reverse Proxy Hardening: Caddy with admin interface disabled

## Evidence (from this repo)
- `Caddyfile` exposes: `orthanc.abfnhcsystems.ca` → 5002, `vpn.abfnhcsystems.ca` → 5017
- `orthanc/docker-compose.yml` configures `OrthancExplorer2` + Keycloak and external `orthanc-auth-service`
- `docker-compose.yml` defines `wg-easy` with static addressing and DNS via `dnsmasq`