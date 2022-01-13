from aws_cdk import (
    Stack,
    CfnOutput,
    SecretValue,
    Aws,
    aws_iam as iam,
    aws_secretsmanager as secretmanager,
    aws_ssm as ssm
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
        generalman_group = iam.Group(
            self, "generalman-group", group_name="generalman-group")

        # Add User to Group
        generalman_group.add_user(user2)

        # Add Managed Policy to Group
        generalman_group.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name(
            "AmazonS3ReadOnlyAccess")
        )

        # Grant Group to LIST ALL SSM Parameters in Console
        group_statement1 = iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            resources=["*"],
            actions=["ssm:DescribeParameters"], sid="DescribeAllParametersInConsole"
        )

        # Add Permission To Group
        generalman_group.add_to_policy(group_statement1)

        param1 = ssm.StringParameter(
            self, "parameter1",
            description="Load Testing Configuration",
            parameter_name="/local/configs/DurationInSeconds",
            string_value="300",
            tier=ssm.ParameterTier.STANDARD
        )

        # Grant generalman-group read access to SSM Parameter
        param1.grant_read(generalman_group)

        # Create IAM Role
        generalman_group_role = iam.Role(
            self,
            'generalman-group-role',
            assumed_by=iam.AccountPrincipal(f"{Aws.ACCOUNT_ID}"),
            role_name="generalman-group-role")

        list_ec2_policy = iam.ManagedPolicy(
            self, "listEc2Instances", 
            description="list ec2 instances in the account", 
            managed_policy_name="list_ec2_policy", 
            statements=[
                iam.PolicyStatement(
                    effect=iam.Effect.ALLOW,
                    actions=[
                        "ec2:Describe*",
                        "cloudwatch:Describe*",
                        "cloudwatch:Get*"
                    ],
                    resources=["*"]
                )
            ],
            roles=[generalman_group_role]
        )

        output_1 = CfnOutput(self, "user2LoginUrl",
                             description="Login Url for User 2",
                             value=f"https://{Aws.ACCOUNT_ID}.signin.aws.amazon.com/console")
