"""AWSへのlookupを行わずCloudFormationを合成する。`-c env=dev|prod`で環境を選ぶ。"""

import aws_cdk as cdk

from infra.config import load
from infra.stack import SlotKeeperStack

app = cdk.App()
config = load(str(app.node.try_get_context("env") or "dev"))
SlotKeeperStack(
    app,
    "SlotKeeper-" + config.name,
    config=config,
    env=cdk.Environment(region=config.region),
)
app.synth()
