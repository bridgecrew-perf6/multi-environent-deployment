from aws_cdk import (
    Stack,
    CfnOutput,
    aws_ssm as ssm,
    aws_secretsmanager as secretmanager
)
from constructs import Construct
import json


class CustomParametersSecretStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Let us create AWS secrets & SSM Parameters
        param1 = ssm.StringParameter(
            self, "parameter1",
            description="Load Testing Configuration",
            parameter_name="/local/configs/DurationInSeconds",
            string_value="300",
            tier=ssm.ParameterTier.STANDARD
        )

        # ERROR because SSM Parameters of type SecureString cannot be created using CloudFormation
        # param2 = ssm.StringParameter(
        #     self, "parameter2",
        #     description="Secret Password",
        #     parameter_name="/local/configs/SecretPassword",
        #     type=ssm.ParameterType.SECURE_STRING,
        #     string_value="ke3f78",
        #     tier=ssm.ParameterTier.STANDARD
        # )

        secret1 = secretmanager.Secret(
            self, 
            "secret1", 
            description="Customer DB Password", 
            secret_name="cust_db_pass")

        templated_secret = secretmanager.Secret(
            self, 
            "secret2", 
            description="A Templated secret for user data", 
            secret_name="user_kon_attributes",
            generate_secret_string=secretmanager.SecretStringGenerator(
                secret_string_template=json.dumps({"username": "kon"}), 
                generate_string_key="password")
            )

        output1 = CfnOutput(
            self, "output_param1", description="Duration In Seconds", value=f"{param1.string_value}")
        output2 = CfnOutput(
            self, "output_secret1", description="Customer DB Password", value=f"{secret1.secret_value}")
