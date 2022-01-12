from aws_cdk import (
    Fn,
    Stack,
    aws_ec2 as ec2
)
from constructs import Construct


class CustomEC2Stack(Stack):

    def __init__(self, scope: Construct, construct_id: str, vpc, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        web_server = ec2.Instance(self, "webServerId", 
                                  instance_type=ec2.InstanceType(instance_type_identifier="t2.nano"),
                                  instance_name="WebServer001", 
                                  machine_image=ec2.AmazonLinuxImage(), 
                                  vpc=vpc, 
                                  vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC))
