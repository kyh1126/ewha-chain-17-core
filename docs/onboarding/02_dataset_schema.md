# BigQuery 데이터셋 스키마 가이드

## Ethereum 데이터셋 스키마

### `transactions` 테이블

가장 중요한 테이블 중 하나로, 모든 Ethereum 트랜잭션을 포함합니다.

#### 주요 컬럼

| 컬럼명 | 타입 | 설명 |
|--------|------|------|
| `hash` | STRING | 트랜잭션 해시 |
| `from_address` | STRING | 송신자 주소 |
| `to_address` | STRING | 수신자 주소 (NULL 가능) |
| `value` | NUMERIC | 전송된 이더 양 (wei 단위) |
| `gas` | INT64 | 가스 한도 |
| `gas_price` | INT64 | 가스 가격 (wei) |
| `receipt_gas_used` | INT64 | 실제 사용된 가스 |
| `receipt_status` | INT64 | 상태 (1=성공, 0=실패) |
| `block_number` | INT64 | 블록 번호 |
| `block_timestamp` | TIMESTAMP | 블록 타임스탬프 |
| `transaction_index` | INT64 | 블록 내 트랜잭션 인덱스 |

#### 사용 예시

```sql
-- 성공한 트랜잭션만 필터링
WHERE receipt_status = 1

-- 이더 단위로 변환 (wei → ETH)
value / POW(10, 18) AS value_eth

-- 가스비 계산
gas_price * receipt_gas_used AS total_gas_cost
```

### `blocks` 테이블

블록 정보를 포함합니다.

#### 주요 컬럼

| 컬럼명 | 타입 | 설명 |
|--------|------|------|
| `number` | INT64 | 블록 번호 |
| `timestamp` | TIMESTAMP | 블록 타임스탬프 |
| `transaction_count` | INT64 | 트랜잭션 개수 |
| `gas_used` | INT64 | 사용된 가스 총량 |
| `gas_limit` | INT64 | 가스 한도 |

### `contracts` 테이블

스마트 컨트랙트 정보를 포함합니다.

#### 주요 컬럼

| 컬럼명 | 타입 | 설명 |
|--------|------|------|
| `address` | STRING | 컨트랙트 주소 |
| `bytecode` | STRING | 컨트랙트 바이트코드 |
| `is_erc20` | BOOL | ERC-20 토큰 여부 |
| `is_erc721` | BOOL | ERC-721 NFT 여부 |

## Solana 데이터셋 스키마

> **⚠️ 데이터 업데이트 중단 안내**  
> Solana BigQuery Public Dataset(`crypto_solana_mainnet_us`)는 **2025년 3월 31일 이후 업데이트가 중단**되었습니다.  
> 데이터 자체는 조회 가능하지만, 2025년 4월 이후의 신규 트랜잭션은 포함되어 있지 않습니다.  
> 따라서 Solana 쿼리에는 `CURRENT_TIMESTAMP()` 대신 **고정 날짜 범위(예: 2025년 3월)**를 사용합니다.
>
> - 데이터셋 이름: `bigquery-public-data.crypto_solana_mainnet_us`
> - 가용 기간: ~2025-03-31

### `Transactions` 테이블

모든 Solana 트랜잭션을 포함합니다.

> **참고**: 테이블 이름이 대문자 `Transactions`입니다. 쿼리 시 백틱 안에서 정확히 써야 합니다.

#### 주요 컬럼

| 컬럼명 | 타입 | 모드 | 설명 |
|--------|------|------|------|
| `block_slot` | INTEGER | NULLABLE | 블록 슬롯 번호 |
| `block_hash` | STRING | NULLABLE | 블록 해시 |
| `block_timestamp` | TIMESTAMP | NULLABLE | 블록 타임스탬프 (파티셔닝 키) |
| `recent_block_hash` | STRING | NULLABLE | 최근 블록 해시 |
| `signature` | STRING | NULLABLE | 트랜잭션 서명 (= 트랜잭션 ID) |
| `index` | INTEGER | NULLABLE | 블록 내 트랜잭션 인덱스 |
| `fee` | NUMERIC | NULLABLE | 수수료 (lamports, 1 SOL = 10^9 lamports) |
| `status` | STRING | NULLABLE | 트랜잭션 상태 (`"Success"` 또는 에러 정보) |
| `err` | STRING | NULLABLE | 에러 메시지 (성공 시 NULL) |
| `compute_units_consumed` | NUMERIC | NULLABLE | 사용된 컴퓨팅 유닛 |
| `accounts` | ARRAY\<STRUCT\> | REPEATED | 관련 계정 목록 (하위: `pubkey` STRING, `signer` BOOL, `writable` BOOL) |
| `log_messages` | STRING | REPEATED | 실행 로그 메시지 |
| `balance_changes` | ARRAY\<STRUCT\> | REPEATED | SOL 잔액 변동 (하위: `account` STRING, `before` NUMERIC, `after` NUMERIC) |
| `pre_token_balances` | ARRAY\<STRUCT\> | REPEATED | 트랜잭션 전 토큰 잔액 (하위: `account_index`, `mint`, `owner`, `amount`, `decimals`) |
| `post_token_balances` | ARRAY\<STRUCT\> | REPEATED | 트랜잭션 후 토큰 잔액 (동일 구조) |

#### 성공/실패 필터링

```sql
-- ✅ 성공한 트랜잭션만 (status 컬럼은 STRING 타입)
WHERE status = 'Success'

-- ✅ 실패한 트랜잭션만
WHERE status != 'Success'
-- 또는
WHERE err IS NOT NULL
```

#### Accounts 구조

`accounts`는 `ARRAY<STRUCT<pubkey STRING, signer BOOL, writable BOOL>>` 타입입니다.

| 하위 필드 | 타입 | 설명 |
|-----------|------|------|
| `pubkey` | STRING | 계정 주소 (공개키) |
| `signer` | BOOL | 서명자 여부 (TRUE = 이 트랜잭션에 서명함) |
| `writable` | BOOL | 쓰기 가능 여부 |

```sql
-- 첫 번째 계정의 주소 (= 수수료 납부자) 조회
SELECT
  signature,
  accounts[OFFSET(0)].pubkey AS fee_payer
FROM
  `bigquery-public-data.crypto_solana_mainnet_us.Transactions`
WHERE
  block_timestamp >= TIMESTAMP('2025-03-01')
  AND block_timestamp < TIMESTAMP('2025-04-01')
  AND status = 'Success'
LIMIT 10;

-- 고유 서명자 수 집계
SELECT
  DATE(block_timestamp) AS date,
  COUNT(DISTINCT accounts[OFFSET(0)].pubkey) AS unique_signers
FROM
  `bigquery-public-data.crypto_solana_mainnet_us.Transactions`
WHERE
  block_timestamp >= TIMESTAMP('2025-03-01')
  AND block_timestamp < TIMESTAMP('2025-04-01')
  AND status = 'Success'
GROUP BY date
ORDER BY date DESC;

-- Vote 트랜잭션 제외 (Vote 프로그램이 accounts에 포함된 경우 필터링)
SELECT COUNT(*) AS non_vote_tx_count
FROM
  `bigquery-public-data.crypto_solana_mainnet_us.Transactions`
WHERE
  block_timestamp >= TIMESTAMP('2025-03-01')
  AND block_timestamp < TIMESTAMP('2025-04-01')
  AND status = 'Success'
  AND NOT EXISTS (
    SELECT 1 FROM UNNEST(accounts) AS a
    WHERE a.pubkey = 'Vote111111111111111111111111111111111111111'
  );
```

### `Blocks` 테이블

> **참고**: 테이블 이름이 대문자 `Blocks`입니다. 쿼리 시 백틱 안에서 정확히 써야 합니다.

블록 정보를 포함합니다.

#### 주요 컬럼

| 컬럼명 | 타입 | 설명 |
|--------|------|------|
| `slot` | INT64 | 슬롯 번호 |
| `height` | INT64 | 블록 높이 |
| `block_timestamp` | TIMESTAMP | 블록 타임스탬프 |
| `block_hash` | STRING | 블록 해시 |
| `previous_block_hash` | STRING | 이전 블록 해시 |
| `leader` | STRING | 블록 생성 밸리데이터 주소 |
| `leader_reward` | NUMERIC | 리더 보상 (lamports) |
| `transaction_count` | INT64 | 트랜잭션 개수 |

### 기타 테이블

`crypto_solana_mainnet_us` 데이터셋에는 다음 테이블도 존재합니다:

| 테이블명 | 설명 |
|----------|------|
| `Accounts` | 계정 정보 |
| `Block Rewards` | 블록 보상 상세 |
| `Instructions` | 트랜잭션 내 인스트럭션 (별도 테이블) |
| `Token Transfers` | 토큰 전송 기록 |
| `Tokens` | 토큰 메타데이터 |

> **참고**: `Instructions`는 `Transactions` 테이블의 컬럼이 아니라 **별도 테이블**입니다.  
> 인스트럭션 분석이 필요한 경우 `Instructions` 테이블을 `Transactions`와 JOIN하여 사용합니다.

## 유용한 쿼리 패턴

### 1. 시간 범위 필터링

```sql
-- 최근 7일 (blocks 테이블: timestamp, transactions 테이블: block_timestamp)
WHERE block_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)

-- 특정 기간
WHERE block_timestamp >= TIMESTAMP('2025-01-01')
  AND block_timestamp < TIMESTAMP('2025-02-01')
```

### 2. 집계 함수

```sql
-- 일별 집계
SELECT
  DATE(block_timestamp) AS date,
  COUNT(*) AS tx_count,
  SUM(value) AS total_value,
  AVG(gas_price) AS avg_gas_price
FROM ...
GROUP BY date
```

### 3. Top N 쿼리

```sql
SELECT
  address,
  COUNT(*) AS tx_count
FROM ...
GROUP BY address
ORDER BY tx_count DESC
LIMIT 20
```

### 4. JOIN 패턴

```sql
-- 트랜잭션과 블록 정보 결합
SELECT
  t.hash,
  t.value,
  b.timestamp AS block_time
FROM
  `bigquery-public-data.crypto_ethereum.transactions` AS t
JOIN
  `bigquery-public-data.crypto_ethereum.blocks` AS b
ON
  t.block_number = b.number
```

## 데이터 제한사항

### Ethereum

- 데이터는 2015년 7월부터 시작
- 최신 데이터는 약 1-2시간 지연 가능
- 일부 컬럼은 NULL일 수 있음 (예: `to_address`)

### Solana

- 데이터는 2020년 3월부터 시작, **2025년 3월 31일까지** (이후 업데이트 중단)
- **테이블 이름이 대문자로 시작**: `Transactions`, `Blocks`, `Instructions` 등 (쿼리 시 정확한 대소문자 필요)
- Vote 트랜잭션이 대부분 (필터링 필요 — `UNNEST(accounts)`로 Vote 프로그램 주소 확인)
- `accounts`, `balance_changes` 등 ARRAY<STRUCT> 컬럼은 `UNNEST()`로 언패킹 필요
- 인스트럭션 분석은 `Instructions` 별도 테이블 사용 (`Transactions` 테이블에는 `instructions` 컬럼 없음)
- 쿼리 시 `CURRENT_TIMESTAMP()` 대신 **고정 날짜 범위** 사용 필수

## 다음 단계

- [템플릿 쿼리 실행](../../templates/queries/01_tx_volume.sql)
- [Looker Studio 연결](../guides/dashboard_creation.md)
- [Gemini API 설정](./03_gemini_api.md)
