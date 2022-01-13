from aws_cdk import (
    Stack,
    RemovalPolicy,
    Duration,
    CfnOutput,
    aws_rds as rds,
    aws_ec2 as ec2
)
from constructs import Construct


class CustomRDSStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, vpc, asg_security_groups, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        db = rds.DatabaseInstance(self,
                                  "db1",
                                  credentials=rds.Credentials.from_generated_secret(
                                      "generalman025"),
                                  database_name="g025_db",
                                  engine=rds.DatabaseInstanceEngine.MYSQL,
                                  vpc=vpc,
                                  port=3306,
                                  allocated_storage=30,
                                  multi_az=False,
                                  cloudwatch_logs_exports=[
                                      "audit", "error", "general", "slowquery"],
                                  instance_type=ec2.InstanceType.of(
                                      ec2.InstanceClass.BURSTABLE2, ec2.InstanceSize.MICRO),
                                  removal_policy=RemovalPolicy.DESTROY,
                                  deletion_protection=False,
                                  delete_automated_backups=True,
                                  backup_retention=Duration.days(7)
                                  )

        for sg in asg_security_groups:
            db.connections.allow_from(sg, ec2.Port.tcp(
                3306), "Allow MySQL access from ASG security group")

        output_1 = CfnOutput(self, "DatabaseConnectionCommand",
                             value=f"mysql -h {db.db_instance_endpoint_address} -P 3306 -u generalman025 -p",
                             description="Database Connection Command")
