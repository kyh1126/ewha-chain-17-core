-- ============================================
-- 템플릿 04: 실패/리버트 관련 지표
-- ============================================
-- 목적: 트랜잭션 실패율 및 원인 분석

-- Ethereum: 일별 실패 트랜잭션 비율
SELECT
  DATE(block_timestamp) AS date,
  COUNT(*) AS total_tx,
  SUM(CASE WHEN receipt_status = 0 THEN 1 ELSE 0 END) AS failed_tx,
  ROUND(
    100.0 * SUM(CASE WHEN receipt_status = 0 THEN 1 ELSE 0 END) / COUNT(*),
    2
  ) AS failure_rate_percent
FROM
  `bigquery-public-data.crypto_ethereum.transactions`
WHERE
  block_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
GROUP BY
  date
ORDER BY
  date DESC;

-- Ethereum: 실패 원인 분석 (가스 부족 vs 기타)
-- 참고: transactions 테이블에서 가스 한도는 `gas` 컬럼 (blocks 테이블의 gas_limit과 혼동 주의)
SELECT
  DATE(block_timestamp) AS date,
  COUNT(*) AS total_failed,
  SUM(
    CASE
      WHEN receipt_gas_used = gas THEN 1
      ELSE 0
    END
  ) AS out_of_gas_count,
  SUM(
    CASE
      WHEN receipt_gas_used < gas THEN 1
      ELSE 0
    END
  ) AS revert_count
FROM
  `bigquery-public-data.crypto_ethereum.transactions`
WHERE
  block_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
  AND receipt_status = 0  -- 실패한 트랜잭션만
GROUP BY
  date
ORDER BY
  date DESC;

-- Solana: 일별 실패 트랜잭션 비율
-- ⚠️ 주의: Solana Public Dataset는 2025-03-31 이후 업데이트 중단. 고정 날짜 범위 사용.
-- 참고: status 컬럼(STRING)이 'Success'가 아닌 경우 실패, err 컬럼에 에러 상세 정보
SELECT
  DATE(block_timestamp) AS date,
  COUNT(*) AS total_tx,
  SUM(CASE WHEN status != 'Success' THEN 1 ELSE 0 END) AS failed_tx,
  ROUND(
    100.0 * SUM(CASE WHEN status != 'Success' THEN 1 ELSE 0 END) / COUNT(*),
    2
  ) AS failure_rate_percent
FROM
  `bigquery-public-data.crypto_solana_mainnet_us.Transactions`
WHERE
  -- 고정 기간: 2025년 3월 (데이터 가용 마지막 달)
  block_timestamp >= TIMESTAMP('2025-03-01')
  AND block_timestamp < TIMESTAMP('2025-04-01')
GROUP BY
  date
ORDER BY
  date DESC;

-- ============================================
-- 커스터마이징 팁
-- ============================================
-- 1. 특정 컨트랙트 실패율: WHERE 절에 컨트랙트 주소 필터 추가
-- 2. 실패 패턴 분석: 시간대별, 요일별 실패율 비교
-- 3. Solana의 경우: err 컬럼 및 log_messages 분석
-- 4. 네트워크 상태 연관성: 실패율과 네트워크 혼잡도 상관관계 분석
