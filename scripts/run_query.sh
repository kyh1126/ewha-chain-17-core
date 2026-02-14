#!/bin/bash
# BigQuery 쿼리 실행 자동화 스크립트 (Shell 래퍼)
#
# 사용법:
#   ./scripts/run_query.sh <sql_file> [옵션]
#
# 예시:
#   ./scripts/run_query.sh templates/sql/01_basic_exploration.sql
#   ./scripts/run_query.sh my_query.sql --output results.csv

set -e  # 에러 발생 시 중단

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Python 경로 확인
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}오류: python3가 설치되지 않았습니다.${NC}"
    exit 1
fi

# 스크립트 디렉토리로 이동
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

# Python 스크립트 실행
python3 "$SCRIPT_DIR/run_query.py" "$@"
