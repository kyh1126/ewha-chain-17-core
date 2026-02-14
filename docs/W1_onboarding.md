# W1 온보딩 가이드

**기간**: 3월 1주  
**목표**: 목표/지표 확정 + 데이터셋 스키마 파악 + 쿼리 초안(약 10개)

## 📋 W1 체크리스트

- [ ] GCP 계정 생성 및 프로젝트 설정 완료
- [ ] BigQuery API 활성화 완료
- [ ] BigQuery 콘솔 접근 성공
- [ ] Public Datasets 확인 (Ethereum, Solana)
- [ ] 샘플 쿼리 실행 성공
- [ ] 템플릿 쿼리 3개 실행 및 이해
- [ ] 데이터셋 스키마 문서 읽기 완료
- [ ] "내가 분석하고 싶은 지표 1개" 아이디어 제출

## 1. 레포지토리 클론 및 개인 폴더 생성 (15분)

### 1.0 사전 준비

- **Git** 이 설치되어 있어야 합니다. 터미널에서 `git --version` 을 실행해 확인하세요.
  - 설치 안 됨: [Git 설치 가이드](https://git-scm.com/downloads) 참고
- **Python 3.8 이상** 이 설치되어 있어야 합니다 (W3에서 필요). `python3 --version` 으로 확인.

### 1.1 레포지토리 클론

```bash
# 레포지토리 복제
git clone https://github.com/[org]/ewha-chain-17-core.git
cd ewha-chain-17-core
```

> 레포 URL은 팀장이 슬랙/디스코드에 공유합니다.

### 1.2 개인 브랜치 및 폴더 생성

```bash
# 개인 브랜치 생성
git checkout -b members/[본인이름]

# 개인 작업 폴더 생성
mkdir -p members/[본인이름]/queries
mkdir -p members/[본인이름]/dashboard

# 개인 README 생성 (나중에 지표 아이디어 작성)
touch members/[본인이름]/README.md
```

자세한 Git 워크플로우(커밋, PR 생성 등)는 [CONTRIBUTING.md](../CONTRIBUTING.md) 를 참고하세요.

## 2. GCP 환경 설정 (30분)

### 2.1 GCP 계정 생성

1. [Google Cloud Console](https://console.cloud.google.com/) 접속
2. Google 계정으로 로그인
3. 무료 체험 계정 활성화 (크레딧 $300 제공)

### 2.2 프로젝트 생성

1. 상단 프로젝트 선택 드롭다운 클릭
2. "새 프로젝트" 클릭
3. 프로젝트 이름: `ewha-chain-17-[본인이름]` (예: `ewha-chain-17-yoonhee`)
4. "만들기" 클릭
5. 프로젝트 선택 확인

### 2.3 BigQuery API 활성화

1. 왼쪽 메뉴 → "API 및 서비스" → "라이브러리"
2. "BigQuery API" 검색
3. "사용 설정" 클릭

### 2.4 BigQuery 콘솔 접근

1. 왼쪽 메뉴 → "BigQuery" 선택
2. BigQuery 콘솔 확인

**✅ 확인 사항**: BigQuery 콘솔이 정상적으로 열리는지 확인

## 3. Public Datasets 탐색 (20분)

### 3.0 Public Datasets 프로젝트 추가 (처음 한 번만)

`bigquery-public-data`는 기본적으로 탐색기에 보이지 않을 수 있습니다. 다음 방법 중 하나로 추가하세요:

**방법 A** — 검색으로 추가:
1. BigQuery 콘솔 왼쪽 탐색기 상단의 검색창(돋보기)에 `bigquery-public-data` 입력
2. 검색 결과에서 프로젝트 클릭 → "별표" 또는 "고정" 클릭

**방법 B** — 직접 추가:
1. 탐색기 상단 **"+ 추가"** 버튼 클릭
2. "프로젝트 이름으로 별표 표시" 선택
3. `bigquery-public-data` 입력 → "별표 표시" 클릭

이제 왼쪽 탐색기에 `bigquery-public-data` 프로젝트가 표시됩니다.

### 3.1 Ethereum 데이터셋 확인

1. 왼쪽 탐색기에서 `bigquery-public-data` 프로젝트 확장
2. `crypto_ethereum` 데이터셋 확인
3. 주요 테이블 확인:
   - `transactions`: 모든 트랜잭션
   - `blocks`: 블록 정보
   - `contracts`: 컨트랙트 정보
   - `token_transfers`: 토큰 전송

### 3.2 Solana 데이터셋 확인

> **⚠️ Solana 데이터 업데이트 중단 안내**  
> `crypto_solana_mainnet_us` 데이터셋은 **2025년 3월 31일 이후 업데이트가 중단**되었습니다.  
> 과거 데이터(~2025-03-31)는 정상 조회할 수 있으므로, **고정 날짜 범위**(예: 2025년 3월)를 사용해 분석합니다.  
> Ethereum은 실시간 데이터, Solana는 과거 스냅샷으로 체인 비교를 수행합니다.

1. `crypto_solana_mainnet_us` 데이터셋 확인
2. 주요 테이블 확인:
   - `Transactions`: 모든 트랜잭션 (~2025-03-31, 대문자 T 주의)
   - `Blocks`: 블록 정보 (대문자 B 주의)

### 3.3 테이블 미리보기

1. `crypto_ethereum.blocks` 테이블 클릭
2. "미리보기" 탭 클릭
3. 데이터 구조 확인

**✅ 확인 사항**: Ethereum과 Solana 데이터셋의 구조를 이해했는지 확인

## 4. 첫 쿼리 실행 (30분)

### 4.1 기본 쿼리 실행

1. BigQuery 콘솔 상단 "새 쿼리 작성" 클릭
2. 다음 쿼리 붙여넣기:

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

3. "실행" 버튼 클릭
4. 결과 확인

**✅ 확인 사항**: 쿼리가 정상적으로 실행되고 결과가 표시되는지 확인

### 4.2 템플릿 쿼리 실행

다음 순서로 템플릿 쿼리를 실행해보세요:

1. **`templates/sql/01_basic_exploration.sql`**
   - 기본 SELECT, WHERE, ORDER BY 문법 학습
   - 실행 시간: 약 5-10초

2. **`templates/sql/02_aggregation.sql`**
   - COUNT, SUM, AVG 등 집계 함수 학습
   - 실행 시간: 약 10-20초

3. **`templates/sql/03_join.sql`**
   - 테이블 JOIN 방법 학습
   - 실행 시간: 약 15-30초

**💡 팁**: 각 쿼리의 주석을 읽고 "왜 이렇게 썼는지" 이해하세요.

### 4.3 쿼리 수정해보기

템플릿 쿼리를 수정해보세요:

- 날짜 범위 변경: `INTERVAL 7 DAY` → `INTERVAL 30 DAY`
- LIMIT 변경: `LIMIT 10` → `LIMIT 100`
- 필터 추가: `WHERE` 절에 조건 추가

**✅ 확인 사항**: 쿼리를 수정하고 실행할 수 있는지 확인

## 5. 데이터셋 스키마 이해 (40분)

### 5.1 Ethereum 스키마 학습

[데이터셋 스키마 가이드](./onboarding/02_dataset_schema.md) 문서를 읽고 다음을 이해하세요:

- `transactions` 테이블의 주요 컬럼
- `blocks` 테이블의 주요 컬럼
- `contracts` 테이블의 주요 컬럼

### 5.2 Solana 스키마 학습

- `Transactions` 테이블의 주요 컬럼 (대문자 T)
- `Blocks` 테이블의 주요 컬럼 (대문자 B)
- `accounts` 배열(`ARRAY<STRUCT>`) 언패킹 방법

### 5.3 스키마 차이점 이해

Ethereum과 Solana의 데이터 구조 차이를 이해하세요:

| 항목 | Ethereum | Solana |
|------|----------|--------|
| 트랜잭션 구조 | 단순 (from/to/value) | 복잡 (accounts, log_messages 등) |
| 가스비 | 가변 (gas_price * receipt_gas_used) | 고정 (fee) |
| 실패 표시 | receipt_status (0/1) | status ('Success' 또는 에러), err 컬럼 |

**✅ 확인 사항**: 두 네트워크의 데이터 구조 차이를 이해했는지 확인

## 6. 쿼리 초안 작성 (2시간)

### 6.1 분석하고 싶은 지표 선택

다음 중 하나를 선택하거나 본인만의 아이디어를 제시하세요:

- 거래량 추이 (일별/시간별)
- 활성 주소 수
- 수수료/가스비 추이
- 실패 트랜잭션 비율
- 특정 컨트랙트 활동 분석
- 토큰 전송 패턴
- 네트워크 혼잡도

### 6.2 쿼리 작성

템플릿 쿼리를 참고하여 본인의 지표를 분석하는 쿼리를 작성하세요:

1. 템플릿 쿼리 복사
2. 날짜 범위, 필터 등 수정
3. 필요한 컬럼 추가
4. 실행 및 결과 확인

### 6.3 쿼리 저장

1. BigQuery 콘솔에서 쿼리 작성
2. "저장" 버튼 클릭
3. 쿼리 이름 입력 (예: `my_tx_volume_analysis`)
4. `members/[본인이름]/queries/` 폴더에도 저장

**✅ 확인 사항**: 최소 3개 이상의 쿼리 초안 작성 완료

## 7. 개별 지표 아이디어 제출 (30분)

### 7.1 아이디어 작성

다음 형식으로 아이디어를 정리하세요:

```markdown
# 분석 지표: [지표 이름]

## 목적
- 왜 이 지표를 분석하고 싶은지

## 분석 방법
- 어떤 데이터를 사용할지
- 어떤 쿼리를 작성할지

## 예상 결과
- 어떤 인사이트를 얻을 수 있을지
```

### 7.2 제출 방법

1. `members/[본인이름]/README.md` 파일 생성
2. 위 형식으로 아이디어 작성
3. GitHub에 커밋 및 PR 생성
4. 슬랙 #core-questions 채널에 공유

**✅ 확인 사항**: 아이디어가 명확하고 실행 가능한지 확인

## 8. 자주 묻는 질문 (FAQ)

### 환경 설정 관련

**Q: GCP 무료 체험 크레딧이 부족하면?**  
A: Public Datasets는 무료입니다. 쿼리 처리 비용만 발생하지만, 작은 범위로 테스트하면 비용이 거의 들지 않습니다.

**Q: 프로젝트를 여러 개 만들어도 되나요?**  
A: 네, 개인 프로젝트를 만드는 것을 권장합니다. 프로젝트 이름에 본인 이름을 포함하세요.

### BigQuery 관련

**Q: 쿼리가 너무 느려요**  
A: 날짜 범위를 줄이거나 LIMIT을 사용하세요. 샘플링(`TABLESAMPLE`)도 활용할 수 있습니다.

**Q: "권한이 없습니다" 오류가 나요**  
A: BigQuery API가 활성화되었는지 확인하세요. 프로젝트가 올바르게 선택되었는지도 확인하세요.

**Q: 비용이 걱정돼요**  
A: Public Datasets는 무료입니다. 쿼리 처리 비용은 처리한 데이터 양에 비례하지만, 작은 범위로 테스트하면 비용이 거의 들지 않습니다. Dry Run으로 비용을 미리 확인할 수 있습니다.

### 쿼리 작성 관련

**Q: SQL을 잘 모르는데 괜찮나요?**  
A: 템플릿 쿼리를 제공하니 주석을 읽고 이해하는 것부터 시작하세요. 막히면 슬랙에 질문해주세요.

**Q: 템플릿 쿼리를 그대로 사용해도 되나요?**  
A: 학습용으로는 괜찮지만, 최종 산출물에는 본인만의 쿼리를 작성해야 합니다. 템플릿을 참고하여 수정하세요.

**Q: 쿼리 결과를 어떻게 저장하나요?**  
A: BigQuery 콘솔에서 "결과 다운로드" 버튼을 사용하거나, `scripts/run_query.py` 스크립트를 사용하세요.

### 데이터셋 관련

**Q: Ethereum과 Solana 중 어떤 것을 분석해야 하나요?**  
A: 둘 다 분석하는 것을 권장합니다. 비교 분석이 핵심 목표 중 하나입니다.

**Q: 데이터가 최신인가요?**  
A: 약 1-2시간 지연이 있을 수 있습니다. 최신 데이터가 필요하면 날짜 범위를 조정하세요.

**Q: 특정 기간의 데이터만 조회할 수 있나요?**  
A: 네, `WHERE block_timestamp >= ...` 절을 사용하여 날짜 범위를 지정할 수 있습니다. (blocks 테이블은 `timestamp`, transactions 테이블은 `block_timestamp` 컬럼을 사용합니다.)

## 9. W1 마무리 체크리스트

W1이 끝나기 전에 다음을 확인하세요:

- [ ] GCP 계정 및 BigQuery 설정 완료
- [ ] 템플릿 쿼리 3개 이상 실행 및 이해
- [ ] 데이터셋 스키마 문서 읽기 완료
- [ ] 쿼리 초안 3개 이상 작성
- [ ] 개별 지표 아이디어 제출
- [ ] `members/[본인이름]/` 폴더 생성 및 작업물 업로드
- [ ] 슬랙 #core-questions 채널 가입

## 10. 다음 주 (W2) 준비

W2에서는 다음을 진행합니다:

- 핵심 지표 3~4개 확정
- SQL 재현성 확보
- Looker Studio 연동 시작

W1에서 작성한 쿼리들을 정리하고, W2에서 대시보드로 시각화할 준비를 하세요.

## 11. 도움 받기

막히는 부분이 있으면:

1. **슬랙 #core-questions 채널**에 질문
2. **GitHub Issues**에 버그 리포트
3. **팀장에게 직접 연락** (긴급한 경우)

**💡 팁**: 질문할 때는 다음을 포함하세요:
- 어떤 작업을 하려고 했는지
- 어떤 오류 메시지가 나왔는지
- 어떤 방법을 시도했는지

## 추가 자료

- [BigQuery 설정 가이드](./onboarding/01_bigquery_setup.md)
- [데이터셋 스키마 가이드](./onboarding/02_dataset_schema.md)
- [쿼리 실행 가이드](./guides/query_execution.md)
- [FAQ](./FAQ.md)
