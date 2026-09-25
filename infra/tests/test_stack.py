"""公開範囲と永続データ保護を合成テンプレートで検査する。"""

from pathlib import Path

import aws_cdk as cdk
from aws_cdk.assertions import Annotations, Match, Template

from infra.stack import SlotKeeperStack


def test_serverless_and_authorization(tmp_path: Path) -> None:
    """Given 配布ZIP When synth Then 公開bucketと常設サーバーがなく認証と削除保護がある。"""
    app = cdk.App(outdir=str(tmp_path / "out"))
    stack = SlotKeeperStack(app, "Test")
    template = Template.from_stack(stack)
    template.has_resource_properties(
        "AWS::S3::Bucket",
        {
            "PublicAccessBlockConfiguration": {
                "BlockPublicAcls": True,
                "BlockPublicPolicy": True,
                "IgnorePublicAcls": True,
                "RestrictPublicBuckets": True,
            }
        },
    )
    template.has_resource_properties("AWS::DSQL::Cluster", {"DeletionProtectionEnabled": True})
    template.has_resource_properties(
        "AWS::ApiGatewayV2::Route",
        {
            "RouteKey": "ANY /{proxy+}",
            "AuthorizationType": "JWT",
            "AuthorizationScopes": ["openid"],
        },
    )
    template.has_resource_properties(
        "AWS::Lambda::Function", {"Runtime": "python3.12", "Timeout": 28}
    )
    assert not template.find_resources("AWS::EC2::Instance")
    assert not template.find_resources("AWS::EC2::NatGateway")
    resources = template.to_json()["Resources"]
    for resource in resources.values():
        if resource["Type"] in ("AWS::S3::Bucket", "AWS::DSQL::Cluster", "AWS::Cognito::UserPool"):
            assert resource["DeletionPolicy"] == "Retain"
    Annotations.from_stack(stack).has_no_error("*", Match.any_value())
