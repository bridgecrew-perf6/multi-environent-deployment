from aws_cdk import (
    Stack,
    Tags,
    aws_ec2 as ec2,
    aws_s3 as s3,
    CfnOutput
)
from constructs import Construct


class CustomVpcStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        prod_configs = self.node.try_get_context('envs')['prod']

        self.custom_vpc = ec2.Vpc(
            self, "customVpcId",
            cidr=prod_configs['vpc_configs']['vpc_cidr'],
            max_azs=2,
            nat_gateways=1,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="publicSubnet",
                    cidr_mask=prod_configs['vpc_configs']['cidr_mask'],
                    subnet_type=ec2.SubnetType.PUBLIC),
                ec2.SubnetConfiguration(
                    name="privateSubnet",
                    cidr_mask=prod_configs['vpc_configs']['cidr_mask'],
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_NAT),
                ec2.SubnetConfiguration(
                    name="dbSubnet",
                    cidr_mask=prod_configs['vpc_configs']['cidr_mask'],
                    subnet_type=ec2.SubnetType.PRIVATE_ISOLATED)
            ])

        my_bucket = s3.Bucket(self, "customBucketId-g025")

        Tags.of(self.custom_vpc).add("Owner", "g025Vpc")
        Tags.of(my_bucket).add("Owner", "g025Vpc")

        # Resource in same account.
        bucket1 = s3.Bucket.from_bucket_name(
            self, "generalman025-s3-inventory", "generalman025-s3-inventory")

        bucket2 = s3.Bucket.from_bucket_arn(
            self, "thebucket", "arn:aws:s3:::thebucketofgeneralman025")

        CfnOutput(self, "generalman025-s3-inventoryId",
                  value=bucket1.bucket_name, export_name="generalman025-s3-inventory")

        # Existing VPC = vpc-08c8ec9e921deff16
        vpc2 = ec2.Vpc.from_lookup(
            self, "vpc2", vpc_id="vpc-08c8ec9e921deff16")

        peer_vpc = ec2.CfnVPCPeeringConnection(
            self, "peerVpc", peer_vpc_id=self.custom_vpc.vpc_id, vpc_id=vpc2.vpc_id)
        
        CfnOutput(self, "customVpcOutput",
                  value=self.custom_vpc.vpc_id, export_name="VpcId")
