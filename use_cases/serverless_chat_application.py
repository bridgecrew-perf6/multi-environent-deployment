from aws_cdk import (
    Stack,
    CfnOutput,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
)
from constructs import Construct


class ServerlessChatApplicationStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create VPC
        vpc = ec2.Vpc(self, "my-vpc",
                      max_azs=2,
                      nat_gateways=1
                      )

        # Create ECS Cluster
        ecs_cluster = ecs.Cluster(self, "my-ecs-cluster", vpc=vpc)

        # Create chat service as Fargate Task
        chat_app_task = ecs.FargateTaskDefinition(self, "chat-app-task")

        # Create Container Definition
        chat_app_container = chat_app_task.add_container(
            "chat-app-container",
            image=ecs.ContainerImage.from_registry(
                "mystique/fargate-chat-app:latest"),
            environment={"github": "https://github.com/miztiik"}
        )

        # Add Port Mapping to Container, Chat app runs on Port 3000
        chat_app_container.add_port_mappings(ecs.PortMapping(
            container_port=3000, protocol=ecs.Protocol.TCP))

        # Deploy Container in the Microservice & attach a LoadBalancer
        chat_app_service = ecs_patterns.ApplicationLoadBalancedFargateService(
            self,
            "chat-app-service",
            cluster=ecs_cluster,
            task_definition=chat_app_task,
            assign_public_ip=True,
            public_load_balancer=True,
            listener_port=80,
            desired_count=1,
            service_name="chat-app-service",
        )

        # Output Chat App Url
        output_1 = CfnOutput(
            self, "ChatAppUrl", value=f"http://{chat_app_service.load_balancer.load_balancer_dns_name}", description="Chat App Url")
