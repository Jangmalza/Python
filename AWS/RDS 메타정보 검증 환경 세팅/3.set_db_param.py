import subprocess
import json
import re

# 특정 프리픽스
prefix = "gamedb"

# JSON 파일로부터 디비 정보 읽기
with open('db_credentials.json') as f:
    db_credentials = json.load(f)

# DB 클러스터 엔드포인트 조회 명령어 실행
describe_instance_command = "aws rds describe-db-instances --filters Name=engine,Values=aurora-mysql"
result = subprocess.run(describe_instance_command, shell=True, check=False, capture_output=True, text=True)
instances = json.loads(result.stdout)

# 디비 인스턴스 식별자를 숫자로 정렬
def get_instance_identifier_key(instance):
    match = re.search(r'\d+', instance['DBInstanceIdentifier'])
    return int(match.group()) if match else 0

sorted_instances = sorted(instances['DBInstances'], key=get_instance_identifier_key)

for instance in sorted_instances:
    cluster_identifier=instance['DBClusterIdentifier']
    instance_identifier = instance['DBInstanceIdentifier']
     # 특정 프리픽스를 가지는 클러스터만 처리
    if not instance_identifier.startswith(prefix):
        continue
   
    # 디비 파라미터 그룹 변경 명령어 실행
    db_parameter_group_name = "aurora-mysql80-cluster"  # 실제 파라미터 그룹 이름으로 변경
    modify_db_cluster_command = f"aws rds modify-db-cluster --db-cluster-identifier {cluster_identifier} --db-cluster-parameter-group-name {db_parameter_group_name}"
    result=subprocess.run(modify_db_cluster_command, shell=True, check=False)
    print(f"클러스터 '{cluster_identifier}' 파라미터그룹 적용 완료") 
    # RDS 인스턴스 리붓 명령어 실행
    reboot_db_instance_command = f"aws rds reboot-db-instance --db-instance-identifier {instance_identifier}"
    result=subprocess.run(reboot_db_instance_command, shell=True, check=False)
        
    print(f"인스턴스 '{instance_identifier}' 리붓 시작")

print("작업이 완료되었습니다.리붓작업완료여부는콘솔에서 확인해주세요.")

