# the-return-of-troposhere
Messing around with troposphere... again! :D

## References
- [Troposphere Repo](https://github.com/cloudtools/troposphere/tree/main)
- [Trpoosphere Package Reference](https://troposphere.readthedocs.io/en/latest/apis/troposphere_toc.html)
- [Cloudformation Template Resource and Property Types](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-template-resource-type-ref.html)
- [AWS CloudFormation Attributes (GetAtt) Cheat Sheet](https://towardsthecloud.com/aws-cloudformation-resource-attributes)
- [Service Linked Role for App Runner](https://docs.aws.amazon.com/apprunner/latest/dg/using-service-linked-roles-management.html)
- [App Runner Cloudformation Example + GitHub Actions](https://dev.to/aws-builders/infrastructure-as-code-on-aws-aws-cloudformation-and-cicd-with-github-actions-3bij)

## Examples
- [ECR](https://github.com/cloudtools/troposphere/blob/main/examples/ECRSample.py)
- [IAM Roles and Instance Profiles](https://github.com/cloudtools/troposphere/blob/main/examples/IAM_Roles_and_InstanceProfiles.py)
- [IAM Users, Groups, and Policies pt 1](https://github.com/cloudtools/troposphere/blob/main/examples/IAM_Users_Groups_and_Policies.py)
- [IAM Users, Groups, and Policies pt 2](https://github.com/cloudtools/troposphere/blob/main/examples/IAM_Users_snippet.py)
- [Secrets Manager](https://github.com/cloudtools/troposphere/blob/main/examples/Secretsmanager.py)

## Code Snips
- AppRunnerECRAccessRole
    - Managed Policy = `AWSAppRunnerServicePolicyForECRAccess`, `arn:aws:iam::aws:policy/service-role/AWSAppRunnerServicePolicyForECRAccess`
    