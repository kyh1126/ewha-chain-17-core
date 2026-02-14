-- ============================================
-- 템플릿 03: 수수료/가스 지표 분석
-- ============================================
-- 목적: 네트워크 수수료 추이 및 사용자 부담 분석

-- Ethereum: 일별 평균 가스비 추이
-- 참고: transactions 테이블에서 가스 사용량은 receipt_gas_used 컬럼 사용
--        (gas_used는 blocks 테이블 컬럼이므로 혼동 주의)
-- 참고: 중앙값은 APPROX_QUANTILES 집계 함수를 사용 (GROUP BY와 호환)
SELECT
  DATE(block_timestamp) AS date,
  COUNT(*) AS tx_count,
  AVG(gas_price * receipt_gas_used) / POW(10, 18) AS avg_gas_cost_eth,
  APPROX_QUANTILES(gas_price * receipt_gas_used, 2)[OFFSET(1)]
    / POW(10, 18) AS median_gas_cost_eth,
  MAX(gas_price * receipt_gas_used) / POW(10, 18) AS max_gas_cost_eth
FROM
  `bigquery-public-data.crypto_ethereum.transactions`
WHERE
  block_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
  AND receipt_status = 1
GROUP BY
  date
ORDER BY
  date DESC;

-- Ethereum: 시간대별 가스비 패턴 (피크 시간 분석)
SELECT
  EXTRACT(HOUR FROM block_timestamp) AS hour_of_day,
  AVG(gas_price * receipt_gas_used) / POW(10, 18) AS avg_gas_cost_eth,
  COUNT(*) AS tx_count
FROM
  `bigquery-public-data.crypto_ethereum.transactions`
WHERE
  block_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
  AND receipt_status = 1
GROUP BY
  hour_of_day
ORDER BY
  hour_of_day;

-- Solana: 일별 평균 수수료 추이
-- ⚠️ 주의: Solana Public Dataset는 2025-03-31 이후 업데이트 중단. 고정 날짜 범위 사용.
-- 참고: fee 컬럼은 NUMERIC 타입 (lamports 단위, 1 SOL = 10^9 lamports)
-- 참고: 성공 여부는 status 컬럼(STRING)으로 필터링
-- 참고: 중앙값은 APPROX_QUANTILES 집계 함수를 사용 (GROUP BY와 호환)
SELECT
  DATE(block_timestamp) AS date,
  COUNT(*) AS tx_count,
  AVG(fee) / POW(10, 9) AS avg_fee_sol,
  APPROX_QUANTILES(fee, 2)[OFFSET(1)]
    / POW(10, 9) AS median_fee_sol
FROM
  `bigquery-public-data.crypto_solana_mainnet_us.Transactions`
WHERE
  -- 고정 기간: 2025년 3월 (데이터 가용 마지막 달)
  block_timestamp >= TIMESTAMP('2025-03-01')
  AND block_timestamp < TIMESTAMP('2025-04-01')
  AND status = 'Success'
GROUP BY
  date
ORDER BY
  date DESC;

-- ============================================
-- 커스터마이징 팁
-- ============================================
-- 1. 가스비 비교: Ethereum vs Solana 수수료 차이 시각화
-- 2. 특정 이벤트 분석: NFT 민팅, 토큰 스왑 등 특정 활동 시 가스비 추이
-- 3. 사용자 부담 분석: 평균 사용자가 지불하는 수수료 금액
-- 4. 네트워크 혼잡도: 가스비 상승 = 네트워크 혼잡도 증가
