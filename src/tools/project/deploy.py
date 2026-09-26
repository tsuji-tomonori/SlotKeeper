"""CDK出力から公開設定と配信をつなぐ明示実行専用ツール。"""

from __future__ import annotations

import argparse
import contextlib
import json
import mimetypes
from datetime import UTC, datetime
from pathlib import Path
from typing import cast

from boto3.session import Session
from botocore.config import Config
from mypy_boto3_cloudfront import CloudFrontClient
from mypy_boto3_cognito_idp import CognitoIdentityProviderClient
from mypy_boto3_s3 import S3Client


def publish(outputs: dict[str, str], root: Path) -> None:
    """既存アセットを削除せずS3へ配置し、設定と入口のキャッシュを更新する。"""
    s3 = cast(
        S3Client,
        Session().client(
            "s3",
            config=Config(
                retries={"total_max_attempts": 3, "mode": "standard"},
                connect_timeout=5,
                read_timeout=30,
            ),
        ),
    )
    cloudfront = cast(
        CloudFrontClient,
        Session().client(
            "cloudfront",
            config=Config(
                retries={"total_max_attempts": 3, "mode": "standard"},
                connect_timeout=5,
                read_timeout=30,
            ),
        ),
    )
    config = {
        "api": outputs["ApiUrl"],
        "authority": outputs["Issuer"],
        "clientId": outputs["ClientId"],
        "authMode": "cognito",
        "logoutUrl": outputs["LoginUrl"] + "/logout",
    }
    (root / "config.json").write_text(json.dumps(config) + "\n")
    for path in sorted(root.rglob("*")):
        if path.is_file():
            key = path.relative_to(root).as_posix()
            s3.upload_file(
                str(path),
                outputs["WebBucket"],
                key,
                ExtraArgs={
                    "ContentType": mimetypes.guess_type(key)[0] or "application/octet-stream",
                    "CacheControl": "public,max-age=31536000,immutable"
                    if key.startswith("_astro/")
                    else "no-cache",
                },
            )
    cloudfront.create_invalidation(
        DistributionId=outputs["DistributionId"],
        InvalidationBatch={
            "Paths": {"Quantity": 2, "Items": ["/", "/config.json"]},
            "CallerReference": datetime.now(UTC).isoformat(),
        },
    )


def main() -> None:
    """生成済みCDK出力と明示操作があるときだけ外部を書き換える。"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--outputs", required=True)
    parser.add_argument("--publish", action="store_true")
    parser.add_argument("--admin-email")
    parser.add_argument("--stack", default="SlotKeeper-dev")
    args = parser.parse_args()
    data = json.loads(Path(args.outputs).read_text())
    outputs = cast(dict[str, str], data[args.stack])
    if args.publish:
        publish(outputs, Path("frontend/dist"))
    if args.admin_email:
        client = cast(
            CognitoIdentityProviderClient,
            Session().client(
                "cognito-idp",
                config=Config(
                    retries={"total_max_attempts": 3, "mode": "standard"},
                    connect_timeout=5,
                    read_timeout=30,
                ),
            ),
        )
        with contextlib.suppress(client.exceptions.UsernameExistsException):
            client.admin_create_user(
                UserPoolId=outputs["UserPoolId"],
                Username=args.admin_email,
                UserAttributes=[{"Name": "email", "Value": args.admin_email}],
                DesiredDeliveryMediums=["EMAIL"],
            )
        client.admin_add_user_to_group(
            UserPoolId=outputs["UserPoolId"], Username=args.admin_email, GroupName="admin"
        )


if __name__ == "__main__":
    main()
