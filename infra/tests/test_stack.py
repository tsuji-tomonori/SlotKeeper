"""公開範囲・認証・権限・永続データ保護と環境設定の一致を合成テンプレートで検査する。"""

import json
from pathlib import Path
from typing import Any

import aws_cdk as cdk
import pytest
from aws_cdk.assertions import Annotations, Match, Template

from infra.config import load
from infra.stack import SlotKeeperStack


def synth(tmp_path: Path, name: str = "dev") -> tuple[SlotKeeperStack, Template]:
    config = load(name)
    app = cdk.App(outdir=str(tmp_path / ("out-" + name)))
    stack = SlotKeeperStack(
        app, "SlotKeeper-" + name, config=config, env=cdk.Environment(region=config.region)
    )
    return stack, Template.from_stack(stack)


def only(template: Template, kind: str) -> Any:
    found = template.find_resources(kind)
    assert len(found) == 1, kind
    return next(iter(found.values()))


def origin_join(template: Template) -> Any:
    """CloudFrontの既定ドメインから作るアプリ配信元の式。"""
    distribution = next(iter(template.find_resources("AWS::CloudFront::Distribution")))
    return {"Fn::Join": ["", ["https://", {"Fn::GetAtt": [distribution, "DomainName"]}]]}


def test_serverless_and_authorization(tmp_path: Path) -> None:
    """Given 配布ZIP When synth Then 公開bucketと常設サーバーがなく認証と削除保護がある。 [TECH-INFRA-AC]"""
    stack, template = synth(tmp_path)
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
        "AWS::Lambda::Function",
        {"Runtime": "python3.12", "Timeout": 28, "MemorySize": 1024, "Architectures": ["x86_64"]},
    )
    for kind in (
        "AWS::EC2::Instance",
        "AWS::EC2::NatGateway",
        "AWS::ECS::Service",
        "AWS::RDS::DBInstance",
    ):
        assert not template.find_resources(kind), kind
    resources = template.to_json()["Resources"]
    for resource in resources.values():
        if resource["Type"] in (
            "AWS::S3::Bucket",
            "AWS::DSQL::Cluster",
            "AWS::Cognito::UserPool",
            "AWS::Logs::LogGroup",
        ):
            assert resource["DeletionPolicy"] == "Retain", resource["Type"]
            assert resource["UpdateReplacePolicy"] == "Retain", resource["Type"]
    assert stack.termination_protection
    Annotations.from_stack(stack).has_no_error("*", Match.any_value())


def test_routes_are_protected(tmp_path: Path) -> None:
    """Given HTTP API When routeを列挙 Then healthだけ認証なしで、他はJWTとaccess scopeが必須。 [TECH-INFRA-AC]"""
    _, template = synth(tmp_path)
    routes = template.find_resources("AWS::ApiGatewayV2::Route")
    keys = {r["Properties"]["RouteKey"]: r["Properties"] for r in routes.values()}
    assert set(keys) == {"GET /health", "ANY /{proxy+}"}
    assert keys["GET /health"].get("AuthorizationType", "NONE") == "NONE"
    assert keys["ANY /{proxy+}"]["AuthorizationType"] == "JWT"
    assert keys["ANY /{proxy+}"]["AuthorizationScopes"] == ["openid"]
    authorizer = only(template, "AWS::ApiGatewayV2::Authorizer")["Properties"]
    client = next(iter(template.find_resources("AWS::Cognito::UserPoolClient")))
    assert authorizer["JwtConfiguration"]["Audience"] == [{"Ref": client}]


def test_origin_consistency(tmp_path: Path) -> None:
    """Given 環境設定 When synth Then CORS・Cognito callback/logout・API許可元が同じ配信元を指す。 [TECH-INFRA-AC]"""
    _, template = synth(tmp_path)
    origin = origin_join(template)
    api = only(template, "AWS::ApiGatewayV2::Api")["Properties"]["CorsConfiguration"]
    assert api["AllowOrigins"] == [origin]
    assert "Authorization" in api["AllowHeaders"] and "Idempotency-Key" in api["AllowHeaders"]
    assert "DELETE" not in api["AllowMethods"]
    client = only(template, "AWS::Cognito::UserPoolClient")["Properties"]
    callback = {"Fn::Join": ["", ["https://", origin["Fn::Join"][1][1], "/"]]}
    assert client["CallbackURLs"] == [callback]
    assert client["LogoutURLs"] == [callback]
    assert client["AllowedOAuthFlows"] == ["code"]
    assert client["GenerateSecret"] is False
    env = only(template, "AWS::Lambda::Function")["Properties"]["Environment"]["Variables"]
    assert env["SLOT_CORS_ORIGIN"] == origin
    assert env["SLOT_AUTH_MODE"] == "cognito"
    assert env["SLOT_DATABASE_MODE"] == "dsql"
    assert env["SLOT_ENVIRONMENT"] == "dev"
    assert not any("PASSWORD" in k or "SECRET" in k for k in env)


def test_least_privilege_and_private_bucket(tmp_path: Path) -> None:
    """Given 合成IAMとbucket policy When 権限を列挙 Then DSQLは対象clusterのDbConnectだけでS3はCloudFrontだけ読める。 [TECH-INFRA-AC]"""
    _, template = synth(tmp_path)
    statements = [
        s
        for policy in template.find_resources("AWS::IAM::Policy").values()
        for s in policy["Properties"]["PolicyDocument"]["Statement"]
    ]
    dsql = [s for s in statements if "dsql" in json.dumps(s["Action"])]
    cluster = next(iter(template.find_resources("AWS::DSQL::Cluster")))
    assert dsql == [
        {
            "Action": "dsql:DbConnect",
            "Effect": "Allow",
            "Resource": {"Fn::GetAtt": [cluster, "ResourceArn"]},
        }
    ]
    assert all(s["Resource"] != "*" for s in statements), statements
    policy = only(template, "AWS::S3::BucketPolicy")["Properties"]["PolicyDocument"]
    readers = [s for s in policy["Statement"] if s["Effect"] == "Allow"]
    assert len(readers) == 1
    assert readers[0]["Principal"] == {"Service": "cloudfront.amazonaws.com"}
    assert readers[0]["Action"] == "s3:GetObject"
    assert "AWS:SourceArn" in json.dumps(readers[0]["Condition"])


@pytest.mark.parametrize("name,days", [("dev", 30), ("prod", 365)])
def test_environment_settings(tmp_path: Path, name: str, days: int) -> None:
    """Given 環境context When synth Then ログ保持・throttle・環境名が設定どおりで削除保護は共通。 [TECH-INFRA-AC]"""
    config = load(name)
    _, template = synth(tmp_path, name)
    for group in template.find_resources("AWS::Logs::LogGroup").values():
        assert group["Properties"]["RetentionInDays"] == days
    stage = only(template, "AWS::ApiGatewayV2::Stage")["Properties"]
    assert stage["DefaultRouteSettings"]["ThrottlingRateLimit"] == config.api_throttle_rate
    assert stage["AccessLogSettings"]["Format"].count("$context") == 3
    template.has_resource_properties("AWS::DSQL::Cluster", {"DeletionProtectionEnabled": True})


@pytest.mark.parametrize("name", ["staging", "../dev", "Dev"])
def test_unknown_environment_rejected(name: str) -> None:
    """Given 未定義や不正な環境名 When 設定を読む Then 推測で合成せず拒否する。 [TECH-INFRA-AC]"""
    with pytest.raises(ValueError):
        load(name)
