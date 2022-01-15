from aws_cdk import (
    Stack,
    RemovalPolicy,
    CfnOutput,
    aws_s3 as s3,
    aws_s3_deployment as s3_deployment,
    aws_iam as iam,
    aws_cloudfront as cf,
    Aws
)
from constructs import Construct


class DeployCloudFrontOAIStaticSiteStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create an S3 Bucket
        static_site_assets_bkt = s3.Bucket(self,
                                           "static-site-assets-bkt",
                                           versioned=True,
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

        # Create OAI for CloudFront
        static_site_oai = cf.OriginAccessIdentity(
            self,  "static-site-oai",
            comment=f"OAI for static site from stack:{Aws.STACK_NAME}"
        )

        # Deploy CloudFront Configuration: Connecting OAI with static asset bucket
        cf_source_configuration = cf.SourceConfiguration(
            s3_origin_source=cf.S3OriginConfig(
                s3_bucket_source=static_site_assets_bkt,
                origin_access_identity=static_site_oai
            ),
            behaviors=[
                cf.Behavior(
                    is_default_behavior=True,
                    compress=True,
                    allowed_methods=cf.CloudFrontAllowedMethods.ALL,
                    cached_methods=cf.CloudFrontAllowedCachedMethods.GET_HEAD)
            ]
        )

        # Create CloudFront Distribution
        static_site_distribution = cf.CloudFrontWebDistribution(self,
                                                                "static-site-distribution",
                                                                comment="CDN for static website",
                                                                origin_configs=[
                                                                    cf_source_configuration],
                                                                price_class=cf.PriceClass.PRICE_CLASS_100)

        output_1 = CfnOutput(self,
                             "CloudFrontUrl",
                             description="The domain name of the static site",
                             value=f"{static_site_distribution.distribution_domain_name}")
