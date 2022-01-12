from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    CfnOutput
)
from constructs import Construct


class CustomVpcStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        prod_configs = self.node.try_get_context('envs')['prod']

        custom_vpc = ec2.Vpc(
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
        
        CfnOutput(self, "customVpcOutput", value=custom_vpc.vpc_id, export_name="customVpcId")
