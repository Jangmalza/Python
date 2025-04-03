import boto3
import json

def tag_rds_instances_by_keyword(keyword, tag_key, tag_value):
    # AWS 리전 및 인증 정보 설정
    with open('path', 'r') as f:
    #with open('C:\\path\aws_credentials.json', 'r') as f:
        credentials = json.load(f)

    account_name = ""
    account_credentials = credentials[account_name]

    region = account_credentials['region']
    aws_access_key_id = account_credentials['access_key_id']
    aws_secret_access_key = account_credentials['secret_access_key']

    # Boto3 RDS 클라이언트 생성
    rds_client = boto3.client('rds', region_name=region,
                              aws_access_key_id=aws_access_key_id,
                              aws_secret_access_key=aws_secret_access_key)

    try:
        # 특정 키워드를 포함하는 RDS 인스턴스 필터링
        response = rds_client.describe_db_instances()
        instances = response['DBInstances']
        filtered_instances = [instance for instance in instances if keyword in instance['DBInstanceIdentifier']]

        # 필터링된 RDS 인스턴스에 태그 추가
        for instance in filtered_instances:
            instance_id = instance['DBInstanceIdentifier']
            print(f"Tagging RDS instance: {instance_id}")
            rds_client.add_tags_to_resource(
                ResourceName=instance['DBInstanceArn'],
                Tags=[
                    {
                        'Key': tag_key,
                        'Value': tag_value
                    }
                ]
            )

    except Exception as e:
        print(f"Error tagging RDS instances: {e}")

# 실행 예시
if __name__ == "__main__":
    keyword = ""  # 클러스터 ID에 포함될 키워드
    tag_key = ''  # 추가할 태그 키
    tag_value = ''  # 추가할 태그 값
    tag_rds_instances_by_keyword(keyword, tag_key, tag_value)
