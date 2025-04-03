import boto3

dms_client = boto3.client('dms')

task_arns = [
    'arn:aws:dms:us-east-1:123456789012:task:my-task-1'
]

for task_arn in task_arns:
    response = dms_client.start_task(
        ReplicationTaskArn=task_arn
    )
    print(f"Task '{task_arn}' 실행 시작: {response['ResponseMetadata']['RequestId']}")
