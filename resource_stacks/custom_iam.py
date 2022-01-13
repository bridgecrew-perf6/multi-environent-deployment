from aws_cdk import (
    Stack,
    CfnOutput,
    SecretValue,
    Aws,
    aws_iam as iam,
    aws_secretsmanager as secretmanager
)
from constructs import Construct


class CustomIAMStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        user1_pass = secretmanager.Secret(
            self, "user1-pass", description="Password for User1", secret_name="user1-pass")

        # Add User1 with SecretsManager Password
        user1 = iam.User(self, "user1", user_name="user1",
                         password=user1_pass.secret_value)

        # Add User2
        user2 = iam.User(self, "user2", user_name="user2",
                         password=SecretValue.plain_text("Dont-Use-B@d-Passw0rd"))

        # Add IAM Group
        generalman_group = iam.Group(self, "generalman-group", group_name="generalman-group")

        generalman_group.add_user(user2)

        output_1 = CfnOutput(self, "user2LoginUrl",
                             description="Login Url for User 2",
                             value=f"https://{Aws.ACCOUNT_ID}.signin.aws.amazon.com/console")
