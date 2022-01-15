from aws_cdk import (
    Stack,
    RemovalPolicy,
    Duration,
    aws_s3 as s3,
    aws_dynamodb as dynamodb,
    aws_iam as iam,
    aws_lambda as lambda_,
    aws_logs as logs,
    aws_s3_notifications as s3_notifications,
)
from constructs import Construct


class ServerlessEventProcessorArchitectureStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create an S3 Bucket for storing our web store assets
        web_store_assets_bkt = s3.Bucket(
            self, "web-store-assets-bkt", versioned=True, removal_policy=RemovalPolicy.DESTROY)

        # Creat a DynamoDB table
        web_store_table = dynamodb.Table(self, "web-store-table", partition_key=dynamodb.Attribute(
            name="_id", type=dynamodb.AttributeType.STRING), removal_policy=RemovalPolicy.DESTROY)

        # Read Lambda Code
        try:
            with open("use_cases/lambda_src/s3_event_processor.py", "r") as f:
                lambda_src = f.read()
        except OSError:
            print("Could not read lambda_src")

        # Deploy the lambda function
        s3_event_processor_fn = lambda_.Function(self,
                                                 "s3_event_processor_lambda",
                                                 function_name="g025_store_processor_function",
                                                 description="Process store events and update DDB",
                                                 runtime=lambda_.Runtime.PYTHON_3_8,
                                                 handler="index.lambda_handler",
                                                 code=lambda_.Code.from_inline(
                                                         lambda_src),
                                                 timeout=Duration.seconds(
                                                     30),
                                                 reserved_concurrent_executions=1,
                                                 environment={
                                                     "LOG_LEVEL": "INFO",
                                                     "DDB_TABLE_NAME": f"{web_store_table.table_name}"
                                                 }
                                                 )

        # Add DynamoDB Write Privilledges to Lambda
        web_store_table.grant_read_write_data(s3_event_processor_fn)

        # Create Custom Loggroup
        web_store_lg = logs.LogGroup(
            self, "web-store-lg", 
            log_group_name=f"/aws/lambda/{s3_event_processor_fn.function_name}", 
            removal_policy=RemovalPolicy.DESTROY, retention=logs.RetentionDays.ONE_DAY)

        # Create S3 notification for lambda function
        web_store_backend = s3_notifications.LambdaDestination(fn=s3_event_processor_fn)

        # Assign notification for S3 event type (ex: OBJECT_CREATED)
        web_store_assets_bkt.add_event_notification(s3.EventType.OBJECT_CREATED, web_store_backend)
