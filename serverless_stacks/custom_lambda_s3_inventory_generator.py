from aws_cdk import (
    Stack,
    Duration,
    aws_lambda as lambdaFunction,
    aws_logs as logs,
    aws_iam as iam,
    aws_dynamodb as dynamodb,
    RemovalPolicy
)
from constructs import Construct


class CustomLambdaS3InventoryGeneratorStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create Serverless Event Process using Lambda Function

        # Read Lambda Code
        try:
            with open("serverless_stacks/lambda_src/g025_s3_inventory_generator.py", "r") as f:
                lambda_code = f.read()
        except OSError:
            print("Unable to read Lambda Code")

        # Create DynamoDB Table
        ddb_table = dynamodb.Table(
            self, "ddb_table", 
            table_name="g025-inventory-table",
            partition_key=dynamodb.Attribute(
                name="_id", type=dynamodb.AttributeType.STRING
            ),
            removal_policy=RemovalPolicy.DESTROY
        )

        # Create Lambda Function
        g025_fn = lambdaFunction.Function(
            self,
            "g025Function",
            function_name="g025Function",
            runtime=lambdaFunction.Runtime.PYTHON_3_8,
            handler="index.lambda_handler",
            code=lambdaFunction.Code.from_inline(lambda_code),
            timeout=Duration.seconds(30),
            reserved_concurrent_executions=1,
            environment={
                'LOG_LEVEL': 'INFO',
                'DDB_TABLE_NAME': f'{ddb_table.table_name}'
            }
        )

        # Create Custom Log Group
        # /aws/lambda/g025Function
        g025_lg = logs.LogGroup(
            self, "g025LogGroup",
            log_group_name=f"/aws/lambda/{g025_fn.function_name}",
            removal_policy=RemovalPolicy.DESTROY)

        # Add S3 Read Only Managed Policy to Lambda
        g025_fn.role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name('AmazonS3ReadOnlyAccess'))

        # Add DynamoDB write Privilledges to Lambda
        ddb_table.grant_write_data(g025_fn)
