import boto3
import json

def delete_rds_instances_by_tag(tag_key, tag_value):
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
        # 모든 RDS 인스턴스에 대해 태그 정보 확인
        response = rds_client.describe_db_instances()
        instances = response['DBInstances']
        # 태그 키와 값이 일치하는 인스턴스 필터링 및 삭제
        for instance in instances:
            instance_id = instance['DBInstanceIdentifier']
            response = rds_client.list_tags_for_resource(ResourceName=instance['DBInstanceArn'])
            tags = response['TagList']
            for tag in tags:
                if tag['Key'] == tag_key and tag['Value'] == tag_value:
                    print(f"Deleting RDS instance: {instance_id}")
                    rds_client.delete_db_instance(
                        DBInstanceIdentifier=instance_id,
                        SkipFinalSnapshot=True
                    )
                    break  # 동일한 인스턴스에 대해 중복 삭제를 방지하기 위해 루프 종료

    except Exception as e:
        print(f"Error deleting RDS instances by tag: {e}")

# 실행 예시
if __name__ == "__main__":
    tag_key = ''  # 추가할 태그 키
    tag_value = ''  # 추가할 태그 값
    delete_rds_instances_by_tag(tag_key, tag_value)
