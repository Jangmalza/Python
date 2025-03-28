from googleapiclient.discovery import build
from google.oauth2 import service_account

def start_instance(project_id, instance_name):
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
        # 성공 메시지와 응답 내용을 출력합니다.
        print(f"성공적으로 인스턴스 {instance_name}를 중지했습니다: {response}")
    except Exception as e:
        # 예외 발생 시 에러 메시지를 출력합니다.
        print(f"인스턴스 {instance_name} 중지 실패: {e}")

if __name__ == "__main__":
    # Google Cloud 프로젝트 ID를 설정합니다.
    PROJECT_ID = ""
    # 중지할 인스턴스 이름에 사용될 접두사를 설정합니다.
    INSTANCE_PREFIX = ""
    # 인스턴스 이름 생성 시 사용할 시작 인덱스입니다.
    START_INDEX = 1
    # 인스턴스 이름 생성 시 사용할 끝 인덱스입니다.
    END_INDEX = 1

    # 인스턴스 이름 리스트를 생성합니다.
    # 예를 들어, INSTANCE_PREFIX가 "myinstance"일 경우 "myinstance-001" 형식으로 생성됩니다.
    instance_names = [f"{INSTANCE_PREFIX}-{i:03}" for i in range(START_INDEX, END_INDEX + 1)]

    # 중지될 인스턴스 목록을 출력합니다.
    print("다음 인스턴스들이 중지됩니다:")
    for instance in instance_names:
        print(instance)
    print()

    # 사용자에게 인스턴스 중지 작업 진행 여부를 확인합니다.
    confirmation = input("정말로 이 인스턴스들을 중지하시겠습니까? (yes/no): ")

    # 사용자가 'yes'를 입력한 경우에만 중지 작업을 진행합니다.
    if confirmation.lower() == 'yes':
        for instance_name in instance_names:
            start_instance(PROJECT_ID, instance_name)
    else:
        print("작업이 취소되었습니다.")
