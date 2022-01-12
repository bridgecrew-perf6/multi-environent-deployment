from aws_cdk import (
    RemovalPolicy,
    Stack,
    aws_s3 as s3,
    aws_kms as kms
)
from constructs import Construct


class MultiEnvironentDeploymentStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, is_prod=False, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        my_key = kms.Key.from_key_arn(
            self, "myKeyId", self.node.try_get_context('envs')['prod']['kms_arn'])

        if is_prod:
            artifactBucket = s3.Bucket(self, "myProdArtifactBucketId-g025", versioned=True,
                                       encryption=s3.BucketEncryption.KMS, encryption_key=my_key, removal_policy=RemovalPolicy.RETAIN)
        else:
            artifactBucket = s3.Bucket(
                self, "myDevArtifactBucketId-g025", removal_policy=RemovalPolicy.DESTROY)
