from aws_cdk import (
    Stack,
    RemovalPolicy,
    aws_s3 as s3, 
    aws_s3_deployment as s3_deployment,
    aws_iam as iam,
)
from constructs import Construct


class DeployStaticSiteStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create an S3 Bucket
        static_site_assets_bkt = s3.Bucket(self,
                                           "static-site-assets-bkt",
                                           versioned=True,
                                           public_read_access=True,
                                           website_index_document="index.html",
                                           website_error_document="error.html",
                                           removal_policy=RemovalPolicy.DESTROY, 
                                           auto_delete_objects=True
                                           )

        # Add assets to static site bucket
        add_assets_to_site = s3_deployment.BucketDeployment(
            self, "add-assets-to-site",
            sources=[s3_deployment.Source.asset("use_cases/static_assets")],
            destination_bucket=static_site_assets_bkt
        )