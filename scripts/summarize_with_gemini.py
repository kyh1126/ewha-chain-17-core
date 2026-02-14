#!/usr/bin/env python3
"""
BigQuery 쿼리 결과를 Gemini API로 자동 요약하는 스크립트

사용법:
    python scripts/summarize_with_gemini.py <sql_file> [옵션]

예시:
    python scripts/summarize_with_gemini.py templates/queries/01_tx_volume.sql
    python scripts/summarize_with_gemini.py my_query.sql --type weekly --output summary.txt
    python scripts/summarize_with_gemini.py eth_data.sql sol_data.sql --type comparison
"""

import os
import sys
import argparse
import json
from decimal import Decimal
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv가 없으면 환경 변수에서 직접 가져옴

try:
    from google.cloud import bigquery
    from google.cloud.exceptions import GoogleCloudError
except ImportError:
    print("오류: google-cloud-bigquery 패키지가 설치되지 않았습니다.")
    print("설치 방법: pip install google-cloud-bigquery")
    sys.exit(1)

try:
    import google.generativeai as genai
except ImportError:
    print("오류: google-generativeai 패키지가 설치되지 않았습니다.")
    print("설치 방법: pip install google-generativeai")
    sys.exit(1)


class GeminiSummarizer:
    """Gemini API를 사용한 요약 생성 클래스"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        초기화
        
        Args:
            api_key: Gemini API 키 (None이면 환경 변수에서 가져옴)
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY 환경 변수를 설정하거나 --api-key 옵션을 사용하세요.\n"
                "예: export GEMINI_API_KEY='your-api-key'"
            )
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
    
    def generate_weekly_summary(self, query_results: Dict[str, Any]) -> str:
        """
        주간 온체인 데이터 요약 생성
        
        Args:
            query_results: BigQuery 쿼리 결과 딕셔너리
        
        Returns:
            생성된 요약 텍스트
        """
        prompt = f"""
당신은 블록체인 데이터 분석가입니다. 다음 온체인 데이터를 기반으로 
기관 투자자/증권사 관점에서 읽을 수 있는 주간 요약 리포트를 작성해주세요.

## 데이터 요약
{json.dumps(query_results, indent=2, ensure_ascii=False, default=str)}

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
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            raise RuntimeError(f"Gemini API 호출 실패: {str(e)}")
    
    def generate_comparison_insight(
        self,
        data1: Dict[str, Any],
        data2: Dict[str, Any],
        label1: str = "Ethereum",
        label2: str = "Solana"
    ) -> str:
        """
        두 데이터셋 비교 인사이트 생성
        
        Args:
            data1: 첫 번째 데이터셋
            data2: 두 번째 데이터셋
            label1: 첫 번째 데이터셋 라벨
            label2: 두 번째 데이터셋 라벨
        
        Returns:
            비교 분석 텍스트
        """
        prompt = f"""
다음은 {label1}과 {label2} 네트워크의 온체인 데이터입니다.
두 네트워크를 비교하여 기관 투자자 관점에서 3줄 요약을 작성해주세요.

## {label1} 데이터
{json.dumps(data1, indent=2, ensure_ascii=False, default=str)}

## {label2} 데이터
{json.dumps(data2, indent=2, ensure_ascii=False, default=str)}

## 요구사항
1. 처리량(트랜잭션 수) 비교
2. 수수료 효율성 비교
3. 네트워크 활성도 비교
4. 각 네트워크의 강점을 데이터로 뒷받침하여 설명
5. 총 3줄로 간결하게 작성
"""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            raise RuntimeError(f"Gemini API 호출 실패: {str(e)}")
    
    def detect_anomalies(self, query_results: Dict[str, Any]) -> str:
        """
        이상 징후 탐지 및 코멘트 생성
        
        Args:
            query_results: BigQuery 쿼리 결과
        
        Returns:
            이상 징후 분석 텍스트
        """
        prompt = f"""
다음 온체인 데이터에서 이상 징후나 주목할 만한 패턴을 찾아주세요.

## 데이터
{json.dumps(query_results, indent=2, ensure_ascii=False, default=str)}

## 분석 요청
1. 평소와 다른 급증/급감 지점 식별
2. 가능한 원인 추론 (이벤트, 시장 상황 등)
3. 추가 조사가 필요한 항목 제안

이상 징후가 없다면 "특별한 이상 징후 없음"이라고 답변하세요.
"""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            raise RuntimeError(f"Gemini API 호출 실패: {str(e)}")
    
    def generate_custom_summary(
        self,
        query_results: Dict[str, Any],
        custom_prompt: str
    ) -> str:
        """
        커스텀 프롬프트로 요약 생성
        
        Args:
            query_results: BigQuery 쿼리 결과
            custom_prompt: 사용자 정의 프롬프트
        
        Returns:
            생성된 요약 텍스트
        """
        full_prompt = f"""
{custom_prompt}

## 데이터
{json.dumps(query_results, indent=2, ensure_ascii=False, default=str)}
"""
        
        try:
            response = self.model.generate_content(full_prompt)
            return response.text
        except Exception as e:
            raise RuntimeError(f"Gemini API 호출 실패: {str(e)}")


class BigQueryExecutor:
    """BigQuery 쿼리 실행 클래스"""
    
    def __init__(self, project_id: Optional[str] = None):
        """
        초기화
        
        Args:
            project_id: GCP 프로젝트 ID
        """
        self.project_id = project_id or os.getenv("GCP_PROJECT_ID")
        if not self.project_id:
            raise ValueError(
                "GCP_PROJECT_ID 환경 변수를 설정하거나 --project-id 옵션을 사용하세요."
            )
        
        self.client = bigquery.Client(project=self.project_id)
    
    def read_sql_file(self, file_path: str) -> str:
        """SQL 파일 읽기 (멀티쿼리 파일의 경우 첫 번째 쿼리만 반환)"""
        sql_path = Path(file_path)
        
        if not sql_path.exists():
            raise FileNotFoundError(f"SQL 파일을 찾을 수 없습니다: {file_path}")
        
        with open(sql_path, 'r', encoding='utf-8') as f:
            sql = f.read()
        
        if not sql.strip():
            raise ValueError(f"SQL 파일이 비어있습니다: {file_path}")
        
        # 주석과 공백을 제외한 유효한 SQL 문장 분리
        statements = self._split_sql_statements(sql)
        
        if len(statements) > 1:
            print(f"\n⚠️  SQL 파일에 {len(statements)}개의 쿼리가 포함되어 있습니다.")
            print(f"   첫 번째 쿼리만 실행합니다. 다른 쿼리를 실행하려면 해당 부분만 별도 파일로 저장하세요.")
        
        return statements[0] if statements else sql.strip()
    
    @staticmethod
    def _split_sql_statements(sql: str) -> list:
        """
        SQL 텍스트를 개별 문장으로 분리
        (주석 및 문자열 리터럴 내 세미콜론은 무시)
        """
        statements = []
        current = []
        in_single_comment = False
        in_multi_comment = False
        in_single_quote = False
        in_double_quote = False
        i = 0
        
        while i < len(sql):
            char = sql[i]
            
            # 문자열 리터럴 내부에서는 세미콜론/주석을 무시
            if in_single_quote:
                current.append(char)
                if char == "'" and i + 1 < len(sql) and sql[i + 1] == "'":
                    i += 1
                    current.append(sql[i])
                elif char == "'":
                    in_single_quote = False
                i += 1
                continue
            
            if in_double_quote:
                current.append(char)
                if char == '"':
                    in_double_quote = False
                i += 1
                continue
            
            if not in_multi_comment and char == '-' and i + 1 < len(sql) and sql[i + 1] == '-':
                in_single_comment = True
                current.append(char)
                i += 1
                current.append(sql[i])
            elif in_single_comment and char == '\n':
                in_single_comment = False
                current.append(char)
            elif not in_single_comment and char == '/' and i + 1 < len(sql) and sql[i + 1] == '*':
                in_multi_comment = True
                current.append(char)
                i += 1
                current.append(sql[i])
            elif in_multi_comment and char == '*' and i + 1 < len(sql) and sql[i + 1] == '/':
                in_multi_comment = False
                current.append(char)
                i += 1
                current.append(sql[i])
            elif not in_single_comment and not in_multi_comment and char == "'":
                in_single_quote = True
                current.append(char)
            elif not in_single_comment and not in_multi_comment and char == '"':
                in_double_quote = True
                current.append(char)
            elif not in_single_comment and not in_multi_comment and char == ';':
                stmt = ''.join(current).strip()
                if stmt:
                    statements.append(stmt)
                current = []
            else:
                current.append(char)
            
            i += 1
        
        remaining = ''.join(current).strip()
        if remaining:
            statements.append(remaining)
        
        return statements
    
    def execute_query(self, sql: str) -> List[Dict[str, Any]]:
        """
        쿼리 실행 및 결과 반환
        
        Args:
            sql: 실행할 SQL 쿼리
        
        Returns:
            쿼리 결과 리스트
        """
        try:
            query_job = self.client.query(sql)
            results = query_job.result()
            
            # 결과를 딕셔너리 리스트로 변환
            rows = []
            for row in results:
                rows.append(dict(row))
            
            return rows
        except GoogleCloudError as e:
            raise RuntimeError(f"BigQuery 쿼리 실행 실패: {str(e)}")
    
    def execute_query_to_dict(self, sql: str) -> Dict[str, Any]:
        """
        쿼리 실행 및 통계 정보 포함 딕셔너리로 반환
        
        Args:
            sql: 실행할 SQL 쿼리
        
        Returns:
            결과와 통계 정보를 포함한 딕셔너리
        """
        try:
            query_job = self.client.query(sql)
            results = query_job.result()
            
            rows = []
            for row in results:
                rows.append(dict(row))
            
            return {
                'data': rows,
                'total_rows': len(rows),
                'total_bytes_processed': query_job.total_bytes_processed,
                'execution_time': (query_job.ended - query_job.started) if (query_job.ended and query_job.started) else None
            }
        except GoogleCloudError as e:
            raise RuntimeError(f"BigQuery 쿼리 실행 실패: {str(e)}")


def format_query_results(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    쿼리 결과를 요약 가능한 형식으로 변환
    
    Args:
        results: 쿼리 결과 리스트
    
    Returns:
        요약용 딕셔너리
    """
    if not results:
        return {"message": "결과가 없습니다."}
    
    # 첫 번째 행의 키를 사용하여 구조 파악
    sample_row = results[0]
    
    # 숫자형 컬럼 찾기 (BigQuery NUMERIC/BIGNUMERIC은 decimal.Decimal으로 반환됨)
    numeric_cols = []
    for key, value in sample_row.items():
        if isinstance(value, (int, float, Decimal)) and value is not None:
            numeric_cols.append(key)
    
    # 통계 계산
    summary = {
        'total_rows': len(results),
        'columns': list(sample_row.keys()),
        'sample_data': results[:5] if len(results) > 5 else results
    }
    
    # 숫자형 컬럼의 통계
    if numeric_cols:
        summary['statistics'] = {}
        for col in numeric_cols:
            values = [float(row[col]) for row in results
                      if row[col] is not None and isinstance(row[col], (int, float, Decimal))]
            if values:
                summary['statistics'][col] = {
                    'sum': sum(values),
                    'avg': sum(values) / len(values),
                    'min': min(values),
                    'max': max(values),
                    'count': len(values)
                }
    
    return summary


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(
        description='BigQuery 쿼리 결과를 Gemini API로 자동 요약',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  # 기본 주간 요약
  python scripts/summarize_with_gemini.py templates/queries/01_tx_volume.sql
  
  # 비교 분석 (두 쿼리 결과 비교)
  python scripts/summarize_with_gemini.py eth_query.sql sol_query.sql --type comparison
  
  # 이상 징후 탐지
  python scripts/summarize_with_gemini.py my_query.sql --type anomalies
  
  # 커스텀 프롬프트
  python scripts/summarize_with_gemini.py my_query.sql --custom-prompt "이 데이터의 주요 특징을 3줄로 요약해주세요"
        """
    )
    
    parser.add_argument(
        'sql_files',
        nargs='+',
        help='실행할 SQL 파일 경로 (1개 또는 2개)'
    )
    
    parser.add_argument(
        '--type', '-t',
        choices=['weekly', 'comparison', 'anomalies', 'custom'],
        default='weekly',
        help='요약 타입 (기본값: weekly)'
    )
    
    parser.add_argument(
        '--output', '-o',
        help='요약 결과를 저장할 파일 경로'
    )
    
    parser.add_argument(
        '--project-id', '-p',
        help='GCP 프로젝트 ID (기본값: GCP_PROJECT_ID 환경 변수)'
    )
    
    parser.add_argument(
        '--api-key',
        help='Gemini API 키 (기본값: GEMINI_API_KEY 환경 변수)'
    )
    
    parser.add_argument(
        '--custom-prompt',
        help='커스텀 프롬프트 (--type custom일 때 사용)'
    )
    
    parser.add_argument(
        '--label1',
        default='Ethereum',
        help='첫 번째 데이터셋 라벨 (comparison 타입용)'
    )
    
    parser.add_argument(
        '--label2',
        default='Solana',
        help='두 번째 데이터셋 라벨 (comparison 타입용)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='상세 출력'
    )
    
    args = parser.parse_args()
    
    # 입력 검증
    if args.type == 'comparison' and len(args.sql_files) != 2:
        print("오류: comparison 타입은 2개의 SQL 파일이 필요합니다.", file=sys.stderr)
        sys.exit(1)
    
    if args.type == 'custom' and not args.custom_prompt:
        print("오류: custom 타입은 --custom-prompt 옵션이 필요합니다.", file=sys.stderr)
        sys.exit(1)
    
    try:
        # BigQuery 실행기 초기화
        bq_executor = BigQueryExecutor(project_id=args.project_id)
        
        # Gemini 요약기 초기화
        summarizer = GeminiSummarizer(api_key=args.api_key)
        
        # 첫 번째 쿼리 실행
        print(f"📊 쿼리 실행 중: {args.sql_files[0]}")
        sql1 = bq_executor.read_sql_file(args.sql_files[0])
        results1 = bq_executor.execute_query(sql1)
        formatted_results1 = format_query_results(results1)
        
        if args.verbose:
            print(f"  - 결과 행 수: {len(results1)}개")
            print(f"  - 컬럼: {', '.join(formatted_results1.get('columns', []))}")
        
        # 두 번째 쿼리 실행 (comparison 타입인 경우)
        formatted_results2 = None
        if args.type == 'comparison':
            print(f"\n📊 쿼리 실행 중: {args.sql_files[1]}")
            sql2 = bq_executor.read_sql_file(args.sql_files[1])
            results2 = bq_executor.execute_query(sql2)
            formatted_results2 = format_query_results(results2)
            
            if args.verbose:
                print(f"  - 결과 행 수: {len(results2)}개")
                print(f"  - 컬럼: {', '.join(formatted_results2.get('columns', []))}")
        
        # 요약 생성
        print(f"\n🤖 Gemini로 요약 생성 중...")
        
        if args.type == 'weekly':
            summary = summarizer.generate_weekly_summary(formatted_results1)
        elif args.type == 'comparison':
            summary = summarizer.generate_comparison_insight(
                formatted_results1,
                formatted_results2,
                args.label1,
                args.label2
            )
        elif args.type == 'anomalies':
            summary = summarizer.detect_anomalies(formatted_results1)
        else:  # custom
            summary = summarizer.generate_custom_summary(
                formatted_results1,
                args.custom_prompt
            )
        
        # 결과 출력
        print("\n" + "="*60)
        print("생성된 요약:")
        print("="*60)
        print(summary)
        print("="*60)
        
        # 파일로 저장
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(f"# 요약 리포트\n\n")
                f.write(f"생성 일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write(f"쿼리 파일: {', '.join(args.sql_files)}\n")
                f.write(f"요약 타입: {args.type}\n\n")
                f.write("---\n\n")
                f.write(summary)
            
            print(f"\n✓ 요약이 저장되었습니다: {args.output}")
        
        sys.exit(0)
        
    except Exception as e:
        print(f"\n✗ 오류 발생: {str(e)}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
