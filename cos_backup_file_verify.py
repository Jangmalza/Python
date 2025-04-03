#!/usr/bin/env python3
import os
import sys
import socket
import subprocess
import hashlib
from datetime import datetime, timedelta

# 원본 디렉토리 및 COS 대상 버킷 설정
SOURCE_DIR = ""
#ex) /backup
TARGET_COS_BUCKET = ""
#ex) /cos://backup-777

# 현재 호스트명과 1일 전 날짜 (YYYYMMDD)
HOST_NAME = socket.gethostname()
DATE = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')

# 원본 백업 디렉토리 (예: /dblog/backup/20250222)
LOCAL_BACKUP_DIR = os.path.join(SOURCE_DIR, DATE)

# COS 업로드 대상 경로 (예: cos://backup-1324819375/호스트명/20250222)
REMOTE_TARGET_DIR = f"{TARGET_COS_BUCKET}/{HOST_NAME}/{DATE}"

# 원본 백업 디렉토리 존재 여부 확인
if not os.path.isdir(LOCAL_BACKUP_DIR):
    print(f"Error: Local backup directory '{LOCAL_BACKUP_DIR}' does not exist.")
    sys.exit(1)

# COS에 백업 디렉토리 업로드 (재귀적 옵션 사용)
result = subprocess.run(["coscli", "cp", "--recursive", LOCAL_BACKUP_DIR, REMOTE_TARGET_DIR])
if result.returncode != 0:
    print("Error: coscli cp command failed.")
    sys.exit(1)

# --- 해시 검증 단계 ---

def compute_local_file_hash(file_path):
    """로컬 파일의 MD5 해시값 계산"""
    hasher = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
    except Exception as e:
        print(f"Error: Failed to compute MD5 hash for {file_path}: {e}")
        sys.exit(1)
    return hasher.hexdigest()

def get_remote_hash(remote_file):
    """
    원격 파일의 MD5 해시값 추출을 위해 아래 명령어를 실행
    coscli hash "${COS_PATH}${file}" --type md5 2>/dev/null | grep -oE '[0-9a-f]{32}'
    """
    cmd = f'coscli hash "{remote_file}" --type md5 2>/dev/null | grep -oE \'[0-9a-f]{{32}}\''
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0 or not result.stdout.strip():
        print(f"Error: coscli hash command failed for {remote_file}")
        return None
    return result.stdout.strip()

def get_remote_file_list(remote_dir):
    """
    coscli ls -r 결과에서 헤더(첫 2줄)를 건너뛰고,
    KEY를 정제한 후 폴더(즉, '/'로 끝나는 항목)는 제외하고,
    마지막 3줄을 미포함시켜 파일 목록을 추출
    
    실행되는 명령어:
    coscli ls -r "remote_dir" | 
      awk -F'|' 'NR>2 { gsub(/^[ \t]+|[ \t]+$/, "", $1); 
                      if ($1 !~ /\/$/) { lines[++count]=$1 } } 
                END { for (i=1; i<=count-3; i++) print lines[i] }'
    """
    cmd = (
        f'coscli ls -r "{remote_dir}" | '
        f'awk -F\'|\' \'NR>2 {{ gsub(/^[ \\t]+|[ \\t]+$/, "", $1); '
        f'if ($1 !~ /\\/$/) {{ lines[++count]=$1 }} }} END {{ for (i=1; i<=count-3; i++) print lines[i] }}\''
    )
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print("Error: coscli ls command failed for remote target directory.")
        sys.exit(1)
    files = result.stdout.strip().splitlines()
    return files

# 원격 디렉토리 내 파일 목록 추출 (폴더 제외, 마지막 3줄 미포함)
remote_files_list = get_remote_file_list(REMOTE_TARGET_DIR)

# 로컬 파일 목록 추출 (디렉토리 트리 재귀 탐색)
local_files = []
for root, _, files in os.walk(LOCAL_BACKUP_DIR):
    for file in files:
        local_files.append(os.path.join(root, file))

# 업로드된 원격 파일 수와 로컬 파일 수 출력
print(f"업로드된 원격 파일 수: {len(remote_files_list)}")
print(f"로컬 파일 수: {len(local_files)}")

if len(remote_files_list) != len(local_files):
    print("Error: 업로드된 원격 파일 수와 로컬 파일 수가 일치하지 않습니다.")
    sys.exit(1)

# 파일별 해시 비교 및 검증 결과 출력
all_match = True
for local_file in local_files:
    relative_path = os.path.relpath(local_file, LOCAL_BACKUP_DIR)
    expected_remote_key = f"{HOST_NAME}/{DATE}/{relative_path}"
    if expected_remote_key not in remote_files_list:
        print(f"Error: Remote file {expected_remote_key} not found in ls output.")
        all_match = False
        continue

    remote_file = f"{REMOTE_TARGET_DIR}/{relative_path}"
    local_hash = compute_local_file_hash(local_file)
    remote_hash = get_remote_hash(remote_file)
    
    if remote_hash is None:
        print(f"Error: Could not retrieve remote hash for {relative_path}")
        all_match = False
        continue

    if local_hash == remote_hash:
        print(f"검증 완료: {relative_path} [MD5: {local_hash}]")
    else:
        print(f"Hash 불일치: {relative_path}\n  로컬: {local_hash}\n  원격: {remote_hash}")
        all_match = False

if all_match:
    print("모든 파일이 정상 검증되었습니다.")
    # 해시 검증 성공 시 원본 백업 디렉토리 삭제
    result = subprocess.run(["rm", "-rf", LOCAL_BACKUP_DIR])
    if result.returncode != 0:
        print("Error: Failed to delete local backup directory.")
        sys.exit(1)
    print("로컬 백업 디렉토리가 삭제되었습니다.")
else:
    print("오류: 일부 파일의 해시 검증에 실패하였습니다. 원본 백업 디렉토리는 삭제되지 않습니다.")

sys.exit(0)
