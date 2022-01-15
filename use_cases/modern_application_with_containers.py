from aws_cdk import (
    Stack,
    CfnOutput,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
)
from constructs import Construct


class ContainerizedMicroserviceWithECSStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create VPC
        vpc = ec2.Vpc(self, "my-vpc",
                      max_azs=2,
                      nat_gateways=1
                      )

        # Create ECS Cluster
        ecs_cluster = ecs.Cluster(self, "my-ecs-cluster", vpc=vpc)

        # Define ECS Cluster Capacity
        ecs_cluster.add_capacity(
            "DefaultAutoScalingGroup", instance_type=ec2.InstanceType("t2.micro"))

        # Deploy Container in the microservice & attach a LoadBalancer
        loadbalanced_web_service = ecs_patterns.ApplicationLoadBalancedEc2Service(
            self,
            "my-web-service",
            cluster=ecs_cluster,
            memory_reservation_mib=512,
            task_image_options={
                "image": ecs.ContainerImage.from_registry("nginx"),
                "container_port": 80,
                "environment": {"ENVIRONMENT": "PROD"},
            }
        )

        # Output the URL of the website
        output_1 = CfnOutput(
            self, "LoadBalancerDNS",
            value=f"{loadbalanced_web_service.load_balancer.load_balancer_dns_name}",
            description="Access the web service url from your browser"
        )
