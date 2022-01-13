#!/usr/bin/env python3
import os

import aws_cdk as cdk

from resource_stacks.custom_vpc import CustomVpcStack
from resource_stacks.custom_ec2 import CustomEC2Stack
from resource_stacks.custom_parameters_secret import CustomParametersSecretStack
from resource_stacks.custom_iam import CustomIAMStack
from resource_stacks.custom_s3_resource_policy import CustomS3ResourcePolicyStack

app = cdk.App()

prod_configs = app.node.try_get_context('envs')['prod']
prod_env=cdk.Environment(region=prod_configs['region'], account=prod_configs['account'])

# Custom VPC Stack
# vpc = CustomVpcStack(app, "my-custom-vpc-stack", env=prod_env)
# cdk.Tags.of(app).add("stack-team-support-email", prod_configs['stack-team-support-email'])
# cdk.Tags.of(app).add("stack-level-tagging", "sample_tag_value")

# # Custom EC2 Stack
# CustomEC2Stack(app, "my-custom-ec2-stack", vpc=vpc.custom_vpc, env=prod_env)

# # Custom SSM and Secrets
# CustomParametersSecretStack(app, "my-custom-parameters-secret-stack")

# # Custom IAM
# CustomIAMStack(app, "my-custom-iam-stack")

# Custom S3 Resource Policy
CustomS3ResourcePolicyStack(app, "my-custom-s3-resource-policy-stack")

app.synth()
