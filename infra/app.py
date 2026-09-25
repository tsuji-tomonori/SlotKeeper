"""AWSへのlookupを行わずCloudFormationを合成する。"""

import aws_cdk as cdk

from infra.stack import SlotKeeperStack

app = cdk.App()
SlotKeeperStack(app, "SlotKeeper")
app.synth()
