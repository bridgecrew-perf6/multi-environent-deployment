from aws_cdk import (
    Stack,
    CfnOutput,
    cloudformation_include,
    Fn
)
from constructs import Construct
import json


class StackFromCloudFormationTemplate(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        resource_from_cfn_template = cloudformation_include.CfnInclude(
            self, "ExistingInfra", template_file="stacks_from_cfn/sample_templates/create_s3_bucket_template.json")

        encrypted_bucket_arn = Fn.get_att("EncryptedS3Bucket", "Arn")

        # Output Arn of encrypted Bucket
        output_1 = CfnOutput(self, "EncryptedS3BucketArn",
                             value=f"{encrypted_bucket_arn.to_string()}")
