from aws_cdk import (
    Stack,
    RemovalPolicy,
    aws_s3 as s3,
    aws_iam as iam,
)
from constructs import Construct


class CustomS3ResourcePolicyStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create an S3 Bucket
        g025_bucket = s3.Bucket(
            self, "g025-bucket", versioned=True, removal_policy=RemovalPolicy.DESTROY)

        # Add Bucket Resource Policy
        g025_bucket.add_to_resource_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "s3:GetObject",
                ],
                resources=[g025_bucket.arn_for_objects("*.html")],
                principals=[iam.AnyPrincipal()],
            )
        )

        g025_bucket.add_to_resource_policy(
            iam.PolicyStatement(
                effect=iam.Effect.DENY,
                actions=[
                    "s3:*",
                ],
                resources=[f"{g025_bucket.bucket_arn}"],
                principals=[iam.AnyPrincipal()],
                conditions={
                    "Bool": {"aws:SecureTransport": False}
                }
            )
        )
