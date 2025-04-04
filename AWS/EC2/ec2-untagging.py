import boto3
import json

def tag_ec2_instances_by_tag_value(tag_key, tag_value_contains, new_tag_key, new_tag_value):
    # AWS 리전 및 인증 정보 설정
    with open('path', 'r') as f:
        credentials = json.load(f)

    account_name = ""
    account_credentials = credentials[account_name]

    region = account_credentials['region']
    aws_access_key_id = account_credentials['access_key_id']
    aws_secret_access_key = account_credentials['secret_access_key']

    # Boto3 EC2 클라이언트 생성
    ec2_client = boto3.client('ec2', region_name=region,
                              aws_access_key_id=aws_access_key_id,
                              aws_secret_access_key=aws_secret_access_key)

    try:
        # 특정 태그 키의 값에 특정 문자열이 포함된 EC2 인스턴스 필터링
        response = ec2_client.describe_instances(Filters=[
            {
                'Name': 'tag-key',
                'Values': [tag_key]
            },
            {
                'Name': 'tag-value',
                'Values': ['*' + tag_value_contains + '*']
            }
        ])

        # 필터링된 EC2 인스턴스
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                instance_id = instance['InstanceId']
                print(f"Untagging EC2 instance: {instance_id}")

                # 특정 태그 삭제
                ec2_client.delete_tags(
                    Resources=[instance_id],
                    Tags=[
                        {
                            'Key': new_tag_key,
                            'Value': new_tag_value
                        }
                    ]
                )

    except Exception as e:
        print(f"Error untagging EC2 instances: {e}")

# 실행 예시
if __name__ == "__main__":
    tag_key = ''  # 기존 태그 키
    tag_value_contains = ''  # 기존 태그 값에 포함된 문자열
    new_tag_key = ''  # 새로운 태그 키
    new_tag_value = ''  # 새로운 태그 값
    tag_ec2_instances_by_tag_value(tag_key, tag_value_contains, new_tag_key, new_tag_value)
