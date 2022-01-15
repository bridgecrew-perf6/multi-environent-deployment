from aws_cdk import (
    Stack,
    Duration,
    RemovalPolicy,
    aws_lambda as lambda_,
    aws_cloudwatch as cw,
    aws_logs as logs,
)
from constructs import Construct


class CustomCloudWatchDashboardsWidgetsStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Read Lambda Code
        try:
            with open("serverless_stacks/lambda_src/g025_custom_metric_log_generator.py", "r") as f:
                lambda_code = f.read()
        except OSError:
            print("Unable to read Lambda Code")

        # Create Lambda Function
        g025_fn = lambda_.Function(
            self,
            "g025Function",
            function_name="g025Function",
            runtime=lambda_.Runtime.PYTHON_3_8,
            handler="index.lambda_handler",
            code=lambda_.Code.from_inline(lambda_code),
            timeout=Duration.seconds(30),
            reserved_concurrent_executions=1,
            environment={'LOG_LEVEL': 'INFO'}
        )

        g025_lg = logs.LogGroup(
            self, "g025LogGroup",
            log_group_name=f"/aws/lambda/{g025_fn.function_name}",
            removal_policy=RemovalPolicy.DESTROY,
            retention=logs.RetentionDays.ONE_DAY
            )

        # Create Custom Metric Namespace
        third_party_error_metric = cw.Metric(namespace=f"third-party-error-metric",
                                             metric_name="third_party_error_metric",
                                             label="Total No. of Third Party API Errors",
                                             period=Duration.minutes(1),
                                             statistic="Sum")

        # Create Custom Metric Log Filter
        third_party_error_metric_filter = logs.MetricFilter(self,
                                                            "thirdPartyApiErrorMetricFilter",
                                                            filter_pattern=logs.FilterPattern.boolean_value(
                                                                "$.third_party_api_error", True),
                                                            log_group=g025_lg,
                                                            metric_namespace=third_party_error_metric.namespace,
                                                            metric_name=third_party_error_metric.metric_name,
                                                            default_value=0,
                                                            metric_value="1"
                                                            )

        # Create Third Party Error Alarm
        third_party_error_alarm = cw.Alarm(self,
                                           "thirdPartyApiErrorAlarm",
                                           alarm_description="Alert if 3rd party API has more than 2 errors in the last two minutes",
                                           alarm_name="third-party-api-alarm",
                                           metric=third_party_error_metric,
                                           comparison_operator=cw.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD,
                                           threshold=2,
                                           evaluation_periods=2,
                                           datapoints_to_alarm=1,
                                           treat_missing_data=cw.TreatMissingData.NOT_BREACHING,
                                           )
        
        # Create CLoudWatch Dashboard
        g025_dashboard = cw.Dashboard(self, id="g025Dashboard", dashboard_name="g025Dashboard")

        # Add lambda Function Metrics to Dashboard
        g025_dashboard.add_widgets(cw.Row(
                cw.GraphWidget(title="Backend-Invocations", left=[
                        g025_fn.metric_invocations(statistic="Sum", period=Duration.minutes(1))
                    ]
                ),
                cw.GraphWidget(title="Backend-Errors", left=[
                        g025_fn.metric_errors(statistic="Sum", period=Duration.minutes(1))
                    ]
                )
            )
        )

        # Add 3rd Party API Error to Dashboard
        g025_dashboard.add_widgets(cw.Row(
            cw.SingleValueWidget(title="3rd Party API Errors", metrics=[third_party_error_metric])
        ))