from aws_cdk import (
    Stack,
    Duration,
    aws_lambda as lambdaFunction,
    aws_apigateway as apigw,
    aws_logs as logs,
    RemovalPolicy,
    CfnOutput
)
from constructs import Construct


class CustomAPIGatewayLambdaStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Read Lambda Code
        try:
            with open("serverless_stacks/lambda_src/g025_processor.py", "r") as f:
                lambda_code = f.read()
        except OSError:
            print("Unable to read Lambda Code")

        g025_fn = lambdaFunction.Function(
            self,
            "g025Function",
            function_name="g025Function",
            runtime=lambdaFunction.Runtime.PYTHON_3_8,
            handler="index.lambda_handler",
            code=lambdaFunction.Code.from_inline(lambda_code),
            timeout=Duration.seconds(3),
            reserved_concurrent_executions=1,
            environment={'LOG_LEVEL': 'INFO'}
        )

        # Create Custom Log Group
        # /aws/lambda/g025Function
        g025_lg = logs.LogGroup(
            self, "g025LogGroup",
            log_group_name=f"/aws/lambda/{g025_fn.function_name}",
            removal_policy=RemovalPolicy.DESTROY)

        # Add API GW infront of Lambda
        g025_fn_integration = apigw.LambdaRestApi(
            self, "g025ApiEndpoint", handler=g025_fn)

        output_1 = CfnOutput(
            self, "apiUrl", value=f"{g025_fn_integration.url}", description="Use a browser to access this url")
