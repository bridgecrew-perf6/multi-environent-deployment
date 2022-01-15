from aws_cdk import (
    Stack,
    RemovalPolicy,
    Duration,
    CfnOutput,
    aws_dynamodb as dynamodb,
    aws_lambda as lambda_,
    aws_logs as logs,
    aws_apigateway as apigateway,
)
from constructs import Construct


class ServerlessRESTAPIArchitectureStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create a DynamoDB table
        api_table = dynamodb.Table(self, "api-table", partition_key=dynamodb.Attribute(
            name="_id", type=dynamodb.AttributeType.STRING), removal_policy=RemovalPolicy.DESTROY)

        # Read Lambda Code
        try:
            with open("use_cases/lambda_src/rest_api_backend.py", "r") as f:
                lambda_src = f.read()
        except OSError:
            print("Could not read lambda_src")

        # Create a Lambda Function
        api_backend_fn = lambda_.Function(self,
                                          "api-backend-fn",
                                          function_name="api-backend-fn",
                                          description="Process API events from APIGW and ingest to DDB",
                                          runtime=lambda_.Runtime.PYTHON_3_8,
                                          handler="index.lambda_handler",
                                          code=lambda_.Code.from_inline(
                                              lambda_src),
                                          timeout=Duration.seconds(10),
                                          reserved_concurrent_executions=1,
                                          environment={
                                              "LOG_LEVEL": "INFO",
                                              "DDB_TABLE_NAME": api_table.table_name
                                          })

        # Add DynamoDB Write Privilledges to Lambda
        api_table.grant_read_write_data(api_backend_fn)

        # Create Custom Loggroup
        api_backend_lg = logs.LogGroup(self,
                                       "api-backend-lg",
                                       log_group_name="api-backend-lg",
                                       removal_policy=RemovalPolicy.DESTROY,
                                       retention=logs.RetentionDays.ONE_DAY)

        # Add API Gateway infront of Lambda
        api_gw = apigateway.LambdaRestApi(
            self, 
            "api-frontend", 
            rest_api_name="api-frontend",
            handler=api_backend_fn, 
            proxy=False)

        user_name = api_gw.root.add_resource("{user_name}")
        add_user_likes = user_name.add_resource("{likes}")
        add_user_likes.add_method("GET")

        # Output the URL of the API Gateway
        output_1 = CfnOutput(self,
                             "output-1",
                             value=f"{api_gw.url}",
                             description="Use a browser to access this url, Replace {user_name} and {likes} with your own values")
