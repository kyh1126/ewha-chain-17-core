-- ============================================
-- 샘플 쿼리 02: 집계 함수 활용
-- ============================================
-- 목적: COUNT, SUM, AVG, MAX, MIN 등 집계 함수를 사용하여 데이터 요약
-- 학습 포인트: GROUP BY, 집계 함수, 날짜 함수
-- 실행 시간: 약 10-20초
-- 처리 데이터: 약 50-100MB (비용 낮음)

-- ============================================
-- 쿼리 설명
-- ============================================
-- 이 쿼리는 Ethereum 네트워크의 일별 트랜잭션 통계를 계산합니다.
-- 일별로 총 트랜잭션 수, 고유 송신자 수, 평균 가스비 등을 집계합니다.

SELECT
  -- DATE() 함수로 타임스탬프를 날짜로 변환 (시간 제거)
  DATE(block_timestamp) AS transaction_date,
  
  -- COUNT(*): 해당 날짜의 모든 트랜잭션 개수
  COUNT(*) AS total_transactions,
  
  -- COUNT(DISTINCT ...): 고유한 값의 개수 (중복 제거)
  -- from_address: 트랜잭션을 보낸 주소
  COUNT(DISTINCT from_address) AS unique_senders,
  
  -- SUM(): 합계 계산
  -- value: 전송된 이더 양 (wei 단위)
  -- POW(10, 18): wei를 ETH로 변환 (1 ETH = 10^18 wei)
  SUM(value) / POW(10, 18) AS total_eth_transferred,
  
  -- AVG(): 평균 계산
  -- gas_price * receipt_gas_used: 실제 지불한 가스비
  AVG(gas_price * receipt_gas_used) / POW(10, 18) AS avg_gas_cost_eth,
  
  -- MIN(): 최솟값
  MIN(gas_price * receipt_gas_used) / POW(10, 18) AS min_gas_cost_eth,
  
  -- MAX(): 최댓값
  MAX(gas_price * receipt_gas_used) / POW(10, 18) AS max_gas_cost_eth,
  
  -- 성공한 트랜잭션 비율 계산
  -- receipt_status = 1: 성공, 0: 실패
  ROUND(
    100.0 * SUM(CASE WHEN receipt_status = 1 THEN 1 ELSE 0 END) / COUNT(*),
    2
  ) AS success_rate_percent

FROM
  -- Ethereum 트랜잭션 데이터
  `bigquery-public-data.crypto_ethereum.transactions`

WHERE
  -- 최근 30일간의 데이터만 조회
  block_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
  
  -- NULL 값 제외 (데이터 품질 향상)
  AND from_address IS NOT NULL
  AND to_address IS NOT NULL

GROUP BY
  -- GROUP BY: 집계할 그룹 지정 (날짜별로 그룹화)
  transaction_date

ORDER BY
  -- 최신 날짜부터 표시
  transaction_date DESC;

-- ============================================
-- 실행 결과 예시
-- ============================================
-- transaction_date | total_transactions | unique_senders | total_eth_transferred | avg_gas_cost_eth | success_rate_percent
-- 2025-03-15       | 1200000           | 450000         | 50000.5              | 0.002            | 98.5
-- 2025-03-14       | 1150000           | 440000         | 48000.2              | 0.0021           | 98.3
-- ...

-- ============================================
-- 집계 함수 설명
-- ============================================
-- COUNT(*): 모든 행의 개수
-- COUNT(column): NULL이 아닌 값의 개수
-- COUNT(DISTINCT column): 고유한 값의 개수
-- SUM(column): 합계
-- AVG(column): 평균
-- MIN(column): 최솟값
-- MAX(column): 최댓값
-- 
-- 중요: 집계 함수를 사용할 때는 GROUP BY로 그룹을 지정해야 합니다!

-- ============================================
-- 커스터마이징 팁
-- ============================================
-- 1. 시간 단위 변경: DATE(block_timestamp) → DATETIME_TRUNC(block_timestamp, HOUR) (시간별 집계)
-- 2. 추가 필터: WHERE 절에 value > 0 추가 (이더 전송이 있는 트랜잭션만)
-- 3. 통계 추가: PERCENTILE_CONT(gas_cost, 0.5) 추가 (중앙값 계산)
-- 4. Solana 버전: FROM 절을 crypto_solana_mainnet_us.Transactions로 변경하고 컬럼명 조정

-- ============================================
-- Solana 버전 예시
-- ⚠️ 주의: Solana Public Dataset는 2025-03-31 이후 업데이트 중단.
--          CURRENT_TIMESTAMP() 대신 고정 날짜 범위를 사용합니다.
-- ============================================
/*
SELECT
  DATE(block_timestamp) AS transaction_date,
  COUNT(*) AS total_transactions,
  COUNT(DISTINCT accounts[OFFSET(0)].pubkey) AS unique_signers,
  AVG(fee) / POW(10, 9) AS avg_fee_sol,  -- lamports를 SOL로 변환
  ROUND(
    100.0 * SUM(CASE WHEN status = 'Success' THEN 1 ELSE 0 END) / COUNT(*),
    2
  ) AS success_rate_percent
FROM
  `bigquery-public-data.crypto_solana_mainnet_us.Transactions`
WHERE
  -- 고정 기간: 2025년 3월 (데이터 가용 마지막 달)
  block_timestamp >= TIMESTAMP('2025-03-01')
  AND block_timestamp < TIMESTAMP('2025-04-01')
GROUP BY
  transaction_date
ORDER BY
  transaction_date DESC;
*/

-- ============================================
-- 다음 단계
-- ============================================
-- 이 쿼리를 이해했다면 다음 쿼리로 넘어가세요:
-- - 03_join.sql: 여러 테이블을 결합하는 방법
-- - templates/queries/01_tx_volume.sql: 실제 분석 쿼리 예시
