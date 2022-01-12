from aws_cdk import (
    CfnOutput,
    Stack,
    aws_ec2 as ec2,
    aws_iam as iam
)
from constructs import Construct


class CustomEC2Stack(Stack):

    def __init__(self, scope: Construct, construct_id: str, vpc, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Read Bootstrap Script
        with open("bootstrap_scripts/install_httpd.sh", mode="r") as file:
            user_data = file.read()

        # Get the latest Windows AMI
        windows_ami = ec2.MachineImage.latest_windows(
            version=ec2.WindowsVersion.WINDOWS_SERVER_2019_ENGLISH_FULL_BASE
        )

        # Get the latest Linux AMI
        amz_linux_ami = ec2.MachineImage.latest_amazon_linux(
            generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2,
            edition=ec2.AmazonLinuxEdition.STANDARD,
            storage=ec2.AmazonLinuxStorage.EBS,
            virtualization=ec2.AmazonLinuxVirt.HVM
        )

        web_server = ec2.Instance(self, "webServerId",
                                  instance_type=ec2.InstanceType(
                                      instance_type_identifier="t2.nano"),
                                  instance_name="WebServer001",
                                  machine_image=amz_linux_ami,
                                  vpc=vpc,
                                  vpc_subnets=ec2.SubnetSelection(
                                      subnet_type=ec2.SubnetType.PUBLIC),
                                  user_data=ec2.UserData.custom(user_data))

        # Add EBS with provisioned IOPS Storage
        web_server.instance.add_property_override("BlockDeviceMappings", [
            {
                "DeviceName": "/dev/sdb",
                "Ebs": {"VolumeSize": 8, "VolumeType": "io1", "Iops": 400, "DeleteOnTermination": True}
            }
        ])

        output_1 = CfnOutput(self, "webServer001Ip", description="WebServer Public Ip Address",
                             value=f"http://{web_server.instance_public_ip}")

        # Allow Web Traffic
        web_server.connections.allow_from_any_ipv4(
            ec2.Port.tcp(80), "Allow Web Traffic")

        # Add permission to web server instance profile
        web_server.role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name(
                "AmazonSSMManagedInstanceCore")
        )
        web_server.role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name(
                "AmazonS3ReadOnlyAccess")
        )
