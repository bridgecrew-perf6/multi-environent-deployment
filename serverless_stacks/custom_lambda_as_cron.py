from aws_cdk import (
    Stack,
    Duration,
    aws_lambda as lambdaFunction,
    aws_logs as logs,
    aws_events as events,
    RemovalPolicy,
    aws_events_targets as events_targets,
)
from constructs import Construct


class CustomLambdaAsCronStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create Serverless Event Process using Lambda Function

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

        # Run Every day at 18:00 UTC
        six_pm_cron = events.Rule(self, "sixPmRule", schedule=events.Schedule.cron(
            hour="18", minute="0", month="*", week_day="MON-FRI", year="*"))

        # Setup Cron Based on Rate
        # Run Every 3 Minutes
        run_every_3_minutes = events.Rule(
            self, "threeMinutesRule", schedule=events.Schedule.rate(Duration.minutes(3)))

        # Add Lambda to CW Event Rule
        six_pm_cron.add_target(events_targets.LambdaFunction(g025_fn))
        run_every_3_minutes.add_target(events_targets.LambdaFunction(g025_fn))

