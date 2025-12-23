# System Overview and Boundary
[Home](README.md) | [Overview](system-overview.md) | [Data Flows](data-flows.md) | [Security Controls](security-controls.md) | [Risk Register](risk-register.md) | [Future Work](future-work.md)

## Environments
- Single host `???` (Caddy as reverse proxy)
- Docker Compose orchestrates services; includes Orthanc, Keycloak, Orthanc Auth Service, WireGuard (wg-easy) and dnsmasq

## Components (from repo)
- Reverse Proxy: `Caddy` (`Caddyfile`) publishes:
  - `orthanc.abfnhc.com` → 5002
  - `orthanc-auth.abfnhc.com` → 5003
  - `keycloak.abfnhc.com` → 5004
  - `vpn.abfnhc.com` → 5017 (wg-easy UI)
- Imaging Archive: `Orthanc` (`orthanc/docker-compose.yml`)
  - Uses Postgres (`orthanc-db`) for metadata/storage (compose snippet indicates Postgres integration)
  - Integrates Orthanc Explorer 2 + OHIF with Keycloak and `orthanc-auth-service`
  - DICOM ingress intended via VPN only due to lack of widespread DICOM TLS support
- AuthN/AuthZ: `Keycloak` and `orthanc-auth-service`
  - Keycloak realm `orthanc`, client `orthanc`
  - Orthanc Auth Service provides policy enforcement and tokenized shares
- Secure Network: `wg-easy` WireGuard and `dnsmasq`
  - WireGuard network `wg` (10.42.42.0/24, IPv6 enabled) with static IPs (e.g., Orthanc 10.42.42.3)
  - `dnsmasq` provides split-horizon DNS (e.g., `pacs.abfnhc.com` → 10.42.42.2, `pacs-direct.abfnhc.com` → 10.42.42.3)

## System Boundary
- In-scope: All services, data stores, networks, and configurations defined in this repo and host managed by the team.
- Out-of-scope: External services and data flows not defined here (e.g., external PACS outside VPN, cloud provider controls not managed by this repo, third-party SaaS).

## Trust Zones
- Public Zone: Caddy TLS endpoints `*.abfnhc.com` exposed to the Internet
- Private Zone: WireGuard network `wg` (10.42.42.0/24) for DICOM and admin access where possible
- Host Admin Zone: Docker host and `docker.sock` (must be restricted to admins)

## Data Classification
- PHI: DICOM images and metadata in Orthanc
- Confidential: Admin credentials, service tokens, VPN keys
- Public: Static site content and documentation

## User Roles and Access
### Admin User
- **Responsibilities**: System configuration, user management, and VPN administration.
- **Access Control**:
  - **WireGuard (VPN)**: Requires 2FA to establish a secure connection.
  - **Management**: Authorized to create and manage VPN accounts (via wg-easy) and application accounts in Keycloak.

### Basic User
- **Responsibilities**: Clinical data access and DICOM transmission.
- **Access Methods**:
  - **DICOMweb Protocol**: Used for sending/receiving DICOM data. This requires an active VPN connection to reach the Orthanc DICOMweb endpoints securely.
  - **Orthanc UI (Web)**: Accessed via browser for viewing studies. Authentication is handled by Keycloak, requiring either a third-party identity provider (e.g., GitHub, Google) or a 2FA-enabled username/password.
