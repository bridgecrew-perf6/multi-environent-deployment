from aws_cdk import (
    Stack,
    aws_sns as sns,
    aws_sns_subscriptions as subs,
)
from constructs import Construct


class CustomSnsStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create a new SNS topic
        g025_topic = sns.Topic(
            self, "g025-topic", 
            display_name="g025-topic-display", 
            topic_name="g025-topic-name")

        # Add Subscription to SNS Topic
        g025_topic.add_subscription(subs.EmailSubscription("bass.kiattisak@gmail.com"))
