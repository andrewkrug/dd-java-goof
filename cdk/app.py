#!/usr/bin/env python3

from aws_cdk import core

from java_goof_ecs_construct.java_goof_ecs_construct_stack import CdkStack


app = core.App()
CdkStack(app, "JavaGoofEcsConstruct")

app.synth()
