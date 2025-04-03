import boto3
import csv
import datetime

now = datetime.datetime.now()
filename_prefix = now.strftime("%Y_%m_%d")

# AWS 계정 자격 증명
session = boto3.Session(
    aws_access_key_id='',
    aws_secret_access_key='',
)

# 모든 사용 가능한 리전을 가져옵니다.
# ex) ap-south-1
region_codes = [
    "ap-northeast-2"
]

# 인스턴스 세부 정보를 저장할 리스트
instance_details = []

# 각 리전을 반복합니다.
for region_code in region_codes:
    print(f"EC2 인스턴스 목록을 {region_code} 리전에서 가져옵니다.")
    # 해당 리전에 대한 EC2 클라이언트를 만듭니다.
    ec2_client = session.client('ec2', region_name=region_code)
    # 리전의 인스턴스를 설명합니다.
    instances = ec2_client.describe_instances()
    # 인스턴스 세부 정보를 추출합니다.
    for reservation in instances['Reservations']:
        for instance in reservation['Instances']:
            instance_id = instance['InstanceId']
            name = ''
            for tag in instance['Tags']:
                if tag['Key'] == 'Name':
                    name = tag['Value']
                    break
            private_ip_address = instance.get('PrivateIpAddress', '')
            public_ip_address = instance.get('PublicIpAddress', '')
            key_pair_name = instance.get('KeyName', '')
            instance_details.append({
                'Name': name,
                'Instance ID': instance_id,
                'Private IP': private_ip_address,
                'Public IP': public_ip_address,
                'Region Code': region_code,
                'Key Pair Name': key_pair_name,
            })

csv_filename = f"{filename_prefix}_kr_ec2_list.csv"
with open(csv_filename, 'w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=['Name', 'Instance ID', 'Private IP', 'Public IP', 'Region Code', 'Key Pair Name'])
    writer.writeheader()
    for instance in instance_details:
        writer.writerow(instance)

print(f"모든 리전의 EC2 인스턴스 세부 정보가 {csv_filename} 파일에 기록되었습니다.")