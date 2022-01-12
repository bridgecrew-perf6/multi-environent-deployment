from aws_cdk import (
    CfnOutput,
    Stack,
    aws_ec2 as ec2,
    aws_elasticloadbalancingv2 as elbv2,
    aws_iam as iam,
    aws_autoscaling as autoscaling,
)
from constructs import Construct


class CustomEC2Stack(Stack):

    def __init__(self, scope: Construct, construct_id: str, vpc, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Read Bootstrap Script
        with open("bootstrap_scripts/install_httpd.sh", mode="r") as file:
            user_data = file.read()

        # Get the latest Linux AMI
        amz_linux_ami = ec2.MachineImage.latest_amazon_linux(
            generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2,
            edition=ec2.AmazonLinuxEdition.STANDARD,
            storage=ec2.AmazonLinuxStorage.GENERAL_PURPOSE,
            virtualization=ec2.AmazonLinuxVirt.HVM
        )

        # Create Application Load Balancer
        alb = elbv2.ApplicationLoadBalancer(
            self, "myAlbId", vpc=vpc, internet_facing=True, load_balancer_name="WebServerAlb"
        )

        # Allow ALB to receive internet traffic
        alb.connections.allow_from_any_ipv4(
            ec2.Port.tcp(80),
            description="Allow Internet access on ALB port 80"
        )

        # Add Listener to ALB
        listener = alb.add_listener(
            "listenerId",
            port=80,
            open=True,
        )

        # Webserver IAM Role
        web_server_role = iam.Role(self, "WebServerRole", assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
                                   managed_policies=[
            iam.ManagedPolicy.from_aws_managed_policy_name(
                "AmazonSSMManagedInstanceCore"),
            iam.ManagedPolicy.from_aws_managed_policy_name(
                "AmazonS3ReadOnlyAccess"),
        ])
        
        # Create AutoScaling Group with 2 EC2 Instances
        web_server_asg = autoscaling.AutoScalingGroup(
            self, 
            "webServerAsgId", 
            vpc=vpc, 
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_NAT), 
            instance_type=ec2.InstanceType(instance_type_identifier="t2.micro"),
            role=web_server_role,
            machine_image=amz_linux_ami,
            min_capacity=2,
            max_capacity=3,
            # desired_capacity=2
            user_data=ec2.UserData.custom(user_data)
        )

        # Allow ASG Security Group receive traffic from ALB
        web_server_asg.connections.allow_from(alb, ec2.Port.tcp(80), description="Allows ASG Security Group to receive traffic from ALB")

        # Add AutoScaling Group Instances to ALB Target Group
        listener.add_targets("listenerId", port=80, targets=[web_server_asg], health_check=elbv2.HealthCheck(healthy_http_codes="200-499"))

        # Output of the ALB Domain Name
        output_alb_1 = CfnOutput(self, "albDomainName", value=f"http://{alb.load_balancer_dns_name}", description="Web Server ALB Domain Name")
