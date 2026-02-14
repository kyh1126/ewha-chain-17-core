"""
Gemini API를 사용한 온체인 데이터 요약 생성 템플릿
"""

import os
import json
import google.generativeai as genai
from typing import Dict, Any

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv가 없으면 환경 변수에서 직접 가져옴


# API 키 설정 (환경 변수에서 가져오기)
# .env 파일 또는 export GEMINI_API_KEY="your-api-key-here"
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


def generate_weekly_summary(query_results: Dict[str, Any]) -> str:
    """
    주간 온체인 데이터 요약 생성
    
    Args:
        query_results: BigQuery 쿼리 결과 딕셔너리
            예: {
                'tx_volume': {...},
                'active_addresses': {...},
                'fee_trends': {...}
            }
    
    Returns:
        생성된 요약 텍스트
    """
    
    model = genai.GenerativeModel('gemini-2.0-flash')
    
    data_str = json.dumps(query_results, indent=2, ensure_ascii=False, default=str)
    
    prompt = f"""
당신은 블록체인 데이터 분석가입니다. 다음 온체인 데이터를 기반으로 
기관 투자자/증권사 관점에서 읽을 수 있는 주간 요약 리포트를 작성해주세요.

## 데이터 요약
{data_str}

## 요구사항
1. 핵심 지표 3가지를 한 문장씩 요약
2. 전주 대비 변화율 언급 (가능한 경우)
3. 주목할 만한 이상 징후나 패턴 발견 시 언급
4. 전문적이지만 이해하기 쉬운 문체 사용
5. 총 3-5문장으로 구성

## 출력 형식
[주간 요약]
(내용)

[주요 변화]
(내용)

[이상 징후]
(내용 또는 "특별한 이상 징후 없음")
"""
    
    response = model.generate_content(prompt)
    return response.text


def generate_comparison_insight(
    ethereum_data: Dict[str, Any],
    solana_data: Dict[str, Any]
) -> str:
    """
    Ethereum vs Solana 비교 인사이트 생성
    
    Args:
        ethereum_data: Ethereum 네트워크 데이터
        solana_data: Solana 네트워크 데이터
    
    Returns:
        비교 분석 텍스트
    """
    
    model = genai.GenerativeModel('gemini-2.0-flash')
    
    eth_str = json.dumps(ethereum_data, indent=2, ensure_ascii=False, default=str)
    sol_str = json.dumps(solana_data, indent=2, ensure_ascii=False, default=str)
    
    prompt = f"""
다음은 Ethereum과 Solana 네트워크의 온체인 데이터입니다.
두 네트워크를 비교하여 기관 투자자 관점에서 3줄 요약을 작성해주세요.

## Ethereum 데이터
{eth_str}

## Solana 데이터
{sol_str}

## 요구사항
1. 처리량(트랜잭션 수) 비교
2. 수수료 효율성 비교
3. 네트워크 활성도 비교
4. 각 네트워크의 강점을 데이터로 뒷받침하여 설명
5. 총 3줄로 간결하게 작성
"""
    
    response = model.generate_content(prompt)
    return response.text


def detect_anomalies(query_results: Dict[str, Any]) -> str:
    """
    이상 징후 탐지 및 코멘트 생성
    
    Args:
        query_results: BigQuery 쿼리 결과
    
    Returns:
        이상 징후 분석 텍스트
    """
    
    model = genai.GenerativeModel('gemini-2.0-flash')
    
    data_str = json.dumps(query_results, indent=2, ensure_ascii=False, default=str)
    
    prompt = f"""
다음 온체인 데이터에서 이상 징후나 주목할 만한 패턴을 찾아주세요.

## 데이터
{data_str}

## 분석 요청
1. 평소와 다른 급증/급감 지점 식별
2. 가능한 원인 추론 (이벤트, 시장 상황 등)
3. 추가 조사가 필요한 항목 제안

이상 징후가 없다면 "특별한 이상 징후 없음"이라고 답변하세요.
"""
    
    response = model.generate_content(prompt)
    return response.text


# 사용 예시
if __name__ == "__main__":
    # 예시 데이터
    sample_data = {
        "tx_volume": {
            "date": "2025-03-15",
            "ethereum_tx_count": 1200000,
            "solana_tx_count": 25000000
        },
        "avg_fee": {
            "ethereum_avg_fee_eth": 0.002,
            "solana_avg_fee_sol": 0.000005
        }
    }
    
    # 주간 요약 생성
    summary = generate_weekly_summary(sample_data)
    print("=== 주간 요약 ===")
    print(summary)
    print("\n")
    
    # 비교 인사이트 생성
    eth_data = {"tx_count": 1200000, "avg_fee": 0.002}
    sol_data = {"tx_count": 25000000, "avg_fee": 0.000005}
    comparison = generate_comparison_insight(eth_data, sol_data)
    print("=== 비교 인사이트 ===")
    print(comparison)
