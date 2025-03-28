import boto3
import json

def start_rds_clusters_by_tag(tag_key, tag_value):
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
        # 모든 RDS 클러스터에 대해 태그 정보 확인
        response = rds_client.describe_db_clusters()
        clusters = response['DBClusters']

        # 태그 키와 값이 일치하는 클러스터 필터링 및 시작
        for cluster in clusters:
            cluster_id = cluster['DBClusterIdentifier']
            cluster_status = cluster['Status']
            if cluster_status == 'stopped':
                response = rds_client.list_tags_for_resource(ResourceName=cluster['DBClusterArn'])
                tags = response['TagList']
                for tag in tags:
                    if tag['Key'] == tag_key and tag['Value'] == tag_value:
                        print(f"Starting RDS cluster: {cluster_id}")
                        rds_client.start_db_cluster(DBClusterIdentifier=cluster_id)
                        break  # 동일한 클러스터에 대해 중복 시작을 방지하기 위해 루프 종료

    except Exception as e:
        print(f"Error starting RDS clusters by tag: {e}")

# 실행 예시
if __name__ == "__main__":
    tag_key = ''  # 추가할 태그 키
    tag_value = ''  # 추가할 태그 값
    start_rds_clusters_by_tag(tag_key, tag_value)
