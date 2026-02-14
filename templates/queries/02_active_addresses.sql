-- ============================================
-- 템플릿 02: 활성 주소/프로그램(컨트랙트) Top N
-- ============================================
-- 목적: 가장 활발한 주소나 스마트컨트랙트를 식별하여 네트워크 활동 패턴 파악

-- Ethereum: 가장 활발한 주소 Top 20
SELECT
  to_address AS address,
  COUNT(*) AS tx_count,
  COUNT(DISTINCT from_address) AS unique_senders,
  SUM(value) / POW(10, 18) AS total_eth_received
FROM
  `bigquery-public-data.crypto_ethereum.transactions`
WHERE
  block_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
  AND receipt_status = 1
  AND to_address IS NOT NULL
GROUP BY
  address
ORDER BY
  tx_count DESC
LIMIT
  20;

-- Ethereum: 가장 활발한 컨트랙트 Top 20
SELECT
  to_address AS contract_address,
  COUNT(*) AS tx_count,
  COUNT(DISTINCT from_address) AS unique_users,
  AVG(gas_price * receipt_gas_used) / POW(10, 18) AS avg_gas_cost_eth
FROM
  `bigquery-public-data.crypto_ethereum.transactions`
WHERE
  block_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
  AND receipt_status = 1
  AND to_address IN (
    -- 컨트랙트 주소만 필터링 (코드가 있는 주소)
    SELECT address
    FROM `bigquery-public-data.crypto_ethereum.contracts`
  )
GROUP BY
  contract_address
ORDER BY
  tx_count DESC
LIMIT
  20;

-- Solana: 가장 활발한 서명자(수수료 납부자) Top 20
-- ⚠️ 주의: Solana Public Dataset는 2025-03-31 이후 업데이트 중단. 고정 날짜 범위 사용.
-- 참고: accounts는 ARRAY<STRUCT<pubkey STRING, signer BOOL, writable BOOL>>
-- 참고: accounts[OFFSET(0)].pubkey = 첫 번째 계정 = 수수료 납부자
SELECT
  accounts[OFFSET(0)].pubkey AS fee_payer,
  COUNT(*) AS tx_count,
  SUM(fee) / POW(10, 9) AS total_fee_sol
FROM
  `bigquery-public-data.crypto_solana_mainnet_us.Transactions`
WHERE
  -- 고정 기간: 2025년 3월 1~7일 (1주일)
  block_timestamp >= TIMESTAMP('2025-03-01')
  AND block_timestamp < TIMESTAMP('2025-03-08')
  AND status = 'Success'
GROUP BY
  fee_payer
ORDER BY
  tx_count DESC
LIMIT
  20;

-- ============================================
-- 커스터마이징 팁
-- ============================================
-- 1. 기간 조정: INTERVAL 7 DAY → 30 DAY 등
-- 2. 필터 추가: 특정 토큰, DEX 등으로 필터링
-- 3. 집계 방식 변경: COUNT → SUM, AVG 등
-- 4. Solana의 경우: 프로그램 이름 매핑 테이블과 JOIN하여 가독성 향상
