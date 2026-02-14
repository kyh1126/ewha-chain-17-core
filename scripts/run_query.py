#!/usr/bin/env python3
"""
BigQuery 쿼리 실행 자동화 스크립트

사용법:
    python scripts/run_query.py <sql_file> [옵션]

예시:
    python scripts/run_query.py templates/sql/01_basic_exploration.sql
    python scripts/run_query.py templates/queries/01_tx_volume.sql --output results.csv
    python scripts/run_query.py my_query.sql --dry-run --verbose
"""

import os
import sys
import argparse
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

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


class BigQueryRunner:
    """BigQuery 쿼리 실행 클래스"""
    
    def __init__(self, project_id: Optional[str] = None, dry_run: bool = False):
        """
        초기화
        
        Args:
            project_id: GCP 프로젝트 ID (None이면 환경 변수에서 가져옴)
            dry_run: True면 실제 실행 없이 비용만 확인
        """
        self.project_id = project_id or os.getenv("GCP_PROJECT_ID")
        if not self.project_id:
            raise ValueError(
                "GCP_PROJECT_ID 환경 변수를 설정하거나 --project-id 옵션을 사용하세요.\n"
                "예: export GCP_PROJECT_ID='your-project-id'"
            )
        
        self.client = bigquery.Client(project=self.project_id)
        self.dry_run = dry_run
    
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
        
        Args:
            sql: 전체 SQL 텍스트
        
        Returns:
            유효한 SQL 문장 리스트
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
                    # 이스케이프된 작은따옴표 ('')
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
            
            # 한 줄 주석 시작
            if not in_multi_comment and char == '-' and i + 1 < len(sql) and sql[i + 1] == '-':
                in_single_comment = True
                current.append(char)
                i += 1
                current.append(sql[i])
            # 한 줄 주석 끝
            elif in_single_comment and char == '\n':
                in_single_comment = False
                current.append(char)
            # 블록 주석 시작
            elif not in_single_comment and char == '/' and i + 1 < len(sql) and sql[i + 1] == '*':
                in_multi_comment = True
                current.append(char)
                i += 1
                current.append(sql[i])
            # 블록 주석 끝
            elif in_multi_comment and char == '*' and i + 1 < len(sql) and sql[i + 1] == '/':
                in_multi_comment = False
                current.append(char)
                i += 1
                current.append(sql[i])
            # 문자열 리터럴 시작 (주석 밖에서만)
            elif not in_single_comment and not in_multi_comment and char == "'":
                in_single_quote = True
                current.append(char)
            elif not in_single_comment and not in_multi_comment and char == '"':
                in_double_quote = True
                current.append(char)
            # 세미콜론 (주석/문자열 밖)
            elif not in_single_comment and not in_multi_comment and char == ';':
                stmt = ''.join(current).strip()
                if stmt:
                    statements.append(stmt)
                current = []
            else:
                current.append(char)
            
            i += 1
        
        # 마지막 문장 (세미콜론 없이 끝나는 경우)
        remaining = ''.join(current).strip()
        if remaining:
            statements.append(remaining)
        
        return statements
    
    def execute_query(
        self,
        sql: str,
        output_file: Optional[str] = None,
        output_format: str = 'csv'
    ) -> Dict[str, Any]:
        """
        쿼리 실행
        
        Args:
            sql: 실행할 SQL 쿼리
            output_file: 결과를 저장할 파일 경로 (None이면 출력하지 않음)
            output_format: 출력 형식 ('csv', 'json', 'table')
        
        Returns:
            실행 결과 딕셔너리
        """
        job_config = bigquery.QueryJobConfig()
        
        if self.dry_run:
            # Dry run: 실제 실행 없이 비용만 확인
            job_config.dry_run = True
            job_config.use_query_cache = False
        
        start_time = datetime.now()
        
        try:
            query_job = self.client.query(sql, job_config=job_config)
            
            if self.dry_run:
                # Dry run 결과
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                
                return {
                    'dry_run': True,
                    'total_bytes_processed': query_job.total_bytes_processed,
                    'estimated_cost_usd': self._calculate_cost(query_job.total_bytes_processed),
                    'duration_seconds': duration,
                    'sql': sql
                }
            
            # 실제 쿼리 실행
            print(f"쿼리 실행 중... (프로젝트: {self.project_id})")
            results = query_job.result()
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # 결과 처리
            rows = list(results)
            total_rows = len(rows)
            
            # 결과 출력
            print(f"\n✓ 쿼리 실행 완료!")
            print(f"  - 처리된 데이터: {self._format_bytes(query_job.total_bytes_processed)}")
            print(f"  - 예상 비용: ${self._calculate_cost(query_job.total_bytes_processed):.6f}")
            print(f"  - 실행 시간: {duration:.2f}초")
            print(f"  - 결과 행 수: {total_rows:,}개")
            
            # 파일로 저장
            if output_file:
                self._save_results(rows, results.schema, output_file, output_format)
                print(f"  - 결과 저장: {output_file}")
            
            return {
                'success': True,
                'total_bytes_processed': query_job.total_bytes_processed,
                'estimated_cost_usd': self._calculate_cost(query_job.total_bytes_processed),
                'duration_seconds': duration,
                'total_rows': total_rows,
                'output_file': output_file
            }
            
        except GoogleCloudError as e:
            print(f"\n✗ 쿼리 실행 실패:")
            print(f"  {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _calculate_cost(self, bytes_processed: int) -> float:
        """
        BigQuery 쿼리 비용 계산
        
        참고: Public Datasets는 무료이지만 쿼리 처리 비용은 발생할 수 있습니다.
        일반적인 가격: $5 per TB (처리된 데이터 기준)
        """
        # 1TB = 1,024^4 bytes
        tb_processed = bytes_processed / (1024 ** 4)
        cost_per_tb = 5.0  # USD
        return tb_processed * cost_per_tb
    
    def _format_bytes(self, bytes_count: int) -> str:
        """바이트를 읽기 쉬운 형식으로 변환"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_count < 1024.0:
                return f"{bytes_count:.2f} {unit}"
            bytes_count /= 1024.0
        return f"{bytes_count:.2f} PB"
    
    def _save_results(
        self,
        rows: list,
        schema: Any,
        output_file: str,
        output_format: str
    ):
        """쿼리 결과를 파일로 저장"""
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if output_format == 'csv':
            import csv
            
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                if rows:
                    writer = csv.DictWriter(f, fieldnames=[field.name for field in schema])
                    writer.writeheader()
                    for row in rows:
                        writer.writerow(dict(row))
        
        elif output_format == 'json':
            results = []
            for row in rows:
                results.append(dict(row))
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False, default=str)
        
        else:
            raise ValueError(f"지원하지 않는 출력 형식: {output_format}")


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(
        description='BigQuery 쿼리 실행 자동화 스크립트',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  # 기본 실행
  python scripts/run_query.py templates/sql/01_basic_exploration.sql
  
  # 결과를 CSV로 저장
  python scripts/run_query.py my_query.sql --output results.csv
  
  # Dry run (비용만 확인)
  python scripts/run_query.py my_query.sql --dry-run
  
  # 상세 출력
  python scripts/run_query.py my_query.sql --verbose
        """
    )
    
    parser.add_argument(
        'sql_file',
        help='실행할 SQL 파일 경로'
    )
    
    parser.add_argument(
        '--output', '-o',
        help='결과를 저장할 파일 경로 (CSV 또는 JSON)'
    )
    
    parser.add_argument(
        '--format', '-f',
        choices=['csv', 'json'],
        default='csv',
        help='출력 형식 (기본값: csv)'
    )
    
    parser.add_argument(
        '--project-id', '-p',
        help='GCP 프로젝트 ID (기본값: GCP_PROJECT_ID 환경 변수)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='실제 실행 없이 비용만 확인'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='상세 출력'
    )
    
    args = parser.parse_args()
    
    # SQL 파일 읽기
    try:
        runner = BigQueryRunner(project_id=args.project_id, dry_run=args.dry_run)
        sql = runner.read_sql_file(args.sql_file)
        
        if args.verbose:
            print(f"SQL 파일: {args.sql_file}")
            print(f"프로젝트 ID: {runner.project_id}")
            print(f"Dry run: {args.dry_run}")
            if args.output:
                print(f"출력 파일: {args.output}")
            print("\n" + "="*60)
            print("SQL 쿼리:")
            print("="*60)
            print(sql)
            print("="*60 + "\n")
        
        # 쿼리 실행
        result = runner.execute_query(sql, args.output, args.format)
        
        # Dry run 결과 출력
        if args.dry_run:
            print(f"\n[Dry Run 결과]")
            print(f"  처리될 데이터: {runner._format_bytes(result['total_bytes_processed'])}")
            print(f"  예상 비용: ${result['estimated_cost_usd']:.6f}")
            print(f"  실행 시간: {result['duration_seconds']:.2f}초")
            print(f"\n실제 실행하려면 --dry-run 옵션을 제거하세요.")
        
        # 성공/실패에 따른 종료 코드
        sys.exit(0 if result.get('success', True) else 1)
        
    except Exception as e:
        print(f"\n✗ 오류 발생: {str(e)}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
