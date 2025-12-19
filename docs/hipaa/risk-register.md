# Risk Register and Attack Vectors
[Home](README.md) | [Overview](system-overview.md) | [Data Flows](data-flows.md) | [Security Controls](security-controls.md) | [Risk Register](risk-register.md) | [Gap Analysis](gap-analysis.md) | [Future Work](future-work.md)

The following risks are derived from the repository configuration. Severity reflects potential impact to confidentiality, integrity, availability (CIA) of PHI.

| ID | Risk / Attack Vector | Evidence | Impact | Likelihood | Current Mitigation | Status |
|----|----------------------|----------|--------|------------|--------------------|--------|
| R1 | Secrets in version control (cleartext credentials) | `orthanc/docker-compose.yml` env | High | Medium | None in repo | Open |
| R2 | DICOM TLS disabled; reliance on VPN only | `README.md` DICOM TLS example has `DicomTlsEnabled: false` | High | Medium | WireGuard segmentation | Open |
| R5 | Lack of centralized logging/monitoring | No logging stack present | Medium | Medium | Container logs only | Open |
| R6 | Weak password policies / No MFA for VPN/Orthanc | No enforced MFA in configs | High | Medium | Keycloak present but MFA not configured | Open |
| R7 | Backups/DR not defined for Orthanc data volumes | No backup automation in repo | High | Medium | None | Open |

## Rationale: Why exposure is currently minimal in practice
- The most sensitive components (Orthanc DICOM ingress and PACS connectivity) are designed to operate over the WireGuard network with internal DNS, reducing public exposure of DICOM endpoints.
- However, internet-accessible endpoints (`orthanc`) exist; therefore strong auth, secrets management, and hardening are required before production use with PHI.

## Remediation Plan (high level)
- Migrate secrets to a vault or `.env` files excluded from VCS; rotate all credentials
- Enforce MFA on VPN and Orthanc (via Keycloak policies)
- Enable DICOM TLS or enforce VPN-only ACLs with firewall rules
- Implement centralized logging, alerting, and backups for all persistent volumes