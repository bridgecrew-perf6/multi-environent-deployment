from aws_cdk import (
    Stack,
    Duration,
    RemovalPolicy,
    aws_sns as sns,
    aws_sns_subscriptions as subs,
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_lambda as lambda_,
    aws_logs as logs,
    aws_cloudwatch as cw,
    aws_cloudwatch_actions as cwa,
)
from constructs import Construct


class CustomEc2WithAlarmsStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, vpc, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create a new SNS topic
        g025_topic = sns.Topic(
            self, "g025-topic",
            display_name="g025-topic-display",
            topic_name="g025-topic-name")

        # Add Subscription to SNS Topic
        g025_topic.add_subscription(
            subs.EmailSubscription("bass.kiattisak@gmail.com"))

        # Read Bootstrap Script
        with open("bootstrap_scripts/install_httpd.sh", mode="r") as file:
            user_data = file.read()

        # Get the latest Linux AMI
        amz_linux_ami = ec2.MachineImage.latest_amazon_linux(
            generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2,
            edition=ec2.AmazonLinuxEdition.STANDARD,
            storage=ec2.AmazonLinuxStorage.GENERAL_PURPOSE,
            virtualization=ec2.AmazonLinuxVirt.HVM
        )

        # WebServer Instance
        web_server = ec2.Instance(self, "webServerId",
                                  instance_type=ec2.InstanceType(
                                      instance_type_identifier="t2.nano"),
                                  instance_name="WebServer001",
                                  machine_image=amz_linux_ami,
                                  vpc=vpc,
                                  vpc_subnets=ec2.SubnetSelection(
                                      subnet_type=ec2.SubnetType.PUBLIC),
                                  user_data=ec2.UserData.custom(user_data)
                                  )

        # Allow Web Traffic to WebServer
        web_server.connections.allow_from_any_ipv4(
            ec2.Port.tcp(80), "Allow Web Traffic to WebServer")

        # Add Permission to WebServer to SSM
        web_server.role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSSMManagedInstanceCore"))

        # Read Lambda Code
        try:
            with open("serverless_stacks/lambda_src/g025_processor.py", "r") as f:
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

        # Create Custom Log Group
        # /aws/lambda/g025Function
        g025_lg = logs.LogGroup(
            self, "g025LogGroup",
            log_group_name=f"/aws/lambda/{g025_fn.function_name}",
            removal_policy=RemovalPolicy.DESTROY)

        # EC2 Metric for Avg. CPU
        ec2_metric_for_avg_cpu = cw.Metric(
            namespace="AWS/EC2",
            metric_name="CPUUtilization",
            dimensions_map={
                "InstanceId": web_server.instance_id
            },
            period=Duration.minutes(1),
        )

        # Low CPU Alarm for Web Server
        low_cpu_alarm = cw.Alarm(
            self, "LowCPUAlarm",
            alarm_description="Alert if CPU is less than 10%",
            alarm_name="low-cpu-alarm",
            actions_enabled=True,
            metric=ec2_metric_for_avg_cpu,
            threshold=10,
            comparison_operator=cw.ComparisonOperator.LESS_THAN_OR_EQUAL_TO_THRESHOLD,
            evaluation_periods=1,
            datapoints_to_alarm=1,
            treat_missing_data=cw.TreatMissingData.NOT_BREACHING,
        )

        # Inform SNS on EC2 Low CPU Alarm
        low_cpu_alarm.add_alarm_action(cwa.SnsAction(g025_topic))

        # Create Lambda Alarm
        g025_fn_error_alrm = cw.Alarm(
            self, "g025FunctionErrorAlarm",
            metric=g025_fn.metric_errors(),
            threshold=2,
            evaluation_periods=1,
        )

        # Inform SNS on Lambda Alarm State
        g025_fn_error_alrm.add_alarm_action(cwa.SnsAction(g025_topic))
