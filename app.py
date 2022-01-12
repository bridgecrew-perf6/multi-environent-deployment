#!/usr/bin/env python3
import os

import aws_cdk as cdk

from resource_stacks.custom_vpc import CustomVpcStack

app = cdk.App()

CustomVpcStack(app, "my-custom-vpc-stack")

app.synth()
