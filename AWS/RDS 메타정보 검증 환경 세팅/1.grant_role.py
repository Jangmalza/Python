import subprocess
import json
import re
import time

# IAM 역할 이름
role_name = "DBMetaRole"

# IAM 역할 생성 명령어 실행
create_role_command = f"aws iam create-role --role-name {role_name} --assume-role-policy-document '{{\"Version\":\"2012-10-17\",\"Statement\":[{{\"Effect\":\"Allow\",\"Principal\":{{\"Service\":\"rds.amazonaws.com\"}},\"Action\":\"sts:AssumeRole\"}}]}}'"
subprocess.run(create_role_command, shell=True, check=True)

# S3 버킷 및 RDS 데이터베이스 접근 정책 ARN
s3_policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"  # 여기서 AmazonS3FullAccess를 사용하여 쓰기 권한을 추가합니다.
rds_policy_arn = "arn:aws:iam::aws:policy/AmazonRDSReadOnlyAccess"
glue_policy_arn ="arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole"

# IAM 역할에 정책 부착
attach_policy_command = f"aws iam attach-role-policy --role-name {role_name} --policy-arn {s3_policy_arn}"
subprocess.run(attach_policy_command, shell=True, check=True)

attach_policy_command = f"aws iam attach-role-policy --role-name {role_name} --policy-arn {rds_policy_arn}"
subprocess.run(attach_policy_command, shell=True, check=True)


# 시크릿 매니저 읽기 권한 부여
secrets_policy_arn = "arn:aws:iam::aws:policy/SecretsManagerReadWrite"
attach_policy_command = f"aws iam attach-role-policy --role-name {role_name} --policy-arn {secrets_policy_arn}"
subprocess.run(attach_policy_command, shell=True, check=True)

print('Role DBMetaRole 생성중으로 완료될때까지 30초대기!') 
time.sleep(30)

# 특정 프리픽스
prefix = ""

# JSON 파일로부터 디비 정보 읽기
with open('db_credentials.json') as f:
    db_credentials = json.load(f)

# DB 클러스터 엔드포인트 조회 명령어 실행
describe_endpoint_command = "aws rds describe-db-cluster-endpoints --filters Name=db-cluster-endpoint-type,Values=writer"
result = subprocess.run(describe_endpoint_command, shell=True, check=True, capture_output=True, text=True)
endpoints = json.loads(result.stdout)

# 디비 클러스터 식별자를 숫자로 정렬
def get_cluster_identifier_key(endpoint):
    match = re.search(r'\d+', endpoint['DBClusterIdentifier'])
    return int(match.group()) if match else 0

sorted_endpoints = sorted(endpoints['DBClusterEndpoints'], key=get_cluster_identifier_key)

for endpoint in sorted_endpoints:
    cluster_identifier = endpoint['DBClusterIdentifier']
     # 특정 프리픽스를 가지는 클러스터만 처리
    if not cluster_identifier.startswith(prefix):
        continue
    
    # 클러스터의 엔드포인트 가져오기
    host = endpoint['Endpoint']
    db_info = db_credentials.get(cluster_identifier, None)
    if db_info is None:
        print(f"디비 '{cluster_identifier}'에 대한 정보가 없습니다.")
        continue
    
    # 이미 IAM 역할이 할당되어 있는 경우 스킵
    describe_role_command = f"aws rds describe-db-cluster-roles --db-cluster-identifier {cluster_identifier}"
    role_result = subprocess.run(describe_role_command, shell=True, capture_output=True, text=True)
    if role_name in role_result.stdout:
        print(f"디비 클러스터 '{cluster_identifier}'에는 이미 IAM 역할이 할당되어 있습니다. 스킵합니다.")
        continue
    
    associate_role_command = f"aws rds add-role-to-db-cluster --db-cluster-identifier {cluster_identifier} --role-arn arn:aws:iam::181136804328:role/{role_name}"
    print(associate_role_command)
    subprocess.run(associate_role_command, shell=True, check=True)

print("IAM 역할 생성 및 설정 완료")

