#!/usr/bin/env python3
import os

import aws_cdk as cdk

from resource_stacks.custom_vpc import CustomVpcStack
from resource_stacks.custom_ec2 import CustomEC2Stack

app = cdk.App()

prod_configs = app.node.try_get_context('envs')['prod']
prod_env=cdk.Environment(region=prod_configs['region'], account=prod_configs['account'])

# Custom VPC Stack
vpc = CustomVpcStack(app, "my-custom-vpc-stack", env=prod_env)
cdk.Tags.of(app).add("stack-team-support-email", prod_configs['stack-team-support-email'])
cdk.Tags.of(app).add("stack-level-tagging", "sample_tag_value")

# Custom EC2 Stack
CustomEC2Stack(app, "my-custom-ec2-stack", vpc=vpc.custom_vpc, env=prod_env)

app.synth()
