import asyncio
import logging
import os
from typing import Dict, List

import httpx
import psycopg2
from fastapi import FastAPI, Response, status
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("health-service")

app = FastAPI(title="Orthanc Stack Health Service")

ORTHANC_URL = os.getenv("ORTHANC_URL", "http://orthanc:8042")
ORTHANC_USERNAME = os.getenv("ORTHANC_USERNAME", "share-user")
ORTHANC_PASSWORD = os.getenv("ORTHANC_PASSWORD", "")
AUTH_SERVICE_URL = os.getenv(
    "AUTH_SERVICE_URL", "http://orthanc-auth-service:8000"
)
TEST_STUDY_UID = os.getenv(
    "TEST_STUDY_UID", "1.3.46.670589.14.8100.181.198242.0.5.20200511091533.1.0"
)

DB_HOST = os.getenv("DB_HOST", "orthanc-db")
DB_NAME = os.getenv("DB_NAME", "orthanc")
DB_USER = os.getenv("DB_USER", "orthanc")
DB_PASS = os.getenv("DB_PASS", "")

KEYCLOAK_URL = os.getenv("KEYCLOAK_URL", "http://keycloak:8080/health/live")
KEYCLOAK_ALT_URL = os.getenv(
    "KEYCLOAK_ALT_URL", "http://keycloak:9000/health/live"
)


class HealthStatus(BaseModel):
    status: str
    details: Dict[str, str]


async def get_auth_service_token():
    """
    Attempts to get a token from the orthanc-auth-service.
    """
    if not ORTHANC_USERNAME or not ORTHANC_PASSWORD:
        logger.warning("ORTHANC_USERNAME or ORTHANC_PASSWORD not set")
        return None

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            payload = {
                "id": "health-check",
                "resources": [{"dicom-uid": TEST_STUDY_UID, "level": "study"}],
                "type": "stone-viewer-publication",
                "expiration-date": "2099-12-31T23:59:59Z",
            }
            logger.info(f"Requesting token from {AUTH_SERVICE_URL}")
            resp = await client.put(
                f"{AUTH_SERVICE_URL}/tokens/stone-viewer-publication",
                json=payload,
                auth=(ORTHANC_USERNAME, ORTHANC_PASSWORD),
            )
            if resp.status_code == 200:
                token = resp.json().get("token")
                logger.info("Successfully obtained token from auth service")
                return token
            else:
                logger.error(
                    f"Failed to get token from auth service: {resp.status_code} {resp.text}"
                )
                return None
    except Exception as e:
        logger.exception(f"Error getting token from auth service: {e}")
        return None


async def check_orthanc():
    try:
        # 1. Verify we can get a token from the auth service
        token = await get_auth_service_token()
        if not token:
            return "Error: Failed to get valid token from orthanc-auth-service"

        async with httpx.AsyncClient(timeout=5.0) as client:
            # 2. Check Orthanc system status using Basic Auth
            auth = (ORTHANC_USERNAME, ORTHANC_PASSWORD)
            logger.info(
                f"Checking Orthanc system status at {ORTHANC_URL}/system"
            )
            resp = await client.get(f"{ORTHANC_URL}/system", auth=auth)
            logger.info(f"Orthanc /system response: {resp.status_code}")

            if resp.status_code != 200:
                return (
                    f"Error: Orthanc returned {resp.status_code} for /system"
                )

            # 3. Deep check: try to access the specific study using the token
            # We use the DICOMweb endpoint which is what the viewer uses
            logger.info(f"Checking Orthanc study {TEST_STUDY_UID} with token")

            # The Authorization plugin expects the token in the 'api-key' header
            # as configured in Orthanc's TokenHttpHeaders
            resp = await client.get(
                f"{ORTHANC_URL}/dicom-web/studies/{TEST_STUDY_UID}",
                headers={"api-key": token},
            )
            logger.info(f"Orthanc study access response: {resp.status_code}")

            if resp.status_code == 200:
                return "OK"

            # If DICOMweb failed, try a standard Orthanc API call with the token
            # Some configurations might map the token to specific Orthanc resources
            resp = await client.get(
                f"{ORTHANC_URL}/tools/lookup",
                content=TEST_STUDY_UID,
                headers={"api-key": token},
            )
            logger.info(f"Orthanc lookup response: {resp.status_code}")

            if resp.status_code == 200:
                return "OK"

            return f"Error: Failed to access study with token (Status: {resp.status_code})"
    except Exception as e:
        logger.exception(f"Error checking Orthanc: {e}")
        return f"Error: {str(e)}"


def check_postgres():
    conn = None
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            connect_timeout=3,
        )
        cur = conn.cursor()
        cur.execute("SELECT 1")
        cur.fetchone()
        cur.close()
        return "OK"
    except Exception as e:
        logger.error(f"Postgres check failed: {e}")
        return f"Error: {str(e)}"
    finally:
        if conn:
            conn.close()


async def check_keycloak():
    for url in [KEYCLOAK_URL, KEYCLOAK_ALT_URL]:
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                resp = await client.get(url)
                if resp.status_code == 200:
                    return "OK"
        except Exception:
            continue
    return "Error: Keycloak health check failed on all endpoints"


@app.get("/health", response_model=HealthStatus)
async def health(response: Response):
    orthanc_status = await check_orthanc()
    db_status = check_postgres()
    keycloak_status = await check_keycloak()

    details = {
        "orthanc": orthanc_status,
        "postgres": db_status,
        "keycloak": keycloak_status,
    }

    overall_status = "UP"
    if any(v != "OK" for v in details.values()):
        overall_status = "DOWN"
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return HealthStatus(status=overall_status, details=details)


@app.get("/live")
async def live():
    return {"status": "alive"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
