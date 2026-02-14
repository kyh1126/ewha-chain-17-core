#!/bin/bash
# BigQuery 쿼리 결과를 Gemini로 자동 요약하는 스크립트 (Shell 래퍼)
#
# 사용법:
#   ./scripts/summarize_with_gemini.sh <sql_file> [옵션]
#
# 예시:
#   ./scripts/summarize_with_gemini.sh templates/queries/01_tx_volume.sql
#   ./scripts/summarize_with_gemini.sh eth_query.sql sol_query.sql --type comparison

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
python3 "$SCRIPT_DIR/summarize_with_gemini.py" "$@"
