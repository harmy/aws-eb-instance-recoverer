#!/usr/bin/python

import boto3
import os
import datetime

environments = ['gemininp-appapi', 'gemininp-appapi2', 'gmp-api-qacwjtfu']
region = "us-east-1"


def main():
    client = boto3.client('elasticbeanstalk', region_name=region)
    for environment_name in environments:
        next_token = ''
        instance_health = []
        while next_token is not None:
            if next_token:
                response = client.describe_instances_health(
                    EnvironmentName=environment_name,
                    AttributeNames=['System'],
                    NextToken = next_token
                )
            else:
                response = client.describe_instances_health(
                    EnvironmentName=environment_name,
                    AttributeNames=['System']
                )
            next_token = response.get('NextToken')
            instance_health.extend(response['InstanceHealthList'])

        for item in instance_health:
            #print('checking {}, System Idle:{}'.format(item['InstanceId'], item['System']['CPUUtilization']['Idle']))
            if item['System']['CPUUtilization']['Idle'] == 100:
                print('[{}] restarting httpd on {}...'.format(datetime.datetime.now(), item['InstanceId']))
                os.system('eb ssh {} -i {} -c "sudo service httpd restart"'.format(environment_name, item['InstanceId']))

if __name__ == '__main__':
    main()