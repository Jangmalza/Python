from googleapiclient.discovery import build
from google.oauth2 import service_account

def stop_instance(project_id, instance_name):
    """
    주어진 Google Cloud 프로젝트 내 특정 Cloud SQL 인스턴스를 중지(activationPolicy=NEVER)합니다.
    """
    # 서비스 계정 키 파일을 사용하여 인증 정보를 생성합니다.
    credentials = service_account.Credentials.from_service_account_file('/path/api_key.json')
    # Google SQL Admin API 클라이언트를 초기화합니다.
    service = build('sqladmin', 'v1', credentials=credentials)

    try:
        # 'patch' 메서드를 호출하여 인스턴스의 설정을 업데이트합니다.
        # 여기서는 activationPolicy를 "NEVER"로 설정하여 인스턴스가 중지 상태로 유지되도록 합니다.
        request = service.instances().patch(
            project=project_id,
            instance=instance_name,
            body={
                "settings": {
                    "activationPolicy": "NEVER"
                }
            }
        )
        # 요청을 실행하고 API 응답을 받습니다.
        response = request.execute()
        print(f"성공적으로 인스턴스 {instance_name}를 중지했습니다: {response}")
    except Exception as e:
        print(f"인스턴스 {instance_name} 중지 실패: {e}")

if __name__ == "__main__":
    # Google Cloud 프로젝트 ID
    PROJECT_ID = ""
    # 중지할 인스턴스 이름에 사용될 접두사
    INSTANCE_PREFIX = ""
    # 인스턴스 이름 생성 시 사용할 시작 인덱스
    START_INDEX = 1
    # 인스턴스 이름 생성 시 사용할 끝 인덱스
    END_INDEX = 1

    # 인스턴스 이름 리스트를 생성합니다. (예: myinstance-001)
    instance_names = [f"{INSTANCE_PREFIX}-{i:03}" for i in range(START_INDEX, END_INDEX + 1)]

    print("다음 인스턴스들이 중지됩니다:")
    for instance in instance_names:
        print(instance)
    print()

    confirmation = input("정말로 이 인스턴스들을 중지하시겠습니까? (yes/no): ")
    if confirmation.lower() == 'yes':
        for instance_name in instance_names:
            stop_instance(PROJECT_ID, instance_name)
    else:
        print("작업이 취소되었습니다.")
