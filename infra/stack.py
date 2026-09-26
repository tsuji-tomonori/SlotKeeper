"""待機計算資源を持たないSlotKeeperの配信とAPIを構築する。"""

from pathlib import Path
from typing import cast

from aws_cdk import Aspects, CfnOutput, Duration, Environment, RemovalPolicy, Stack, Tags
from aws_cdk import aws_apigatewayv2 as apigw
from aws_cdk import aws_apigatewayv2_authorizers as authorizers
from aws_cdk import aws_apigatewayv2_integrations as integrations
from aws_cdk import aws_cloudfront as cf
from aws_cdk import aws_cloudfront_origins as origins
from aws_cdk import aws_cognito as cognito
from aws_cdk import aws_dsql as dsql
from aws_cdk import aws_iam as iam
from aws_cdk import aws_lambda as lambda_
from aws_cdk import aws_logs as logs
from aws_cdk import aws_s3 as s3
from cdk_nag import AwsSolutionsChecks, NagSuppressions
from constructs import Construct

from infra.config import EnvironmentConfig, load


class SlotKeeperStack(Stack):
    """S3/OAC、HTTP API、Lambda、Cognitoと単一リージョンDSQLを接続する。"""

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        *,
        asset_path: str = "artifacts/lambda.zip",
        config: EnvironmentConfig | None = None,
        env: Environment | None = None,
    ) -> None:
        super().__init__(scope, construct_id, termination_protection=True, env=env)
        config = config or load("dev")
        retention = {
            30: logs.RetentionDays.ONE_MONTH,
            90: logs.RetentionDays.THREE_MONTHS,
            180: logs.RetentionDays.SIX_MONTHS,
            365: logs.RetentionDays.ONE_YEAR,
        }[config.log_retention_days]
        Tags.of(self).add("Application", "SlotKeeper")
        Tags.of(self).add("Environment", config.name)
        bucket = s3.Bucket(
            self,
            "Web",
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            encryption=s3.BucketEncryption.S3_MANAGED,
            enforce_ssl=True,
            versioned=True,
            removal_policy=RemovalPolicy.RETAIN,
        )
        distribution = cf.Distribution(
            self,
            "Distribution",
            default_root_object="index.html",
            default_behavior=cf.BehaviorOptions(
                origin=origins.S3BucketOrigin.with_origin_access_control(bucket),
                viewer_protocol_policy=cf.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                response_headers_policy=cf.ResponseHeadersPolicy.SECURITY_HEADERS,
            ),
        )
        origin = "https://" + distribution.distribution_domain_name
        pool = cognito.UserPool(
            self,
            "Users",
            self_sign_up_enabled=False,
            sign_in_aliases=cognito.SignInAliases(email=True),
            removal_policy=RemovalPolicy.RETAIN,
            feature_plan=cognito.FeaturePlan.PLUS,
            standard_threat_protection_mode=cognito.StandardThreatProtectionMode.FULL_FUNCTION,
            password_policy=cognito.PasswordPolicy(
                min_length=12,
                require_lowercase=True,
                require_uppercase=True,
                require_digits=True,
                require_symbols=True,
            ),
        )
        domain = pool.add_domain(
            "Login",
            cognito_domain=cognito.CognitoDomainOptions(
                domain_prefix="slotkeeper-" + config.name + "-" + self.account
            ),
        )
        client = pool.add_client(
            "Browser",
            generate_secret=False,
            o_auth=cognito.OAuthSettings(
                flows=cognito.OAuthFlows(authorization_code_grant=True),
                scopes=[cognito.OAuthScope.OPENID, cognito.OAuthScope.PROFILE],
                callback_urls=[origin + "/"],
                logout_urls=[origin + "/"],
            ),
            prevent_user_existence_errors=True,
        )
        cognito.CfnUserPoolGroup(
            self, "Administrators", user_pool_id=pool.user_pool_id, group_name="admin"
        )
        cluster = dsql.CfnCluster(self, "Database", deletion_protection_enabled=True)
        cluster.apply_removal_policy(RemovalPolicy.RETAIN)
        log_group = logs.LogGroup(
            self,
            "ApiLogs",
            retention=retention,
            removal_policy=RemovalPolicy.RETAIN,
        )
        function = lambda_.Function(
            self,
            "Api",
            runtime=lambda_.Runtime.PYTHON_3_14,
            architecture=lambda_.Architecture.X86_64,
            handler="app.lambda_handler.handler",
            code=lambda_.Code.from_asset(str(Path(asset_path))),
            memory_size=config.lambda_memory_mb,
            timeout=Duration.seconds(config.lambda_timeout_seconds),
            log_group=log_group,
            environment={
                "SLOT_ENVIRONMENT": config.name,
                "SLOT_DATABASE_MODE": "dsql",
                "SLOT_DSQL_HOST": cluster.attr_endpoint,
                "SLOT_REGION": self.region,
                "SLOT_DATABASE_USER": "slotkeeper_app",
                "SLOT_ISSUER": pool.user_pool_provider_url,
                "SLOT_JWKS_URL": pool.user_pool_provider_url + "/.well-known/jwks.json",
                "SLOT_CLIENT_ID": client.user_pool_client_id,
                "SLOT_AUTH_MODE": "cognito",
                "SLOT_CORS_ORIGIN": origin,
            },
        )
        function.add_to_role_policy(
            iam.PolicyStatement(actions=["dsql:DbConnect"], resources=[cluster.attr_resource_arn])
        )
        api = apigw.HttpApi(
            self,
            "HttpApi",
            cors_preflight=apigw.CorsPreflightOptions(
                allow_origins=[origin],
                allow_methods=[
                    apigw.CorsHttpMethod.GET,
                    apigw.CorsHttpMethod.POST,
                    apigw.CorsHttpMethod.PUT,
                ],
                allow_headers=["Authorization", "Content-Type", "Idempotency-Key"],
                expose_headers=["X-Request-ID"],
            ),
        )
        access_logs = logs.LogGroup(
            self,
            "GatewayLogs",
            retention=retention,
            removal_policy=RemovalPolicy.RETAIN,
        )
        if api.default_stage:
            stage = api.default_stage.node.default_child
            if isinstance(stage, apigw.CfnStage):
                stage.default_route_settings = apigw.CfnStage.RouteSettingsProperty(
                    throttling_rate_limit=config.api_throttle_rate,
                    throttling_burst_limit=config.api_throttle_burst,
                )
                stage.access_log_settings = apigw.CfnStage.AccessLogSettingsProperty(
                    destination_arn=access_logs.log_group_arn,
                    format='{"requestId":"$context.requestId","routeKey":"$context.routeKey","status":"$context.status"}',
                )
        integration = integrations.HttpLambdaIntegration(
            "FastApi", cast(lambda_.IFunction, function)
        )
        authorizer = authorizers.HttpJwtAuthorizer(
            "Jwt", pool.user_pool_provider_url, jwt_audience=[client.user_pool_client_id]
        )
        health_routes = api.add_routes(
            path="/health", methods=[apigw.HttpMethod.GET], integration=integration
        )
        # OAuth scopeでaccess tokenを要求し、一般/管理者の区別は同じFastAPI境界で検査する。
        api.add_routes(
            path="/{proxy+}",
            methods=[apigw.HttpMethod.ANY],
            integration=integration,
            authorizer=authorizer,
            authorization_scopes=["openid"],
        )
        for route in health_routes:
            NagSuppressions.add_resource_suppressions(
                route,
                [
                    {
                        "id": "AwsSolutions-APIG4",
                        "reason": (
                            "healthは秘密もDB情報も返さない公開稼働確認。業務routeはJWTで保護する。"
                        ),
                    }
                ],
                apply_to_children=True,
            )
        CfnOutput(self, "WebBucket", value=bucket.bucket_name)
        CfnOutput(self, "DistributionId", value=distribution.distribution_id)
        CfnOutput(self, "WebUrl", value=origin)
        CfnOutput(self, "ApiUrl", value=api.api_endpoint)
        CfnOutput(self, "Issuer", value=pool.user_pool_provider_url)
        CfnOutput(self, "ClientId", value=client.user_pool_client_id)
        CfnOutput(self, "UserPoolId", value=pool.user_pool_id)
        CfnOutput(self, "LoginUrl", value=domain.base_url())
        CfnOutput(self, "DsqlEndpoint", value=cluster.attr_endpoint)
        CfnOutput(self, "ApplicationRole", value=function.role.role_arn if function.role else "")
        Aspects.of(self).add(AwsSolutionsChecks(verbose=True))
        NagSuppressions.add_resource_suppressions(
            bucket,
            [
                {
                    "id": "AwsSolutions-S1",
                    "reason": (
                        "静的公開アセット専用。個人情報を保存せず、アクセスログ用bucketの追加は運用"
                        "ADRで別判断する。"
                    ),
                }
            ],
        )
        NagSuppressions.add_resource_suppressions(
            distribution,
            [
                {
                    "id": "AwsSolutions-CFR1",
                    "reason": "単一拠点だが閲覧元の地理制限は要件にない。Cognitoで認可する。",
                },
                {
                    "id": "AwsSolutions-CFR2",
                    "reason": "初回の静的配信。WAFは必要な脅威と費用を運用時に判断する。",
                },
                {
                    "id": "AwsSolutions-CFR3",
                    "reason": "静的成果物のみ。PIIを含むアクセスログの永続化は初回要件外。",
                },
                {
                    "id": "AwsSolutions-CFR4",
                    "reason": (
                        "AWS既定ドメインの証明書を使用する指定に従う。独自証明書を作成しない。"
                    ),
                },
            ],
        )
        NagSuppressions.add_resource_suppressions(
            pool,
            [
                {
                    "id": "AwsSolutions-COG2",
                    "reason": (
                        "初回は管理者による利用者登録。MFA必須化は利用組織の運用設定として判断する"
                        "。"
                    ),
                }
            ],
        )
        NagSuppressions.add_resource_suppressions(
            function,
            [
                {
                    "id": "AwsSolutions-IAM4",
                    "reason": (
                        "Lambda基本ログ出力のAWS管理policy。DSQLは対象clusterのDbConnectだけに限定"
                        "する。"
                    ),
                },
                {
                    "id": "AwsSolutions-L1",
                    "reason": (
                        "配布ZIPとPython 3.14を一致させる固定runtime。互換性を確認して更新する。"
                    ),
                },
            ],
            apply_to_children=True,
        )
