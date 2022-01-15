from aws_cdk import (
    Stack,
    RemovalPolicy,
    Duration,
    aws_dynamodb as dynamodb,
    aws_lambda as lambda_,
    aws_lambda_event_sources as event_sources,
)
from constructs import Construct


class ServerlessDynamoDBEventProcessorWithDynamoDBStreamStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create a DynamoDB Table
        api_table = dynamodb.Table(self,
                                   "api-table",
                                   table_name="api-table",
                                   partition_key=dynamodb.Attribute(
                                       name="_id", type=dynamodb.AttributeType.STRING),
                                   stream=dynamodb.StreamViewType.NEW_AND_OLD_IMAGES,
                                   removal_policy=RemovalPolicy.DESTROY
                                   )

        # Read Lambda Code
        try:
            with open("use_cases/lambda_src/dynamodb_stream_processor.py", mode="r") as f:
                lambda_src = f.read()
        except OSError:
            print("Could not read lambda_src")

        # Create a Lambda Function
        ddb_stream_processor_fn = lambda_.Function(
            self,
            "dynamodb_stream_processor_fn",
            runtime=lambda_.Runtime.PYTHON_3_8,
            handler="index.lambda_handler",
            code=lambda_.Code.from_inline(lambda_src),
            timeout=Duration.seconds(30),
            reserved_concurrent_executions=1,
            environment={
                "LOG_LEVEL": "INFO",
            }
        )

        # Create a new DyanmoDB Stream Event Source
        ddb_stream_event_source = event_sources.DynamoEventSource(
            table=api_table, 
            starting_position=lambda_.StartingPosition.TRIM_HORIZON, 
            bisect_batch_on_error=True)

        # Attach DyanmoDB Stream Event Source to Lambda Function
        ddb_stream_processor_fn.add_event_source(ddb_stream_event_source)
