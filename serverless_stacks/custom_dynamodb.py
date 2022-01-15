from aws_cdk import (
    Stack,
    Duration, 
    RemovalPolicy,
    aws_dynamodb as dynamodb,
)
from constructs import Construct


class CustomDynamoDBStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        g025_table = dynamodb.Table(self, "g025Table", partition_key=dynamodb.Attribute(
            name="id", type=dynamodb.AttributeType.STRING),
            removal_policy=RemovalPolicy.DESTROY)
