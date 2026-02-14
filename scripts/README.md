# 스크립트 가이드

이 폴더에는 BigQuery 쿼리 실행을 자동화하는 스크립트가 포함되어 있습니다.

## run_query.py

BigQuery 쿼리를 자동으로 실행하고 결과를 저장하는 Python 스크립트입니다.

### 설치

```bash
# 필요한 패키지 설치
pip install google-cloud-bigquery

# 또는 requirements.txt 사용
pip install -r requirements.txt
```

### 환경 변수 설정

```bash
# GCP 프로젝트 ID 설정
export GCP_PROJECT_ID="ewha-chain-17"

# 또는 서비스 계정 키 파일 사용
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your-key.json"
```

### 사용법

#### 기본 실행

```bash
# SQL 파일 실행
python scripts/run_query.py templates/sql/01_basic_exploration.sql
```

#### 결과를 파일로 저장

```bash
# CSV로 저장
python scripts/run_query.py templates/queries/01_tx_volume.sql --output results/tx_volume.csv

# JSON으로 저장
python scripts/run_query.py my_query.sql --output results/data.json --format json
```

#### Dry Run (비용만 확인)

```bash
# 실제 실행 없이 비용만 확인
python scripts/run_query.py templates/queries/01_tx_volume.sql --dry-run
```

#### 상세 출력

```bash
# SQL 쿼리와 상세 정보 출력
python scripts/run_query.py my_query.sql --verbose
```

### 옵션

| 옵션 | 설명 | 예시 |
|------|------|------|
| `--output`, `-o` | 결과 저장 파일 경로 | `--output results.csv` |
| `--format`, `-f` | 출력 형식 (csv/json) | `--format json` |
| `--project-id`, `-p` | GCP 프로젝트 ID | `--project-id my-project` |
| `--dry-run` | 실제 실행 없이 비용만 확인 | `--dry-run` |
| `--verbose`, `-v` | 상세 출력 | `--verbose` |

### 예시

```bash
# 1. 쿼리 비용 확인 (Dry Run)
python scripts/run_query.py templates/queries/01_tx_volume.sql --dry-run

# 2. 쿼리 실행 및 결과 저장
python scripts/run_query.py templates/queries/01_tx_volume.sql \
  --output results/tx_volume.csv \
  --verbose

# 3. 여러 쿼리 일괄 실행 (스크립트 작성)
for sql_file in templates/queries/*.sql; do
  python scripts/run_query.py "$sql_file" \
    --output "results/$(basename $sql_file .sql).csv"
done
```

## run_query.sh

Python 스크립트를 실행하는 Shell 래퍼입니다.

### 사용법

```bash
# 실행 권한 부여
chmod +x scripts/run_query.sh

# 실행
./scripts/run_query.sh templates/sql/01_basic_exploration.sql
```

## 비용 관리

### Public Datasets는 무료

- `bigquery-public-data` 프로젝트의 데이터셋은 무료로 조회 가능
- 쿼리 처리 비용만 발생 (처리한 데이터 양 기준)

### 비용 절감 팁

1. **Dry Run으로 비용 확인**
   ```bash
   python scripts/run_query.py my_query.sql --dry-run
   ```

2. **작은 범위로 테스트**
   - 날짜 범위를 줄여서 테스트
   - LIMIT 절 사용

3. **결과 캐싱**
   - BigQuery는 동일 쿼리 결과를 캐시
   - 결과를 파일로 저장하여 재사용

## 문제 해결

### "GCP_PROJECT_ID 환경 변수를 설정하세요"

```bash
export GCP_PROJECT_ID="your-project-id"
```

### "google-cloud-bigquery 패키지가 설치되지 않았습니다"

```bash
pip install google-cloud-bigquery
```

### "권한이 없습니다"

- GCP 콘솔에서 BigQuery API 활성화 확인
- 서비스 계정 권한 확인
- 프로젝트 ID 확인

### 쿼리가 너무 느림

- 날짜 범위 축소
- 샘플링 사용 (`TABLESAMPLE`)
- 필요한 컬럼만 SELECT

## 고급 활용

### Python 코드에서 직접 사용

```python
# 프로젝트 루트에서 실행 시
import sys
sys.path.insert(0, "scripts")
from run_query import BigQueryRunner

runner = BigQueryRunner(project_id="ewha-chain-17")
sql = """
SELECT * FROM `bigquery-public-data.crypto_ethereum.blocks`
LIMIT 10
"""

result = runner.execute_query(sql, output_file="results.csv")
print(f"처리된 데이터: {runner._format_bytes(result['total_bytes_processed'])}")
```

### 스케줄링 (선택)

```bash
# cron으로 주기적 실행
# 매일 오전 9시에 실행
0 9 * * * cd /path/to/project && python scripts/run_query.py queries/daily_summary.sql --output results/daily_$(date +\%Y\%m\%d).csv
```

## summarize_with_gemini.py

BigQuery 쿼리 결과를 Gemini API로 자동 요약하는 스크립트입니다.

### 설치

```bash
# 필요한 패키지 설치
pip install google-cloud-bigquery google-generativeai
```

### 환경 변수 설정

```bash
# GCP 프로젝트 ID 설정
export GCP_PROJECT_ID="ewha-chain-17"

# Gemini API 키 설정
export GEMINI_API_KEY="your-gemini-api-key"
```

### 사용법

#### 기본 주간 요약

```bash
# SQL 쿼리 실행 후 Gemini로 요약 생성
python scripts/summarize_with_gemini.py templates/queries/01_tx_volume.sql
```

#### 비교 분석 (두 쿼리 결과 비교)

```bash
# Ethereum vs Solana 비교 (체인별 쿼리를 별도 파일로 분리한 경우)
# 예: members/[본인이름]/queries/ 에 체인별 쿼리 파일을 만들어 사용
python scripts/summarize_with_gemini.py \
  members/홍길동/queries/eth_tx_volume.sql \
  members/홍길동/queries/sol_tx_volume.sql \
  --type comparison \
  --label1 Ethereum \
  --label2 Solana
```

#### 이상 징후 탐지

```bash
# 데이터에서 이상 징후 탐지
python scripts/summarize_with_gemini.py my_query.sql --type anomalies
```

#### 커스텀 프롬프트

```bash
# 사용자 정의 프롬프트로 요약
python scripts/summarize_with_gemini.py my_query.sql \
  --type custom \
  --custom-prompt "이 데이터의 주요 특징을 3줄로 요약해주세요"
```

#### 결과를 파일로 저장

```bash
python scripts/summarize_with_gemini.py my_query.sql \
  --output summaries/weekly_summary.txt
```

### 옵션

| 옵션 | 설명 | 예시 |
|------|------|------|
| `--type`, `-t` | 요약 타입 (weekly/comparison/anomalies/custom) | `--type comparison` |
| `--output`, `-o` | 요약 결과 저장 파일 경로 | `--output summary.txt` |
| `--project-id`, `-p` | GCP 프로젝트 ID | `--project-id my-project` |
| `--api-key` | Gemini API 키 | `--api-key your-key` |
| `--custom-prompt` | 커스텀 프롬프트 (custom 타입용) | `--custom-prompt "..."` |
| `--label1` | 첫 번째 데이터셋 라벨 | `--label1 Ethereum` |
| `--label2` | 두 번째 데이터셋 라벨 | `--label2 Solana` |
| `--verbose`, `-v` | 상세 출력 | `--verbose` |

### 요약 타입 설명

1. **weekly** (기본값): 주간 요약 리포트 생성
   - 핵심 지표 요약
   - 전주 대비 변화율
   - 이상 징후 탐지

2. **comparison**: 두 쿼리 결과 비교 분석
   - 처리량 비교
   - 수수료 효율성 비교
   - 네트워크 활성도 비교

3. **anomalies**: 이상 징후 탐지
   - 급증/급감 지점 식별
   - 가능한 원인 추론
   - 추가 조사 항목 제안

4. **custom**: 사용자 정의 프롬프트
   - 자유로운 요약 형식

### 예시

```bash
# 1. 주간 요약 생성
python scripts/summarize_with_gemini.py templates/queries/01_tx_volume.sql \
  --output summaries/weekly_2025-03-15.txt

# 2. Ethereum vs Solana 비교
python scripts/summarize_with_gemini.py \
  queries/eth_metrics.sql \
  queries/sol_metrics.sql \
  --type comparison \
  --output summaries/comparison.txt

# 3. 이상 징후 탐지
python scripts/summarize_with_gemini.py queries/daily_tx.sql \
  --type anomalies \
  --output summaries/anomalies.txt

# 4. 여러 쿼리 일괄 요약
for sql_file in templates/queries/*.sql; do
  python scripts/summarize_with_gemini.py "$sql_file" \
    --output "summaries/$(basename $sql_file .sql).txt"
done
```

### 출력 예시

```
📊 쿼리 실행 중: templates/queries/01_tx_volume.sql
  - 결과 행 수: 30개
  - 컬럼: date, tx_count, unique_senders

🤖 Gemini로 요약 생성 중...

============================================================
생성된 요약:
============================================================
[주간 요약]
이번 주 Ethereum 네트워크는 평균 일일 120만 건의 트랜잭션을 처리했으며,
전주 대비 5% 증가했습니다. 특히 수요일과 목요일에 활동이 집중되었습니다.

[주요 변화]
- 일일 트랜잭션 수: 전주 대비 +5%
- 고유 송신자 수: 전주 대비 +3%
- 평균 가스비: 전주 대비 -2% (네트워크 혼잡도 감소)

[이상 징후]
특별한 이상 징후 없음
============================================================

✓ 요약이 저장되었습니다: summaries/weekly_2025-03-15.txt
```

## summarize_with_gemini.sh

Python 스크립트를 실행하는 Shell 래퍼입니다.

### 사용법

```bash
# 실행 권한 부여
chmod +x scripts/summarize_with_gemini.sh

# 실행
./scripts/summarize_with_gemini.sh templates/queries/01_tx_volume.sql
```

## 문제 해결

### "GEMINI_API_KEY 환경 변수를 설정하세요"

```bash
export GEMINI_API_KEY="your-api-key"
```

### "google-generativeai 패키지가 설치되지 않았습니다"

```bash
pip install google-generativeai
```

### "Rate limit exceeded"

- 요청 간격을 늘리기
- 배치 처리로 변경
- 무료 할당량 확인 (분당 60 요청)

### 응답이 느림

- 프롬프트 길이 줄이기
- 필요한 정보만 포함
- 쿼리 결과를 먼저 필터링

## 다음 단계

- [쿼리 실행 가이드](../docs/guides/query_execution.md)
- [BigQuery 설정 가이드](../docs/onboarding/01_bigquery_setup.md)
- [Gemini API 설정 가이드](../docs/onboarding/03_gemini_api.md)
