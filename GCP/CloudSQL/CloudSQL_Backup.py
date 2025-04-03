from googleapiclient.discovery import build
from google.oauth2 import service_account

def create_backup(project_id, instance_name):
    """
    Google Cloud SQL 인스턴스의 백업을 생성하는 함수
    :param project_id: GCP 프로젝트 ID
    :param instance_name: 백업을 생성할 Cloud SQL 인스턴스 이름
    """
    # 서비스 계정 인증 (JSON 키 파일 경로를 지정해야 함)
    credentials = service_account.Credentials.from_service_account_file('path')  
    service = build('sqladmin', 'v1', credentials=credentials)

    try:
        # 백업 생성 요청 실행
        request = service.backupRuns().insert(
            project=project_id,
            instance=instance_name,
            body={}  # 추가적인 설정이 필요 없을 경우 빈 body 사용
        )
        response = request.execute()
        print(f"성공: 인스턴스 '{instance_name}'의 백업이 생성되었습니다.\n응답: {response}")

    except Exception as e:
        print(f"오류: 인스턴스 '{instance_name}' 백업 생성 실패\n오류 메시지: {e}")

if __name__ == "__main__":

    #Google Cloud 프로젝트 ID 입력 (반드시 수정 필요)
    PROJECT_ID = ""

    #백업할 Cloud SQL 인스턴스의 접두어 입력 (예: gamedb)
    INSTANCE_PREFIX = ""

    #백업할 인스턴스 범위 지정 (예: START_INDEX=1, END_INDEX=10 → gamedb-001 ~ gamedb-010 백업)
    START_INDEX = 1
    END_INDEX = 1

    #백업 대상 인스턴스 이름 목록 생성
    instance_names = [f"{INSTANCE_PREFIX}-{i:03}" for i in range(START_INDEX, END_INDEX + 1)]

    # 🔍 백업될 인스턴스 목록 출력
    print("📋 다음 인스턴스들의 백업이 생성됩니다:")
    for instance in instance_names:
        print(f"- {instance}")

    #백업 진행 여부 확인
    confirmation = input("⚠️ 정말로 이 인스턴스들의 백업을 생성하시겠습니까? (yes/no): ")

    if confirmation.lower() == 'yes':
        for instance_name in instance_names:
            create_backup(PROJECT_ID, instance_name)
    else:
        print("🚫 작업이 취소되었습니다.")
