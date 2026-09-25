"""明示指定されたAWS URLだけを検査し、ローカル成功と区別する。"""

import json
import os
from pathlib import Path

import httpx


def main() -> None:
    """healthとJWT境界を実AWSで確認する。書込み試験は別途合成資源を指定する。"""
    url = os.environ.get("SLOT_CLOUD_API", "")
    token = os.environ.get("SLOT_CLOUD_TOKEN", "")
    if not url.startswith("https://") or not token:
        raise SystemExit("実AWS URLとaccess tokenの明示指定が必要")
    with httpx.Client(timeout=30) as client:
        health = client.get(url + "/health")
        anonymous = client.get(url + "/resources")
        authenticated = client.get(url + "/resources", headers={"Authorization": "Bearer " + token})
    results = {
        "health": health.status_code,
        "anonymous": anonymous.status_code,
        "authenticated": authenticated.status_code,
        "scope": "cloud-read-and-auth-only",
        "occ": "not-run",
    }
    Path("artifacts").mkdir(exist_ok=True)
    Path("artifacts/cloud.json").write_text(json.dumps(results, indent=2) + "\n")
    if (health.status_code, anonymous.status_code, authenticated.status_code) != (200, 401, 200):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
