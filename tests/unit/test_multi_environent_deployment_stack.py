import aws_cdk as core
import aws_cdk.assertions as assertions

from multi_environent_deployment.multi_environent_deployment_stack import MultiEnvironentDeploymentStack

# example tests. To run these tests, uncomment this file along with the example
# resource in multi_environent_deployment/multi_environent_deployment_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = MultiEnvironentDeploymentStack(app, "multi-environent-deployment")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
