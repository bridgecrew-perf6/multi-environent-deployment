#!/usr/bin/env python3
import os

import aws_cdk as cdk

from multi_environent_deployment.multi_environent_deployment_stack import MultiEnvironentDeploymentStack

app = cdk.App()

# dev_account = app.node.try_get_context('envs')['dev']
# prod_account = app.node.try_get_context('envs')['prod']

# env_AUS = cdk.Environment(region=dev_account['region'], account=dev_account['account'])
# env_ASIA = cdk.Environment(region=prod_account['region'], account=prod_account['account'])

# MultiEnvironentDeploymentStack(app, "myDevStack", is_prod=False, env=env_AUS)
# MultiEnvironentDeploymentStack(app, "myProdStack", is_prod=True, env=env_ASIA)

app.synth()
