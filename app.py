#!/usr/bin/env python3
import os

import aws_cdk as cdk

from resource_stacks.custom_vpc import CustomVpcStack
from resource_stacks.custom_ec2 import CustomEC2Stack
from resource_stacks.custom_parameters_secret import CustomParametersSecretStack
from resource_stacks.custom_iam import CustomIAMStack
from resource_stacks.custom_s3_resource_policy import CustomS3ResourcePolicyStack
from resource_stacks.custom_rds import CustomRDSStack
from stacks_from_cfn.stack_from_existing_cfn_template import StackFromCloudFormationTemplate
from resource_stacks.custom_sns import CustomSnsStack
from resource_stacks.custom_sqs import CustomSqsStack
from serverless_stacks.custom_lambda import CustomLambdaStack
from serverless_stacks.custom_lambda_from_s3 import CustomLambdaFromS3Stack
from serverless_stacks.custom_lambda_as_cron import CustomLambdaAsCronStack
from serverless_stacks.custom_dynamodb import CustomDynamoDBStack

app = cdk.App()

# prod_configs = app.node.try_get_context('envs')['prod']
# prod_env = cdk.Environment(
#     region=prod_configs['region'], account=prod_configs['account'])

# # Custom VPC Stack
# vpc = CustomVpcStack(app, "my-custom-vpc-stack", env=prod_env)
# cdk.Tags.of(app).add("stack-team-support-email",
#                      prod_configs['stack-team-support-email'])
# cdk.Tags.of(app).add("stack-level-tagging", "sample_tag_value")

# # Custom EC2 Stack
# app_stack = CustomEC2Stack(app, "my-custom-ec2-stack",
#                            vpc=vpc.custom_vpc, env=prod_env)

# # Custom SSM and Secrets
# CustomParametersSecretStack(app, "my-custom-parameters-secret-stack")

# # Custom IAM
# CustomIAMStack(app, "my-custom-iam-stack")

# # Custom S3 Resource Policy
# CustomS3ResourcePolicyStack(app, "my-custom-s3-resource-policy-stack")

# # Custom RDS
# db = CustomRDSStack(app, "my-custom-rds-stack", 
#                     vpc=vpc.custom_vpc,
#                     asg_security_groups=app_stack.web_server_asg.connections.security_groups, env=prod_env)

# # Import existing CloudFormation template
# StackFromCloudFormationTemplate(app, "my-stack-from-cloudformation-template")

# # Custom SNS
# CustomSnsStack(app, "my-custom-sns-stack")

# # Custom SQS
# CustomSqsStack(app, "my-custom-sqs-stack")

# # Custom Lambda
# CustomLambdaStack(app, "my-custom-lambda-stack")

# # Custom Lambda from S3
# CustomLambdaFromS3Stack(app, "my-custom-lambda-from-s3-stack")

# # Custom Lambda as Cron
# CustomLambdaAsCronStack(app, "my-custom-lambda-as-cron-stack")

# Custom DynamoDB
CustomDynamoDBStack(app, "my-custom-dynamodb-stack")

app.synth()
