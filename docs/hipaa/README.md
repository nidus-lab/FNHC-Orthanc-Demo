# PACS Infrastructure HIPAA Documentation
[Home](README.md) | [Overview](system-overview.md) | [Data Flows](data-flows.md) | [Security Controls](security-controls.md) | [Risk Register](risk-register.md) | [Future Work](future-work.md)

This folder contains HIPAA-aligned documentation for the PACS infrastructure, focused on protecting PHI handled by Orthanc and the ChRIS platform.

- Audience: engineering, security, compliance
- Scope: assets and configs in this repo (`docker-compose.yml`, `Caddyfile`, `orthanc/`,  `configs/`)

## Contents
- [System Overview](system-overview.md) — System boundary, components, environments
- [Data Flows](data-flows.md) — PHI data flows and network trust zones
- [Security Controls](security-controls.md) — Implemented safeguards mapped to HIPAA Security Rule
- [Risk Register](risk-register.md) — Risks, attack vectors, impact, and mitigations
- [Future Work](future-work.md) — Prioritized improvements (incl. MFA for VPN, ChRIS, Orthanc)

## Executive Summary
- Orthanc is published at `orthanc.abfnhc.com` via Caddy and integrates with an authorization service and Keycloak. DICOM ingress is intended to occur over the WireGuard VPN (`wg-easy`) and internal DNS (`dnsmasq`).
- Caddy provides TLS termination and reverse proxy for public services.
- WireGuard (`wg-easy`) provides private network access; `dnsmasq` offers split-horizon DNS for PACS/Orthanc.

Key risks identified in this repository:
See `risk-register.md` and `future-work.md` for details and remediation.