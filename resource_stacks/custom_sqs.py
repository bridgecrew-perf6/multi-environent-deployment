from aws_cdk import (
    Stack,
    Duration,
    aws_sqs as sqs,
)
from constructs import Construct


class CustomSqsStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create a new SQS queue
        g025_queue = sqs.Queue(self, "g025-queue", queue_name="g025-queue.fifo",
                               fifo=True, encryption=sqs.QueueEncryption.KMS_MANAGED,
                               retention_period=Duration.days(4),
                               visibility_timeout=Duration.seconds(45))
