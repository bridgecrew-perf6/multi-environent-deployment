#!/usr/bin/env python3
import os

import aws_cdk as cdk

from resource_stacks.custom_vpc import CustomVpcStack

app = cdk.App()

prod_configs = app.node.try_get_context('envs')['prod']
prod_env=cdk.Environment(region=prod_configs['region'], account=prod_configs['account'])

CustomVpcStack(app, "my-custom-vpc-stack", env=prod_env)

cdk.Tags.of(app).add("stack-team-support-email", prod_configs['stack-team-support-email'])
cdk.Tags.of(app).add("stack-level-tagging", "sample_tag_value")

app.synth()
