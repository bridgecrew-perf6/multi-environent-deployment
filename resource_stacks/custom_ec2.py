from aws_cdk import (
    Fn,
    Stack,
    aws_ec2 as ec2
)
from constructs import Construct


class CustomEC2Stack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        vpc = ec2.Vpc.from_lookup(self, "vpc", vpc_id="vpc-0d6a06a7f9fedb6a7")

        web_server = ec2.Instance(self, "webServerId", 
                                  instance_type=ec2.InstanceType(instance_type_identifier="t2.nano"),
                                  instance_name="WebServer001", 
                                  machine_image=ec2.AmazonLinuxImage(), 
                                  vpc=vpc, 
                                  vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC))
