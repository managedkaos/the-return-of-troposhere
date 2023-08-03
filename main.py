'''
Messing around with troposphere... again! :D
'''
from troposphere import Template, Output, Ref, GetAtt, Sub
from troposphere import apprunner, ecr, iam

from awacs.aws import Allow, PolicyDocument, Principal, Statement
from awacs.sts import AssumeRole


def main():
    '''
    Function: Generates the Cloudformation template
    '''
    template = Template()

    template.set_description("This is the CloudFormation stack.")

    image_repository = template.add_resource(
        ecr.Repository(
            "ImageRepository",
            RepositoryName=Sub("${AWS::StackName}")
        )
    )

    app_runner_access_role = template.add_resource(
        iam.Role(
            "AppRunnerServiceRole",
            RoleName=Sub("${AWS::StackName}"),
            AssumeRolePolicyDocument=PolicyDocument(
                Statement=[
                    Statement(
                        Effect=Allow,
                        Action=[AssumeRole],
                        Principal=Principal(
                            "Service", ["build.apprunner.amazonaws.com"]),
                    )
                ]
            ),
            ManagedPolicyArns=[
                "arn:aws:iam::aws:policy/service-role/AWSAppRunnerServicePolicyForECRAccess"]
        )
    )

    environments = {}

    for environment in ['Staging', 'Production']:
        environments[environment] = template.add_resource(
            apprunner.Service(
                f"{environment}Environment",
                ServiceName=f"awesome-application-{environment}".lower(),
                SourceConfiguration=apprunner.SourceConfiguration(
                    AutoDeploymentsEnabled=False,
                    AuthenticationConfiguration=apprunner.AuthenticationConfiguration(
                        AccessRoleArn=GetAtt(
                            logicalName=app_runner_access_role, attrName="Arn")
                    ),
                    ImageRepository=apprunner.ImageRepository(
                        ImageRepositoryType="ECR_PUBLIC",
                        ImageIdentifier="public.ecr.aws/aws-containers/hello-app-runner:latest",
                    )
                ),
            )
        )

        template.add_output([
            Output(
                f"{environment}Environment",
                Description=f"{environment}Environment",
                Value=GetAtt(environments[environment], "ServiceUrl"),
            ),
        ])

    app_runner_admin_group = template.add_resource(
        iam.Group(
            "AppRunnerAdmin",
            GroupName=Sub("${AWS::StackName}"),
            ManagedPolicyArns=[
                "arn:aws:iam::aws:policy/AWSAppRunnerFullAccess"]
        )
    )

    app_runner_service_account = template.add_resource(
        iam.User(
            "ServiceAccount",
            UserName=Sub("${AWS::StackName}"),
            Groups=[Ref(app_runner_admin_group)]
        )
    )

    app_runner_service_account_access_keys = template.add_resource(
        iam.AccessKey(
            "AccessKeys",
            UserName=Ref(app_runner_service_account)
        )
    )

    print(template.to_yaml())


if __name__ == '__main__':
    main()
