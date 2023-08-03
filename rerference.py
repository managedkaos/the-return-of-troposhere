'''Module: Create a CloudFormation Stack'''
import time
import troposphere.ec2 as ec2
from troposphere import Base64, FindInMap, GetAtt, Join
from troposphere import Parameter, Output, Ref, Template
from troposphere.rds import DBInstance
from troposphere.cloudformation import Init, InitConfig, InitFiles, InitFile, Metadata
from troposphere.policies import CreationPolicy, ResourceSignal

def main():
    '''Function: Generates the Cloudformation template'''
    template = Template()
    template.add_description("Dev Stack")

    keyname_param = template.add_parameter(
        Parameter(
            'KeyName',
            Description='An existing EC2 KeyPair.',
            ConstraintDescription='An existing EC2 KeyPair.',
            Type='AWS::EC2::KeyPair::KeyName',
        )
    )

    db_pass_param = template.add_parameter(
        Parameter(
            'DBPass',
            NoEcho=True,
            Type='String',
            Description='The database admin account password',
            ConstraintDescription='Must contain only alphanumeric characters',
            AllowedPattern="[-_a-zA-Z0-9]*",
        )
    )

    db_name_param = template.add_parameter(
        Parameter(
            'DBName',
            Default='miramax',
            Type='String',
            Description='The database name',
            ConstraintDescription='Must begin with a letter and contain only alphanumeric characters',
            AllowedPattern="[-_a-zA-Z0-9]*",
        )
    )

    db_user_param = template.add_parameter(
        Parameter(
            'DBUser',
            Default='miramax',
            Type='String',
            Description='Username for MySQL database access',
            ConstraintDescription='Must begin with a letter and contain only alphanumeric characters',
            AllowedPattern="[-_a-zA-Z0-9]*",
        )
    )

    template.add_mapping('RegionMap', {'ap-south-1': {'ami': 'ami-0d773a3b7bb2bb1c1'}, 'eu-west-3': {'ami': 'ami-08182c55a1c188dee'}, 'eu-west-2': {'ami': 'ami-0b0a60c0a2bd40612'}, 'eu-west-1': {'ami': 'ami-00035f41c82244dab'}, 'ap-northeast-2': {'ami': 'ami-06e7b9c5e0c4dd014'}, 'ap-northeast-1': {'ami': 'ami-07ad4b1c3af1ea214'}, 'sa-east-1': {'ami': 'ami-03c6239555bb12112'}, 'ca-central-1': {'ami': 'ami-0427e8367e3770df1'}, 'ap-southeast-1': {'ami': 'ami-0c5199d385b432989'}, 'ap-southeast-2': {'ami': 'ami-07a3bd4944eb120a0'}, 'eu-central-1': {'ami': 'ami-0bdf93799014acdc4'}, 'us-east-1': {'ami': 'ami-0ac019f4fcb7cb7e6'}, 'us-east-2': {'ami': 'ami-0f65671a86f061fcd'}, 'us-west-1': {'ami': 'ami-063aa838bd7631e0b'}, 'us-west-2': {'ami': 'ami-0bbe6b35405ecebdb'}})

    ec2_security_group = template.add_resource(
        ec2.SecurityGroup(
            'EC2SecurityGroup',
            Tags=[{'Key':'Name', 'Value':Ref('AWS::StackName')},],
            GroupDescription='EC2 Security Group',
            SecurityGroupIngress=[
                ec2.SecurityGroupRule(
                    IpProtocol='tcp',
                    FromPort='22',
                    ToPort='22',
                    CidrIp='0.0.0.0/0',
                    Description='SSH'),
                ec2.SecurityGroupRule(
                    IpProtocol='tcp',
                    FromPort='80',
                    ToPort='80',
                    CidrIp='0.0.0.0/0',
                    Description='HTTP'),
                ec2.SecurityGroupRule(
                    IpProtocol='tcp',
                    FromPort='443',
                    ToPort='443',
                    CidrIp='0.0.0.0/0',
                    Description='HTTPS'),
            ],
        )
    )

    db_security_group = template.add_resource(
        ec2.SecurityGroup(
            'DBSecurityGroup',
            Tags=[{'Key':'Name', 'Value':Ref('AWS::StackName')},],
            GroupDescription='DB Security Group',
            SecurityGroupIngress=[
                    ec2.SecurityGroupRule(
                    IpProtocol='tcp',
                    FromPort='3306',
                    ToPort='3306',
                    SourceSecurityGroupId=GetAtt(ec2_security_group, "GroupId"),
                    Description='MySQL'),
            ]
        )
    )
    ec2_instance = template.add_resource(
        ec2.Instance(
            'Instance',
            Metadata=Metadata(
                Init({
                    "config": InitConfig(
                        files=InitFiles({
                            "/tmp/instance.txt": InitFile(
                                content=Ref('AWS::StackName'),
                                mode="000644",
                                owner="root",
                                group="root"
                            )
                        }),
                    )
                }),
            ),
            CreationPolicy=CreationPolicy(
                ResourceSignal=ResourceSignal(Timeout='PT15M')
            ),
            Tags=[{'Key':'Name', 'Value':Ref('AWS::StackName')},],
            ImageId=FindInMap('RegionMap', Ref('AWS::Region'), 'ami'),
            InstanceType='t3.medium',
            KeyName=Ref(keyname_param),
            SecurityGroups=[Ref(ec2_security_group), Ref(db_security_group)],
            DependsOn='Database',
            IamInstanceProfile='SecretsManagerReadWrite',
            UserData=Base64(
                Join(
                    '',
                    [
                        '#!/bin/bash -x\n',
                        'exec > /tmp/user-data.log 2>&1\n',
                        'unset UCF_FORCE_CONFFOLD\n',
                        'export UCF_FORCE_CONFFNEW=YES\n',
                        'ucf --purge /boot/grub/menu.lst\n',
                        'export DEBIAN_FRONTEND=noninteractive\n',
                        'apt-get update\n',
                        'apt-get -o Dpkg::Options::="--force-confnew" --force-yes -fuy upgrade\n',
			'apt-get install -y python-pip apache2 libapache2-mod-wsgi libmysqlclient-dev\n',
			'pip install https://s3.amazonaws.com/cloudformation-examples/aws-cfn-bootstrap-latest.tar.gz\n',
                        '# Signal Cloudformation when set up is complete\n',
                        '/usr/local/bin/cfn-signal -e $? --resource=Instance --region=', Ref('AWS::Region'), ' --stack=', Ref('AWS::StackName'), '\n',
                    ]
                )
            )
        )
    )

    ip_association = template.add_resource(
        ec2.EIPAssociation(
            'IPAssociation',
            InstanceId=Ref(ec2_instance),
            AllocationId='eipalloc-aa755d96'
        )
    )

    db_instance = template.add_resource(
        DBInstance(
            'Database',
            DBName=Ref(db_name_param),
            AllocatedStorage=20,
            DBInstanceClass='db.t2.micro',
            Engine='MySQL',
            EngineVersion='5.7.21',
            MasterUsername=Ref(db_user_param),
            MasterUserPassword=Ref(db_pass_param),
            VPCSecurityGroups=[GetAtt(db_security_group, "GroupId")],
        )
    )

    template.add_output([
        Output(
            'InstanceDnsName',
            Description='PublicDnsName',
            Value=GetAtt(ec2_instance, 'PublicDnsName'),
        ),
        Output(
            'DatabaseDnsName',
            Description='DBEndpoint',
            Value=GetAtt(db_instance, 'Endpoint.Address'),
        ),
    ])

    print(template.to_yaml())

if __name__ == '__main__':
    main()
