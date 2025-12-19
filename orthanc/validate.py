#!/usr/bin/env python3
"""
Orthanc Test & Config Validator

This script does two things:
1. Validates the JSON configuration values (ORTHANC_JSON and ORTHANC__DICOM_MODALITIES)
   from orthanc/docker-compose.yml.
2. Spins up a temporary Orthanc test container (with overrides) to check if it starts
   successfully without requiring Keycloak.

Usage:
    python3 validate_orthanc.py
"""

import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import yaml

BASE_COMPOSE = "./orthanc/docker-compose.yml"


# -------------------------------
# JSON VALIDATION FUNCTIONS
# -------------------------------
def extract_orthanc_configs_from_compose():
    """Extract the ORTHANC_JSON and ORTHANC__DICOM_MODALITIES values from docker-compose.yml"""
    compose_file = Path(BASE_COMPOSE)

    if not compose_file.exists():
        print("❌ Error: docker-compose.yml not found at", BASE_COMPOSE)
        return None, None

    try:
        with open(compose_file, "r") as f:
            compose_data = yaml.safe_load(f)

        environment = compose_data["services"]["orthanc"]["environment"]

        orthanc_json = environment.get("ORTHANC_JSON")
        dicom_modalities = environment.get("ORTHANC__DICOM_MODALITIES")

        return orthanc_json, dicom_modalities
    except KeyError as e:
        print(
            f"❌ Error: Could not find required environment variables in docker-compose.yml: {e}"
        )
        return None, None
    except yaml.YAMLError as e:
        print(f"❌ Error: Invalid YAML in docker-compose.yml: {e}")
        return None, None


def validate_json_with_comments(json_str):
    """Validate JSON string that may contain // comments"""
    lines = json_str.split("\n")
    clean_lines = []

    for line in lines:
        comment_pos = line.find("//")
        if comment_pos != -1:
            quotes_before = line[:comment_pos].count('"')
            if quotes_before % 2 == 0:
                line = line[:comment_pos]
        clean_lines.append(line)

    clean_json = "\n".join(clean_lines)

    try:
        parsed = json.loads(clean_json)
        return True, parsed, None
    except json.JSONDecodeError as e:
        return False, None, str(e)


def validate_configs():
    """Validate Orthanc JSON configs from docker-compose.yml"""
    print("🔍 Validating Orthanc JSON configurations...")

    orthanc_json, dicom_modalities = extract_orthanc_configs_from_compose()
    if orthanc_json is None and dicom_modalities is None:
        sys.exit(1)

    all_valid = True

    if orthanc_json:
        print("\n📋 Validating ORTHANC_JSON...")
        is_valid, _, error = validate_json_with_comments(orthanc_json)
        if is_valid:
            print("✅ ORTHANC_JSON is valid!")
        else:
            print("❌ ORTHANC_JSON is invalid!")
            print(f"   Error: {error}")
            all_valid = False
    else:
        print("⚠️  ORTHANC_JSON not found in docker-compose.yml")

    if dicom_modalities:
        print("\n🏥 Validating ORTHANC__DICOM_MODALITIES...")
        is_valid, parsed_modalities, error = validate_json_with_comments(
            dicom_modalities
        )
        if is_valid:
            print("✅ ORTHANC__DICOM_MODALITIES is valid!")
            if isinstance(parsed_modalities, dict):
                modality_names = list(parsed_modalities.keys())
                print(
                    f"   📡 Found {len(modality_names)} DICOM modalities: {', '.join(modality_names)}"
                )
        else:
            print("❌ ORTHANC__DICOM_MODALITIES is invalid!")
            print(f"   Error: {error}")
            all_valid = False
    else:
        print("⚠️  ORTHANC__DICOM_MODALITIES not found in docker-compose.yml")

    if not all_valid:
        sys.exit(1)
    else:
        print("\n🎉 All JSON configurations are valid!")


# -------------------------------
# ORTHANC TEST CONTAINER FUNCTIONS
# -------------------------------
def run_orthanc_test():
    """Spin up a temporary Orthanc test container and check if it starts"""
    with open(BASE_COMPOSE, "r") as f:
        base = yaml.safe_load(f)

    orthanc_service = base["services"]["orthanc"].copy()

    # Modify for test
    orthanc_service["restart"] = "no"
    orthanc_service["container_name"] = "orthanc_test"
    orthanc_service["ports"] = ["49152:8042"]

    if "networks" in orthanc_service:
        orthanc_service["networks"] = {
            k: v
            for k, v in orthanc_service["networks"].items()
            if k == "minichris-local"
        }

    orthanc_service.pop("depends_on", None)

    override = {
        "services": {"orthanc_test": orthanc_service},
        "networks": {"minichris-local": {"external": True}},
    }

    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".yml",
        delete=False,
        dir=os.path.dirname(BASE_COMPOSE),
    ) as tmpfile:
        yaml.dump(override, tmpfile, default_flow_style=False)
        override_file = tmpfile.name

    print(f"\n📝 Created temporary override file at {override_file}")

    try:
        print("🚀 Starting Orthanc test container...")
        subprocess.run(
            [
                "sudo",
                "docker",
                "compose",
                "-f",
                override_file,
                "up",
                "-d",
                "orthanc_test",
            ],
            check=True,
        )

        print("⏳ Waiting for Orthanc to start or stop...")

        started = False
        stopped = False
        timeout = 120
        interval = 3
        elapsed = 0

        while elapsed < timeout and not (started or stopped):
            result = subprocess.run(
                [
                    "sudo",
                    "docker",
                    "ps",
                    "--filter",
                    "name=orthanc_test",
                    "--format",
                    "{{.Status}}",
                ],
                capture_output=True,
                text=True,
            )
            status = result.stdout.strip()

            if not status:
                stopped = True
                break

            logs = subprocess.run(
                ["sudo", "docker", "logs", "orthanc_test"],
                capture_output=True,
                text=True,
            )
            log_output = logs.stdout + logs.stderr

            if "Orthanc has started" in log_output:
                started = True
                break

            if "Orthanc has stopped" in log_output:
                stopped = True
                break

            time.sleep(interval)
            elapsed += interval

        logs = subprocess.run(
            ["sudo", "docker", "logs", "orthanc_test"],
            capture_output=True,
            text=True,
        )
        log_output = logs.stdout + logs.stderr

        if started:
            print(
                "✅ Orthanc has started successfully inside the container 🎉"
            )
        elif stopped:
            print("❌ orthanc_test container stopped unexpectedly 💥")
            print("📜 Logs:\n")
            print(log_output)
        else:
            print(
                "⏰ Timeout: Orthanc did not start within the timeout period ⚠️"
            )
            print("📜 Logs:\n")
            print(log_output)

    finally:
        print("\n🧹 Cleaning up test container and override file...")
        subprocess.run(
            [
                "sudo",
                "docker",
                "compose",
                "-f",
                override_file,
                "down",
                "orthanc_test",
            ]
        )
        os.remove(override_file)
        print("✅ Cleanup complete")


# -------------------------------
# MAIN
# -------------------------------
def main():
    validate_configs()
    print("\n🔧 Running Orthanc test container check...")
    run_orthanc_test()


if __name__ == "__main__":
    main()
