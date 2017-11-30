import logging
import os
import shutil
from os import path
from time import time

import yaml
from boto3.session import Session

from rollout.constants import EC2_INSTANCE_TYPES
from rollout.lib.util import get_aws_credentials, ask

logger = logging.getLogger('create')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)


def get_subnets(ec2):
    result = ec2.describe_subnets()
    return result['Subnets']


def get_keypath(keyname):
    return '.rollout/keys/{}.pem'.format(keyname)


def create_key(ec2, service, region):
    keyname = '{}.{}'.format(service, region.replace('-', ''))
    response = ec2.create_key_pair(
        KeyName='{}.{}'.format(service, region.replace('-', '')),
        DryRun=False,
    )
    blob = response['KeyMaterial']

    with open(get_keypath(keyname), 'w') as f:
        f.write(blob)

    return keyname


def wait_for_public_dns_name(ec2, instance_id, timeout=30):
    start_time = time()

    while True:
        if time() > start_time + timeout:
            raise TimeoutError('Could not get public dns for instance. quitting.')
        instance = ec2.Instance(instance_id)
        dns = instance.public_dns_name
        if dns:
            return dns


def create(args, config):
    creds = get_aws_credentials()

    os.mkdir('.rollout')
    os.mkdir('.rollout/keys')

    session = Session(aws_access_key_id=creds.get('access_key'), aws_secret_access_key=creds.get('secret_key'))
    region = ask('What region do you want to use?', 'us-west-1')
    ami = ask('What AMI do you want to use?', 'ami-09d2fb69')
    size = ask('What instance type do you want to use?', 't2.micro')
    assert size in EC2_INSTANCE_TYPES

    ec2 = session.resource('ec2', region_name=region)
    ec2_client = session.client('ec2', region_name=region)

    keyname = create_key(ec2_client, args.service, region)

    subnets = get_subnets(ec2_client)
    instance = ec2.create_instances(
        ImageId=ami,
        MinCount=1,
        MaxCount=1,
        KeyName=keyname,
        InstanceType=size,
        SubnetId=subnets[0]['SubnetId'],
    )

    service = args.service

    public_dns_name = wait_for_public_dns_name(ec2, instance[0].id)
    data = {
        'hosts': [
            {
                    'username': 'ubuntu',
                    'instanceId': instance[0].id,
                    'host': public_dns_name,
                    'keyfile': get_keypath(keyname),
            }
        ],
        'services': {
            service: {
                'default': 'true',
            }
        },
    }

    yaml.dump(data, open('.rollout/config.yaml', 'w'), default_flow_style=False)

    print('Your instance is being created.')
    print('Instance Id: {}'.format(instance[0].id))


def destroy(args, config):
    rollout_dir = path.abspath('.rollout')
    prompt = \
"""Command will destroy:
- {folder}
- keypair
- ec2 hosts
Do you want to destroy these resources? [y/N]""".format(folder=rollout_dir)

    response = input(prompt)
    if not response.lower().startswith('y'):
        return

    shutil.rmtree(rollout_dir)
