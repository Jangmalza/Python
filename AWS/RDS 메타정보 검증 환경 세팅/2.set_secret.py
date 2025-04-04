import subprocess
import json
import re

# 특정 프리픽스
prefix = "gamedb"

# JSON 파일로부터 디비 정보 읽기
with open('db_credentials.json') as f:
    db_credentials = json.load(f)

# Describe DB Cluster Endpoints 명령어 실행
describe_endpoint_command = "aws rds describe-db-cluster-endpoints --filters Name=db-cluster-endpoint-type,Values=writer"
result = subprocess.run(describe_endpoint_command, shell=True, check=True, capture_output=True, text=True)
endpoints = json.loads(result.stdout)

# 디비 클러스터 엔드포인트를 숫자 부분을 기준으로 정렬
def get_cluster_identifier_key(endpoint):
    match = re.search(r'\d+', endpoint['DBClusterIdentifier'])
    return int(match.group()) if match else 0

sorted_endpoints = sorted(endpoints['DBClusterEndpoints'], key=get_cluster_identifier_key)

for endpoint in sorted_endpoints:
    cluster_identifier = endpoint['DBClusterIdentifier']

    # 특정 프리픽스를 가지는 클러스터만 처리
    if not cluster_identifier.startswith(prefix):
        continue

    # 시크릿 이름 생성
    secret_name = f"{cluster_identifier}"

    # 시크릿 생성 여부 확인
    check_secret_command = f"aws secretsmanager describe-secret --secret-id {secret_name}"
    check_result = subprocess.run(check_secret_command, shell=True, capture_output=True, text=True)

    # 클러스터의 엔드포인트 가져오기
    print(endpoint)
    host = endpoint['Endpoint']
    db_info = db_credentials.get(cluster_identifier, None)
    if db_info is None:
        print(f"디비 '{cluster_identifier}'에 대한 정보가 없습니다.")
        continue

    db_username = db_info['username']
    db_password = db_info['password']

    # 이미 시크릿이 존재하는 경우 업데이트
    if check_result.returncode == 0:
        print(f"시크릿 '{secret_name}'을(를) 업데이트합니다.")
        update_secret_command = f"aws secretsmanager update-secret --secret-id {secret_name} --secret-string '{{\"username\":\"{db_username}\",\"password\":\"{db_password}\",\"host\":\"{host}\",\"port\":\"3306\",\"dbClusterIdentifier\":\"{cluster_identifier}\"}}'"
        subprocess.run(update_secret_command, shell=True, check=True)
        print(f"시크릿 '{secret_name}' 업데이트 완료")
    else:
        print(f"시크릿 '{secret_name}'을(를) 생성합니다.")

# 시크릿 생성 명령어 실행
        create_secret_command = f"aws secretsmanager create-secret --name {secret_name} --description 'Secret for {cluster_identifier} database' --secret-string '{{\"username\":\"{db_username}\",\"password\":\"{db_password}\",\"host\":\"{host}\",\"port\":\"3306\",\"dbClusterIdentifier\":\"{cluster_identifier}\"}}'"
        subprocess.run(create_secret_command, shell=True, check=True)
        print(f"시크릿 '{secret_name}' 생성 완료")

print("작업이 완료되었습니다.")

