import boto3
import json

def upgrade_aurora_cluster_engine(tag_key, tag_value, target_engine_version):
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
        # 특정 태그 값을 가지고 있는 RDS 클러스터 찾기
        response = rds_client.describe_db_clusters()
        clusters = response['DBClusters']
        filtered_clusters = [cluster for cluster in clusters if any(tag.get('Key') == tag_key and tag.get('Value') == tag_value for tag in cluster.get('TagList', []))]
        # 찾은 클러스터들의 오로라 엔진 업그레이드
        for cluster in filtered_clusters:
            cluster_id = cluster['DBClusterIdentifier']
            print(f"Upgrading Aurora engine for RDS cluster: {cluster_id}")
            rds_client.modify_db_cluster(
                DBClusterIdentifier=cluster_id,
                EngineVersion=target_engine_version,
                ApplyImmediately=True
            )
            print(f"Aurora engine upgrade initiated for RDS cluster: {cluster_id}")

    except Exception as e:
        print(f"Error upgrading Aurora cluster engines: {e}")

# 실행 예시
if __name__ == "__main__":
    tag_key = ''  # 추가할 태그 키
    tag_value = ''  # 추가할 태그 값
    target_engine_version = '8.0.mysql_aurora.3.04.0'  # 업그레이드할 엔진 버전
    upgrade_aurora_cluster_engine(tag_key, tag_value, target_engine_version)
