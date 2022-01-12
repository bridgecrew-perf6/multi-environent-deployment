from aws_cdk import (
    CfnOutput,
    Stack,
    aws_ec2 as ec2,
    aws_iam as iam
)
from constructs import Construct


class CustomEC2Stack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        vpc = ec2.Vpc.from_lookup(self, "vpc", vpc_id="vpc-0d6a06a7f9fedb6a7")

        # Read Bootstrap Script
        with open("bootstrap_scripts/install_httpd.sh", mode="r") as file:
            user_data = file.read()

        web_server = ec2.Instance(self, "webServerId", 
                                  instance_type=ec2.InstanceType(instance_type_identifier="t2.nano"),
                                  instance_name="WebServer001", 
                                  machine_image=ec2.MachineImage.generic_linux({"ap-southeast-1": "ami-0356b1cd4aa0ee970"}), 
                                  vpc=vpc, 
                                  vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
                                  user_data=ec2.UserData.custom(user_data))

        output_1 = CfnOutput(self, "webServer001Ip", description="WebServer Public Ip Address", value=f"http://{web_server.instance_public_ip}")

        # Allow Web Traffic
        web_server.connections.allow_from_any_ipv4(ec2.Port.tcp(80), "Allow Web Traffic")

        # Add permission to web server instance profile
        web_server.role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSSMManagedInstanceCore")
        )
        web_server.role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3ReadOnlyAccess")
        )
