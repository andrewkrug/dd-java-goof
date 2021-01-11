#!/usr/bin/env python3

import os
from aws_cdk import core

from java_goof_ecs_construct.java_goof_ecs_construct_stack import CdkStack


app = core.App()
d = CdkStack(
    scope=app,
    construct_id="JavaGoofEcsConstruct",
    env={
        "account": os.environ["CDK_DEFAULT_ACCOUNT"],
        "region": os.environ["CDK_DEFAULT_REGION"],
    },
)

app.synth()
