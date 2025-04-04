import boto3
import pymysql
import json
import re

def get_secret(secret_name, region_name):
    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager', region_name=region_name)
    get_secret_value_response = client.get_secret_value(SecretId=secret_name)

    if 'SecretString' in get_secret_value_response:
        secret = get_secret_value_response['SecretString']
    else:
        secret = get_secret_value_response['SecretBinary']

    return secret

def download_routines_to_s3(db_config, s3_prefix):
    host = db_config['host']
    pos = host.find('.')
    db_folder=host[:pos]
    db_name='test'
    port = int(db_config['port'])
    user = db_config['username']
    password = db_config['password']
    s3_bucket = "game-log-hhs"  # 대상 S3 버킷 이름
    # RDS 데이터베이스 연결
    conn = pymysql.connect(host=host, port=port, user=user, password=password, database=db_name)
    cursor = conn.cursor()

    # 쿼리 실행
    query = f"""SELECT '{db_folder}' as db_name,routine_schema, routine_name, routine_type, replace(replace(routine_definition,'\r','||'),'\n','||') as routine_definition 
                FROM information_schema.routines 
                WHERE routine_schema in ('test')
                INTO OUTFILE S3 's3://playwith-test/gamedb_meta/routines/routines_{db_folder}'
                FORMAT TEXT HEADER
                FIELDS TERMINATED BY ',' ESCAPED BY '"'
                LINES TERMINATED BY '\n'
                OVERWRITE ON;"""
    cursor.execute(query)
    routines_data = cursor.fetchall()

    query = f"""select '{db_folder}' as db_name,t.table_schema, t.table_name, c.column_name, c.ordinal_position, c.is_nullable, c.column_type
                from information_schema.columns c, 
                     information_schema.tables  t
                where t.table_schema ='test'
                and t.table_name = c.table_name
                order by table_schema, table_name, ordinal_position
                INTO OUTFILE S3 's3://playwith-test/gamedb_meta/columns/columns_{db_folder}'
                FORMAT TEXT HEADER
                FIELDS TERMINATED BY ',' ESCAPED BY '"'
                LINES TERMINATED BY '\n'
                OVERWRITE ON;"""
    cursor.execute(query)
    columns_data = cursor.fetchall()
    
    cursor.close()
    conn.close()
    print(db_folder);
    # 쿼리 결과를 S3로 업로드
    s3 = boto3.client('s3')
    s3_key = f"{s3_prefix}/{db_name}/routines/routines.csv"  # S3 업로드 경로
    routines_csv = "\n".join([",".join(row) for row in routines_data])
    s3.put_object(Bucket=s3_bucket, Key=s3_key, Body=routines_csv)
    
    s3_key = f"{s3_prefix}/{db_name}/columns/columns.csv"  # S3 업로드 경로
    columns_csv = "\n".join([",".join(row) for row in columns_data])
    s3.put_object(Bucket=s3_bucket, Key=s3_key, Body=columns_csv)
    #print(host,' 처리완료')

def get_secrets_with_prefix(prefix, region_name):
    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager', region_name=region_name)

    secrets = []

    paginator = client.get_paginator('list_secrets')
    for page in paginator.paginate():
        for secret in page['SecretList']:
            if secret['Name'].startswith(prefix):
                secrets.append(secret)

    return secrets

def create_metatable(region_name):
    sql_statements = [
        """drop table if exists routines;""",
        """drop table if exists columns;""",
        """
           create external table routines
           (db_name string,
            routine_schema string,
            routine_name string,
            routine_type string,
            routine_definition string)
           ROW FORMAT DELIMITED FIELDS TERMINATED BY ','
           LOCATION 's3://playwith-test/gamedb_meta/routines/'
           TBLPROPERTIES ('skip.header.line.count'='1');
        """,
        """
           create external table columns
           (db_name string,
            table_schema string,
            table_name string,
            column_name string,
            ordinal_position bigint,
            is_nullable string,
            column_type string)
            ROW FORMAT DELIMITED FIELDS TERMINATED BY ','
            LOCATION 's3://playwith-test/gamedb_meta/columns/'
            TBLPROPERTIES ('skip.header.line.count'='1');
        """
    ]
    session = boto3.session.Session()
    client = session.client(service_name='athena', region_name=region_name)
    for sql_statement in sql_statements:
        print(sql_statement)
        response = client.start_query_execution(
            QueryString=sql_statement,
            QueryExecutionContext={
                'Database': 'gamedb-meta'  # Replace with your Athena database name
            },
            ResultConfiguration={
                'OutputLocation': 's3://playwith-test/gamedb_meta/'  # Replace with your Athena query results bucket
            }
        )

    query_execution_id = response['QueryExecutionId']
    print(f"테이블생성또는변경완료")


def main():
    secret_prefix = "gamedb"  # 원하는 prefix 값
    region_name = "ap-northeast-2"

    secrets_with_prefix = get_secrets_with_prefix(secret_prefix, region_name)

    db_configs = []

    for secret in secrets_with_prefix:
        secret_name = secret['Name']
        secret_value = get_secret(secret_name, region_name)
        db_info = json.loads(secret_value)
        db_user = db_info['username']
        db_password = db_info['password']
        db_port = db_info['port']
        db_host = db_info['host']

        db_config = {
            'host': db_host,
            'port': int(db_port),
            'username': db_user,
            'password': db_password
        }
        db_configs.append(db_config)

    # 테이블 업데이트할 정보
    s3_prefix = 'gamedb_meta'  # S3 버킷 내 폴더 경로
    for db_config in db_configs:
        download_routines_to_s3(db_config, s3_prefix)

    #아테나 테이블생성 
    create_metatable(region_name)


if __name__ == "__main__":
    main()

