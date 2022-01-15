from aws_cdk import (
    Stack,
    Duration,
    aws_lambda as lambdaFunction,
    aws_s3 as s3,
    aws_logs as logs,
    RemovalPolicy
)
from constructs import Construct


class CustomLambdaFromS3Stack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Import an S3 Bucket
        g025_bucket = s3.Bucket.from_bucket_name(
            self, "g025-bucket", bucket_name="lambda-src-g025")

        # Create function with source code from S3 Bucket
        g025_fn = lambdaFunction.Function(self,
                                          "g025-fn",
                                          function_name="g025-fn-s3",
                                          runtime=lambdaFunction.Runtime.PYTHON_3_8,
                                          handler="g025_processor.lambda_handler",
                                          code=lambdaFunction.S3Code(
                                              bucket=g025_bucket, 
                                              key="g025_processor.zip"),
                                            timeout=Duration.seconds(12),
                                            reserved_concurrent_executions=1
                                          )
        
        # Create Custom Log Group
        # /aws/lambda/g025-fn-s3
        g025_lg = logs.LogGroup(
            self, "g025LogGroup", 
            log_group_name=f"/aws/lambda/{g025_fn.function_name}", 
            removal_policy=RemovalPolicy.DESTROY)
