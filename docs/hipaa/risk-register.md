# Risk Register and Attack Vectors
[Home](README.md) | [Overview](system-overview.md) | [Data Flows](data-flows.md) | [Security Controls](security-controls.md) | [Risk Register](risk-register.md) | [Gap Analysis](gap-analysis.md) | [Future Work](future-work.md)

The following risks are derived from the repository configuration. Severity reflects potential impact to confidentiality, integrity, availability (CIA) of PHI.

| ID | Risk / Attack Vector | Evidence | Impact | Likelihood | Current Mitigation | Status |
|----|----------------------|----------|--------|------------|--------------------|--------|
| R1 | Secrets are distributed via unmanaged `.env` files | `orthanc/docker-compose.yml` and supporting services pull credentials from `.env` that sits outside version control | Medium | Low | `.env` excluded from VCS and shared through admin channel | Monitoring |
| R2 | DICOM services operate without TLS | README configuration keeps `DicomTlsEnabled: false`; lack of TLS support across PACS/Orthanc peers makes remediation almost impossible today | Medium | Medium | WireGuard segmentation, ACLs, and host firewalls enforce private transport | Open |
| R3 | Lack of centralized logging/monitoring | No logging stack present | Medium | Medium | Container logs only | Open |
| R4 | Backups/DR not defined for Orthanc data volumes | No backup automation in repo | High | Medium | None | Open |

## Rationale: Why exposure is currently minimal in practice
- The most sensitive components (Orthanc DICOM ingress and PACS connectivity) are designed to operate over the WireGuard network with internal DNS, reducing public exposure of DICOM endpoints.
- However, internet-accessible endpoints (`orthanc`) exist; therefore strong auth, secrets management, and hardening are required before production use with PHI.

## Remediation Plan (high level)
- Introduce a managed secrets store (Vault, SOPS, etc.), keep `.env` generation automated, and rotate credentials periodically
- Continue to mandate WireGuard transport for DICOM until TLS-capable modalities become available; document compensating controls and monitor vendor roadmaps
- Implement centralized logging, alerting, and backups for all persistent volumes
