# BigQuery 설정 가이드

## 1. GCP 계정 생성 및 프로젝트 설정

### GCP 계정 생성

1. [Google Cloud Console](https://console.cloud.google.com/) 접속
2. Google 계정으로 로그인
3. 무료 체험 계정 활성화 (크레딧 $300 제공)

### 프로젝트 생성

1. 상단 프로젝트 선택 드롭다운 클릭
2. "새 프로젝트" 클릭
3. 프로젝트 이름 입력: `ewha-chain-17` (또는 본인 이름 포함)
4. "만들기" 클릭

### BigQuery API 활성화

1. 왼쪽 메뉴에서 "API 및 서비스" → "라이브러리" 선택
2. "BigQuery API" 검색
3. "사용 설정" 클릭

## 2. BigQuery 콘솔 접근

1. 왼쪽 메뉴에서 "BigQuery" 선택
2. BigQuery 콘솔이 열림

## 3. Public Datasets 접근

### Ethereum 데이터셋

1. 왼쪽 탐색기에서 `bigquery-public-data` 프로젝트 확장
2. `crypto_ethereum` 데이터셋 확장
3. 사용 가능한 테이블 확인:
   - `transactions`: 모든 트랜잭션
   - `blocks`: 블록 정보
   - `contracts`: 컨트랙트 정보
   - `token_transfers`: 토큰 전송

### Solana 데이터셋

> ⚠️ **참고**: Solana Public Dataset(`crypto_solana_mainnet_us`)는 **2025-03-31 이후 업데이트가 중단**되었습니다. 과거 데이터는 정상 조회 가능하며, 학습·비교 목적으로 충분합니다. 쿼리 시 `CURRENT_TIMESTAMP()` 대신 고정 날짜 범위(예: 2025-03-01 ~ 2025-03-31)를 사용하세요.

1. `crypto_solana_mainnet_us` 데이터셋 확장
2. 사용 가능한 테이블 확인:
   - `Transactions`: 모든 트랜잭션 (대문자 T 주의)
   - `Blocks`: 블록 정보 (대문자 B 주의)

## 4. 첫 쿼리 실행

### 간단한 쿼리 테스트

```sql
-- Ethereum 최근 블록 10개 조회
SELECT
  number,
  timestamp,
  transaction_count
FROM
  `bigquery-public-data.crypto_ethereum.blocks`
ORDER BY
  number DESC
LIMIT
  10;
```

### 실행 방법

1. BigQuery 콘솔 상단의 "새 쿼리 작성" 클릭
2. 위 쿼리 붙여넣기
3. "실행" 버튼 클릭
4. 결과 확인

## 5. 비용 관리

### Public Datasets는 무료

- `bigquery-public-data` 프로젝트의 데이터셋은 **무료**로 조회 가능
- 쿼리 처리 비용만 발생 (처리한 데이터 양 기준)

### 비용 절감 팁

1. **기간 제한**: `WHERE block_timestamp >= ...` 절로 최근 데이터만 조회
2. **샘플링**: `TABLESAMPLE SYSTEM (1 PERCENT)` 사용
3. **집계 쿼리**: 필요한 집계만 수행
4. **LIMIT 사용**: 결과 개수 제한

### 비용 모니터링

1. 상단 메뉴에서 "청구" 선택
2. BigQuery 사용량 확인
3. 일일 예산 알림 설정 (권장: $1/일)

## 6. 인증 설정 (로컬 개발용)

### 서비스 계정 생성

1. "IAM 및 관리자" → "서비스 계정" 선택
2. "서비스 계정 만들기" 클릭
3. 이름 입력: `bigquery-reader`
4. 역할 선택: "BigQuery 데이터 뷰어"
5. 키 생성: JSON 형식 다운로드

### 환경 변수 설정

```bash
# .env 파일 생성
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your-key.json"
export GCP_PROJECT_ID="ewha-chain-17"
```

### Python 클라이언트 설정

```python
from google.cloud import bigquery

# 환경 변수가 설정되어 있으면 자동 인증
client = bigquery.Client(project="ewha-chain-17")
```

## 7. 다음 단계

- [데이터셋 스키마 파악](./02_dataset_schema.md)
- [템플릿 쿼리 실행](../../templates/queries/01_tx_volume.sql)
- [Gemini API 설정](./03_gemini_api.md)

## 문제 해결

### "권한이 없습니다" 오류

- 프로젝트가 올바르게 선택되었는지 확인
- BigQuery API가 활성화되었는지 확인

### 쿼리가 너무 느림

- 날짜 범위 축소
- 샘플링 사용
- 필요한 컬럼만 SELECT

### 비용이 걱정됨

- Public Datasets는 무료
- 쿼리 비용은 처리 데이터 양 기준
- 작은 범위로 테스트 후 확장
