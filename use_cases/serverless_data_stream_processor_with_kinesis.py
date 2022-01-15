from aws_cdk import (
    Stack,
    Duration,
    RemovalPolicy,
    aws_kinesis as kinesis,
    aws_s3 as s3,
    aws_lambda as lambda_,
    aws_iam as iam,
    aws_logs as logs,
    aws_lambda_event_sources as event_sources,
)
from constructs import Construct


class ServerlessStreamProcessorArchitectureWithKinesisStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create a Kinetisis Stream
        stream_data_processing = kinesis.Stream(self,
                                                "stream-data-processing",
                                                retention_period=Duration.hours(
                                                    24),
                                                shard_count=1,
                                                stream_name="stream-data-processing"
                                                )

        # Create a S3 Bucket for storing streaming data events
        s3_bucket_streaming_data = s3.Bucket(self,
                                             "s3-bucket-streaming-data",
                                             bucket_name="s3-bucket-streaming-data-g025",
                                             removal_policy=RemovalPolicy.DESTROY,
                                             auto_delete_objects=True)

        # Read Lambda Code
        try:
            with open("use_cases/lambda_src/stream_record_consumer.py", mode="r") as f:
                lambda_consumer_src = f.read()
        except OSError:
            print("Could not read lambda_src")

        # Create a Lambda Function
        stream_consumer_fn = lambda_.Function(self,
                                              "stream-consumer-fn",
                                              function_name="stream_consumer_fn",
                                              description="Process streaming data events from kinesis and store in S3",
                                              runtime=lambda_.Runtime.PYTHON_3_8,
                                              handler="index.lambda_handler",
                                              code=lambda_.Code.from_inline(
                                                  lambda_consumer_src),
                                              timeout=Duration.seconds(30),
                                              reserved_concurrent_executions=1,
                                              environment={
                                                  "LOG_LEVEL": "INFO",
                                                  "BUCKET_NAME": s3_bucket_streaming_data.bucket_name
                                              }
                                              )

        # Update Lambda Function Permissions to use Kinetisis Stream
        stream_data_processing.grant_read(stream_consumer_fn)

        # Add permissions to lanmda to write to S3
        s3_bucket_streaming_data.grant_write(stream_consumer_fn)

        # Create Custom Loggroup
        stream_consumer_lg = logs.LogGroup(self,
                                           "stream-consumer-lg",
                                           log_group_name=f"/aws/lambda/{stream_consumer_fn.function_name}",
                                           removal_policy=RemovalPolicy.DESTROY,
                                           retention=logs.RetentionDays.ONE_DAY
                                           )

        # Create a Kinesis Event Source
        stream_data_processing_event_source = event_sources.KinesisEventSource(
            stream=stream_data_processing,
            starting_position=lambda_.StartingPosition.LATEST,
            batch_size=1)

        # Attach Kinesis Event Source to Lambda Function
        stream_consumer_fn.add_event_source(
            stream_data_processing_event_source)

        ########################################
        #######                          #######
        #######   Stream Data Producer   #######
        #######                          #######
        ########################################

        # Read Lambda Code
        try:
            with open("use_cases/lambda_src/stream_record_producer.py", mode="r") as f:
                lambda_producer_src = f.read()
        except OSError:
            print("Could not read lambda_src")

        # Create a Lambda Function
        stream_producer_fn = lambda_.Function(self,
                                              "stream-producer-fn",
                                              function_name="stream_producer_fn",
                                              description="Produce streaming data events to kinesis",
                                              runtime=lambda_.Runtime.PYTHON_3_8,
                                              handler="index.lambda_handler",
                                              code=lambda_.Code.from_inline(
                                                  lambda_producer_src),
                                              timeout=Duration.seconds(60),
                                              reserved_concurrent_executions=1,
                                              environment={
                                                  "LOG_LEVEL": "INFO",
                                                  "STREAM_NAME": stream_data_processing.stream_name
                                              }
                                              )

        # Grant permissions to write to Kinesis Stream
        stream_data_processing.grant_write(stream_producer_fn)

        # Create Custom Loggroup
        stream_producer_lg = logs.LogGroup(self,
                                           "stream-producer-lg",
                                           log_group_name=f"/aws/lambda/{stream_producer_fn.function_name}",
                                           removal_policy=RemovalPolicy.DESTROY,
                                           retention=logs.RetentionDays.ONE_DAY
                                           )
