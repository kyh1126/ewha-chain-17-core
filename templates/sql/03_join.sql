-- ============================================
-- 샘플 쿼리 03: 테이블 JOIN (결합)
-- ============================================
-- 목적: 여러 테이블을 결합하여 더 풍부한 데이터 분석
-- 학습 포인트: JOIN 문법, 테이블 간 관계 이해
-- 실행 시간: 약 15-30초
-- 처리 데이터: 약 100-200MB (비용 중간)

-- ============================================
-- 쿼리 설명
-- ============================================
-- 이 쿼리는 트랜잭션 테이블과 블록 테이블을 결합하여
-- 트랜잭션 정보와 해당 블록의 정보를 함께 조회합니다.
-- 예: 특정 트랜잭션의 가스비와 해당 블록의 총 가스 사용량을 함께 확인

SELECT
  -- 트랜잭션 정보
  t.hash AS transaction_hash,
  t.from_address,
  t.to_address,
  
  -- 전송된 이더 양 (ETH 단위)
  t.value / POW(10, 18) AS value_eth,
  
  -- 트랜잭션 가스비 (ETH 단위)
  (t.gas_price * t.receipt_gas_used) / POW(10, 18) AS gas_cost_eth,
  
  -- 트랜잭션 상태
  CASE
    WHEN t.receipt_status = 1 THEN 'Success'
    WHEN t.receipt_status = 0 THEN 'Failed'
    ELSE 'Unknown'
  END AS transaction_status,
  
  -- 블록 정보 (JOIN으로 가져온 데이터)
  b.number AS block_number,
  b.timestamp AS block_timestamp,
  b.transaction_count AS transactions_in_block,
  b.gas_used AS block_gas_used,
  b.gas_limit AS block_gas_limit,
  
  -- 블록 가스 사용률 계산
  ROUND(100.0 * b.gas_used / NULLIF(b.gas_limit, 0), 2) AS block_gas_usage_percent,
  
  -- 트랜잭션이 블록 내에서 차지하는 가스 비율
  ROUND(
    100.0 * t.receipt_gas_used / NULLIF(b.gas_used, 0),
    4
  ) AS tx_gas_share_percent

FROM
  -- 메인 테이블: 트랜잭션
  `bigquery-public-data.crypto_ethereum.transactions` AS t

-- ============================================
-- JOIN 설명
-- ============================================
-- INNER JOIN: 두 테이블 모두에 존재하는 데이터만 조회
-- LEFT JOIN: 왼쪽 테이블(transactions)의 모든 데이터 + 오른쪽 테이블(blocks)의 매칭 데이터
-- RIGHT JOIN: 오른쪽 테이블의 모든 데이터 + 왼쪽 테이블의 매칭 데이터
-- FULL OUTER JOIN: 양쪽 테이블의 모든 데이터
--
-- 여기서는 INNER JOIN을 사용: 블록 정보가 있는 트랜잭션만 조회

INNER JOIN
  -- 결합할 테이블: 블록
  `bigquery-public-data.crypto_ethereum.blocks` AS b
  
  -- JOIN 조건: 트랜잭션의 블록 번호 = 블록의 번호
  ON t.block_number = b.number

WHERE
  -- 최근 7일간의 데이터만 조회
  t.block_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
  
  -- 성공한 트랜잭션만 필터링
  AND t.receipt_status = 1
  
  -- 이더 전송이 있는 트랜잭션만 (0이 아닌 value)
  AND t.value > 0
  
  -- NULL 값 제외
  AND t.from_address IS NOT NULL
  AND t.to_address IS NOT NULL

ORDER BY
  -- 가스비가 높은 순서대로 정렬 (비싼 트랜잭션 확인)
  gas_cost_eth DESC

LIMIT
  -- 상위 20개만 조회
  20;

-- ============================================
-- 실행 결과 예시
-- ============================================
-- transaction_hash | from_address | to_address | value_eth | gas_cost_eth | transaction_status | block_number | ...
-- 0xabc123...     | 0x123...     | 0x456...   | 10.5      | 0.05         | Success            | 18500000     | ...
-- ...

-- ============================================
-- JOIN 종류 비교
-- ============================================
-- 1. INNER JOIN (내부 조인)
--    - 양쪽 테이블에 모두 존재하는 데이터만
--    - 가장 일반적이고 빠름
--    - 예: 블록이 있는 트랜잭션만
--
-- 2. LEFT JOIN (왼쪽 외부 조인)
--    - 왼쪽 테이블의 모든 데이터 + 오른쪽 매칭 데이터
--    - 오른쪽에 없으면 NULL
--    - 예: 모든 트랜잭션 + 블록 정보 (없으면 NULL)
--
-- 3. RIGHT JOIN (오른쪽 외부 조인)
--    - 오른쪽 테이블의 모든 데이터 + 왼쪽 매칭 데이터
--    - 왼쪽에 없으면 NULL
--    - 예: 모든 블록 + 트랜잭션 정보
--
-- 4. FULL OUTER JOIN (완전 외부 조인)
--    - 양쪽 테이블의 모든 데이터
--    - 매칭되지 않으면 NULL
--    - BigQuery에서는 지원하지 않을 수 있음

-- ============================================
-- 커스터마이징 팁
-- ============================================
-- 1. JOIN 타입 변경: INNER JOIN → LEFT JOIN (블록 정보 없는 트랜잭션도 포함)
-- 2. 추가 테이블 JOIN: contracts 테이블과 JOIN하여 컨트랙트 정보 추가
-- 3. 필터 추가: WHERE 절에 ROUND(100.0 * b.gas_used / NULLIF(b.gas_limit, 0), 2) > 90 추가 (가스 거의 다 쓴 블록만, SELECT alias는 WHERE에서 사용 불가)
-- 4. 집계와 결합: GROUP BY를 추가하여 블록별 통계 계산

-- ============================================
-- 고급 예시: 3개 테이블 JOIN
-- ============================================
/*
-- 트랜잭션 + 블록 + 컨트랙트 정보 결합
SELECT
  t.hash,
  t.from_address,
  t.to_address,
  t.value / POW(10, 18) AS value_eth,
  b.number AS block_number,
  c.is_erc20 AS is_token_contract,
  c.is_erc721 AS is_nft_contract
FROM
  `bigquery-public-data.crypto_ethereum.transactions` AS t
INNER JOIN
  `bigquery-public-data.crypto_ethereum.blocks` AS b
  ON t.block_number = b.number
LEFT JOIN
  `bigquery-public-data.crypto_ethereum.contracts` AS c
  ON t.to_address = c.address
WHERE
  t.block_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
LIMIT 10;
*/

-- ============================================
-- 성능 최적화 팁
-- ============================================
-- 1. 작은 테이블을 먼저 필터링: WHERE 절로 데이터 양 줄이기
-- 2. 필요한 컬럼만 SELECT: * 대신 필요한 컬럼만 선택
-- 3. 인덱스 활용: JOIN 조건에 사용하는 컬럼에 인덱스가 있는지 확인
-- 4. 날짜 필터 우선: 가장 먼저 날짜 범위로 필터링

-- ============================================
-- 다음 단계
-- ============================================
-- 이 쿼리를 이해했다면 실제 분석 쿼리로 넘어가세요:
-- - templates/queries/01_tx_volume.sql: 거래량 분석
-- - templates/queries/02_active_addresses.sql: 활성 주소 분석
-- - templates/queries/03_fee_gas.sql: 수수료 분석
