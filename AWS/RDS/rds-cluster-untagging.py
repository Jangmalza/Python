import boto3
import json

def untag_rds_instances_by_keyword(keyword, tag_key):
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
        # 특정 키워드를 포함하는 RDS 클러스터 필터링
        response = rds_client.describe_db_clusters()
        clusters = response['DBClusters']
        filtered_clusters = [cluster for cluster in clusters if keyword in cluster['DBClusterIdentifier']]

        # 필터링된 RDS 클러스터에서 태그 제거
        for cluster in filtered_clusters:
            cluster_id = cluster['DBClusterIdentifier']
            print(f"Untagging RDS cluster: {cluster_id}")
            rds_client.remove_tags_from_resource(
                ResourceName=cluster['DBClusterArn'],
                TagKeys=[tag_key]
            )

    except Exception as e:
        print(f"Error untagging RDS clusters: {e}")

# 실행 예시
if __name__ == "__main__":
    keyword = ""  # 클러스터 ID에 포함될 키워드
    tag_key = ''  # 삭제할 태그 키
    untag_rds_instances_by_keyword(keyword, tag_key)
