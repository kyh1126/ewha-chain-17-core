# 쿼리 실행 가이드

## 1. 템플릿 쿼리 실행

### 단계별 가이드

1. **BigQuery 콘솔 열기**
   - [BigQuery Console](https://console.cloud.google.com/bigquery) 접속

2. **템플릿 쿼리 복사**
   - `templates/queries/` 폴더에서 원하는 쿼리 파일 열기
   - SQL 코드 복사

3. **쿼리 실행**
   - BigQuery 콘솔에서 "새 쿼리 작성" 클릭
   - 쿼리 붙여넣기
   - "실행" 버튼 클릭

4. **결과 확인**
   - 쿼리 결과 테이블 확인
   - 실행 시간 및 처리된 데이터 양 확인

## 2. 쿼리 커스터마이징

### 날짜 범위 변경

```sql
-- 기본: 최근 30일 (transactions 테이블은 block_timestamp 사용)
WHERE block_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)

-- 변경: 최근 7일
WHERE block_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)

-- 변경: 특정 기간
WHERE block_timestamp >= TIMESTAMP('2025-01-01')
  AND block_timestamp < TIMESTAMP('2025-02-01')
```

### 지표 추가/변경

```sql
-- 기본: 거래량만
SELECT
  DATE(block_timestamp) AS date,
  COUNT(*) AS tx_count

-- 변경: 거래량 + 고유 주소 수
SELECT
  DATE(block_timestamp) AS date,
  COUNT(*) AS tx_count,
  COUNT(DISTINCT from_address) AS unique_senders
```

### 필터 추가

```sql
-- 특정 주소만 필터링
WHERE from_address = '0x...'

-- 특정 컨트랙트만 필터링
WHERE to_address IN (
  SELECT address
  FROM `bigquery-public-data.crypto_ethereum.contracts`
  WHERE is_erc20 = TRUE
)
```

## 3. 비용 최적화

### 샘플링 사용

```sql
-- 전체 데이터 대신 1% 샘플만 사용
SELECT *
FROM `bigquery-public-data.crypto_ethereum.transactions`
TABLESAMPLE SYSTEM (1 PERCENT)
```

### 필요한 컬럼만 SELECT

```sql
-- ❌ 나쁜 예: 모든 컬럼 조회
SELECT * FROM ...

-- ✅ 좋은 예: 필요한 컬럼만
SELECT
  block_timestamp,
  from_address,
  to_address,
  value
FROM ...
```

### 집계 쿼리 활용

```sql
-- ❌ 나쁜 예: 전체 데이터 조회 후 집계
SELECT * FROM transactions
-- (Python에서 집계)

-- ✅ 좋은 예: BigQuery에서 집계
SELECT
  DATE(block_timestamp) AS date,
  COUNT(*) AS tx_count
FROM transactions
GROUP BY date
```

## 4. 쿼리 저장 및 재사용

### 저장된 쿼리

1. 쿼리 작성 후 "저장" 버튼 클릭
2. 쿼리 이름 입력
3. 나중에 "저장된 쿼리"에서 재사용

### 뷰 생성

```sql
-- 뷰 생성 (재사용 가능한 가상 테이블)
CREATE OR REPLACE VIEW `ewha-chain-17.daily_tx_summary` AS
SELECT
  DATE(block_timestamp) AS date,
  COUNT(*) AS tx_count
FROM
  `bigquery-public-data.crypto_ethereum.transactions`
WHERE
  block_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
GROUP BY date;
```

## 5. 결과 내보내기

### CSV 다운로드

1. 쿼리 결과 테이블에서 "결과 다운로드" 클릭
2. "CSV로 다운로드" 선택
3. 파일 저장

### Python으로 결과 가져오기

```python
from google.cloud import bigquery

client = bigquery.Client()

query = """
SELECT * FROM ...
"""

results = client.query(query).result()

# DataFrame으로 변환
import pandas as pd
df = results.to_dataframe()

# CSV로 저장
df.to_csv('results.csv', index=False)
```

## 6. 쿼리 성능 최적화

### 인덱스 활용

- BigQuery는 자동으로 인덱싱하지만, WHERE 절에 자주 사용하는 컬럼 사용

### 파티션 활용

- 날짜 기반 필터링 시 `_PARTITIONTIME` 활용 (가능한 경우)

### JOIN 최적화

```sql
-- 작은 테이블을 먼저 필터링
SELECT ...
FROM (
  SELECT * FROM small_table WHERE ...
) AS small
JOIN large_table ON ...
```

## 7. 일반적인 문제 해결

### "쿼리가 너무 느림"

- 날짜 범위 축소
- 샘플링 사용
- 필요한 컬럼만 SELECT
- LIMIT 사용

### "비용이 너무 많이 나옴"

- Public Datasets는 무료지만 쿼리 처리 비용 발생
- 샘플링 활용
- 집계 쿼리로 데이터 양 줄이기

### "결과가 비어있음"

- WHERE 절 필터 확인
- 날짜 범위 확인
- 테이블 이름 확인

## 8. 다음 단계

- [대시보드 생성](./dashboard_creation.md)
- [Gemini API 연동](../onboarding/03_gemini_api.md)
- [최종 산출물 준비](../../deliverables/README.md)
