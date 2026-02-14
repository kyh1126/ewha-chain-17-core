-- ============================================
-- 템플릿 01: 거래량 추이 분석 (TPS 유사 지표)
-- ============================================
-- 목적: 시간대별 트랜잭션 수를 집계하여 네트워크 처리량 추이 파악
-- 활용: Solana vs Ethereum 비교, 특정 이벤트 시점 분석

-- Ethereum 거래량 추이 (일별)
SELECT
  DATE(block_timestamp) AS date,
  COUNT(*) AS tx_count,
  COUNT(DISTINCT from_address) AS unique_senders
FROM
  `bigquery-public-data.crypto_ethereum.transactions`
WHERE
  -- 최근 30일 데이터만 조회 (비용 절감)
  block_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
  AND receipt_status = 1  -- 성공한 트랜잭션만
GROUP BY
  date
ORDER BY
  date DESC;

-- Solana 거래량 추이 (일별)
-- ⚠️ 주의: Solana Public Dataset(crypto_solana_mainnet_us)는 2025-03-31 이후 업데이트가 중단되었습니다.
--          따라서 CURRENT_TIMESTAMP() 대신 고정 날짜 범위를 사용합니다.
-- 참고: 테이블 이름은 대문자 Transactions
-- 참고: 성공 여부는 status 컬럼(STRING 타입)으로 'Success' 비교
-- 참고: accounts[OFFSET(0)].pubkey = 첫 번째 계정(수수료 납부자/서명자)의 주소
-- 참고: vote 트랜잭션 제외 시 accounts에서 Vote 프로그램 주소 필터링
SELECT
  DATE(block_timestamp) AS date,
  COUNT(*) AS tx_count,
  COUNT(DISTINCT accounts[OFFSET(0)].pubkey) AS unique_signers
FROM
  `bigquery-public-data.crypto_solana_mainnet_us.Transactions`
WHERE
  -- 고정 기간: 2025년 3월 (데이터 가용 마지막 달)
  block_timestamp >= TIMESTAMP('2025-03-01')
  AND block_timestamp < TIMESTAMP('2025-04-01')
  AND status = 'Success'
  -- vote 트랜잭션 제외: Vote 프로그램이 accounts에 포함된 트랜잭션 필터링
  AND NOT EXISTS (
    SELECT 1 FROM UNNEST(accounts) AS a
    WHERE a.pubkey = 'Vote111111111111111111111111111111111111111'
  )
GROUP BY
  date
ORDER BY
  date DESC;

-- ============================================
-- 커스터마이징 팁
-- ============================================
-- 1. 시간 단위 변경: DATE() → DATETIME_TRUNC(block_timestamp, HOUR)
-- 2. 특정 기간 집중: WHERE 절에 날짜 범위 추가
-- 3. 추가 필터: 특정 주소, 컨트랙트 등으로 필터링
-- 4. 비용 절감: LIMIT 사용 또는 샘플링 (TABLESAMPLE)
