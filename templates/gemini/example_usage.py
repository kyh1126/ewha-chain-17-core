"""
Gemini API 사용 예시: BigQuery 결과와 연동
"""

import os
import sys

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv가 없으면 환경 변수에서 직접 가져옴

from google.cloud import bigquery

# prompt_template.py가 같은 디렉토리에 있으므로 경로 추가
# 다른 위치에서 실행 시: python -m templates.gemini.example_usage (프로젝트 루트에서)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from prompt_template import generate_weekly_summary, generate_comparison_insight


# BigQuery 클라이언트 초기화
client = bigquery.Client(project=os.getenv("GCP_PROJECT_ID"))


def fetch_tx_volume_data(days: int = 7) -> dict:
    """
    BigQuery에서 거래량 데이터 조회
    """
    query = f"""
    SELECT
      DATE(block_timestamp) AS date,
      COUNT(*) AS tx_count
    FROM
      `bigquery-public-data.crypto_ethereum.transactions`
    WHERE
      block_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL {days} DAY)
      AND receipt_status = 1
    GROUP BY
      date
    ORDER BY
      date DESC
    LIMIT 7
    """
    
    query_job = client.query(query)
    results = query_job.result()
    
    # 결과를 딕셔너리로 변환
    data = []
    for row in results:
        data.append({
            "date": str(row.date),
            "tx_count": row.tx_count
        })
    
    return {"ethereum_tx_volume": data}


def main():
    """
    메인 실행 함수: BigQuery 데이터 조회 → Gemini 요약 생성
    """
    print("1. BigQuery에서 데이터 조회 중...")
    eth_data = fetch_tx_volume_data(days=7)
    
    print("2. Gemini로 요약 생성 중...")
    summary = generate_weekly_summary(eth_data)
    
    print("\n=== 생성된 요약 ===")
    print(summary)
    
    # 파일로 저장 (선택)
    with open("weekly_summary.txt", "w", encoding="utf-8") as f:
        f.write(summary)
    print("\n요약이 weekly_summary.txt에 저장되었습니다.")


if __name__ == "__main__":
    # 환경 변수 확인
    if not os.getenv("GEMINI_API_KEY"):
        print("오류: GEMINI_API_KEY 환경 변수를 설정해주세요.")
        print("export GEMINI_API_KEY='your-api-key'")
        exit(1)
    
    if not os.getenv("GCP_PROJECT_ID"):
        print("오류: GCP_PROJECT_ID 환경 변수를 설정해주세요.")
        print("export GCP_PROJECT_ID='your-project-id'")
        exit(1)
    
    main()
