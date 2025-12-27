# Setup Guide

This guide provides step-by-step instructions for setting up the FNHC Orthanc Demo environment.

## Prerequisites

### 1. Network Configuration
Ensure the following ports are open on your firewall:
- **80/TCP**: HTTP (Caddy ACME challenge)
- **443/TCP**: HTTPS (Web interfaces)
- **51820/UDP**: WireGuard VPN
- **5017/TCP**: WireGuard UI (wg-easy)
- **4242/TCP**: DICOM (Orthanc)

### 2. Domain Setup
- Point your domains to the server's public IP.
- Required domains (as configured in `Caddyfile`):
  - `orthanc.abfnhcsystems.ca`
  - `orthanc-auth.abfnhcsystems.ca`
  - `keycloak.abfnhcsystems.ca`
  - `vpn.abfnhcsystems.ca`
  - `health.abfnhcsystems.ca`
- `pacs-direct.abfnhcsystems.ca` for sending dicoms through Exo, Philips Lumify etc

### 3. Docker Installation
Install the Docker engine and verify the installation:
```bash
sudo docker compose version
```

## Installation Steps

### 1. Environment Configuration
Create a `.env` file from the example and fill in the required tokens (except `ORTHANC_AUTH_SERVICE_KEYCLOAK_CLIENT_SECRET` which we will do later). Avoid using special characters in passwords to prevent parsing issues.

```bash
cp .env.example .env
nano .env
```

### 2. Network Setup
Create the external Docker network required by the services:
```bash
sudo docker network create minichris-local
```

### 3. Storage Preparation
Create the required Docker volumes for Orthanc data. These are configured as external volumes in `orthanc/docker-compose.yml`.
```bash
sudo docker volume create --name orthanc_dicom_data
sudo docker volume create --name orthanc_dicom_data_named
```

If you want the data in an easy to find location, you can adapt the above command to this one:
```bash
sudo docker volume create \
  --name MY_DICOM_VOLUME_NAME \
  --driver local \
  --opt type=none \
  --opt o=bind \
  --opt device=/storage/MY_DICOM_VOLUME_NAME
```

### 4. Launch Services
Start the essential services (Caddy, VPN Services) and the Orthanc stack:
```bash
sudo docker compose --profile essential --profile orthanc up -d
```

## Service Configuration

### 1. VPN Setup
1. Access the WireGuard UI at `https://vpn.abfnhcsystems.ca`.
2. Setup Admin Account, configure DNS to DNSMASQ (10.42.42.43), setup 2FA
3. Create a new client account.
4. Download the configuration file or scan the QR code.
5. Install the WireGuard client on your device and connect.

### 2. Keycloak Initialization
1. Check the Keycloak logs to retrieve the initial setup token or client secrets if automated:
   ```bash
   sudo docker compose logs keycloak
   ```
2. Access Keycloak at `https://keycloak.abfnhcsystems.ca`.
3. Log in with the admin credentials defined in your `.env` file (admin and `KEYCLOAK_ADMIN_PASSWORD`).
4. **Realm Setup**:
   - Create or configure the `orthanc` realm.
   - Set up users and assign roles (`doctor`, `admin`).
   - Enforce OTP (One-Time Password) and password reset on first login for new users.

More information for keycloak is here: https://www.keycloak.org/documentation

### 3. Orthanc Authentication
After configuring Keycloak, you may need to restart the authentication service to pick up new client secrets:
```bash
sudo docker compose up -d orthanc-auth-service
```
(Since we are resetting an env var, we need to use `up` not `restart`)

## Verification

### 1. DICOM Connectivity
1. Log in to the Orthanc UI at `https://orthanc.abfnhcsystems.ca`.
2. Upload the `example/dicom_upload.dcm` DICOM file to test storage and indexing.
3. Verify that the Stone Web Viewer is functional (eye icon).

### 2. Health Check
Access the health service at `https://health.abfnhcsystems.ca/health` to verify that all components (Orthanc, Keycloak, DB) are communicating correctly.

### 3. Mobile Integration
1. Install **Philips Lumify** and **WireGuard** on your mobile device.
2. Connect to the VPN using the profile created in the VPN Setup step.
3. Test DICOM image transmission from the mobile device to the Orthanc server.

Details for PACS dicom connections:
AET-Local: `FHNC1`
AET-Remote: `FHNC`
Host: `pacs-direct.abfnhcsystems.ca`
Port: `4242`
