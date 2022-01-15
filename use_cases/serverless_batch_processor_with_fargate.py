from aws_cdk import (
    Stack,
    CfnOutput,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
    aws_applicationautoscaling as applicationautoscaling,
)
from constructs import Construct


class ServerlessBatchProcessorWithFargateStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create VPC
        vpc = ec2.Vpc(self, "my-vpc",
                      max_azs=2,
                      nat_gateways=1
                      )

        # Create ECS Cluster
        ecs_cluster = ecs.Cluster(self, "my-ecs-cluster", vpc=vpc)

        # Deploy Container in the microservice & attach a LoadBalancer
        loadbalanced_web_service = ecs_patterns.ScheduledFargateTask(
            self,
            "batchProcessor",
            cluster=ecs_cluster,
            scheduled_fargate_task_image_options={
                "image": ecs.ContainerImage.from_registry("mystique/batch-job-runner"),
                "memory_limit_mib": 512,
                "cpu": 256,
                "environment": {"name": "TRIGGER", "value": "CloudWatch Events"},
            },
            schedule=applicationautoscaling.Schedule.expression("rate(2 minutes)")
        )
