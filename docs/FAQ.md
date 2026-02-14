# 자주 묻는 질문 (FAQ)

이 문서는 프로그램 진행 중 자주 묻는 질문과 답변을 정리한 것입니다.

## 📋 목차

- [환경 설정](#환경-설정)
- [BigQuery 관련](#bigquery-관련)
- [Gemini API 관련](#gemini-api-관련)
- [쿼리 작성](#쿼리-작성)
- [대시보드 관련](#대시보드-관련)
- [비용 관련](#비용-관련)
- [일정 및 산출물](#일정-및-산출물)
- [기술적 문제 해결](#기술적-문제-해결)

---

## 환경 설정

### Q: GCP 무료 체험 크레딧이 부족하면?

**A**: Public Datasets는 무료입니다. 쿼리 처리 비용만 발생하지만, 작은 범위로 테스트하면 비용이 거의 들지 않습니다. 또한 Dry Run 기능으로 비용을 미리 확인할 수 있습니다.

```bash
# 비용 확인 (Dry Run)
python scripts/run_query.py my_query.sql --dry-run
```

### Q: 프로젝트를 여러 개 만들어도 되나요?

**A**: 네, 개인 프로젝트를 만드는 것을 권장합니다. 프로젝트 이름에 본인 이름을 포함하세요 (예: `ewha-chain-17-yoonhee`).

### Q: 서비스 계정 키 파일이 필요한가요?

**A**: 로컬에서 스크립트를 실행할 때만 필요합니다. BigQuery 콘솔에서는 Google 계정으로 자동 인증됩니다.

### Q: 환경 변수 설정이 어렵네요

**A**: `.env` 파일을 사용할 수 있습니다:

```bash
# .env 파일 생성
GCP_PROJECT_ID=ewha-chain-17
GEMINI_API_KEY=your-api-key
```

Python에서 사용:

```python
from dotenv import load_dotenv
load_dotenv()
```

---

## BigQuery 관련

### Q: 쿼리가 너무 느려요

**A**: 다음 방법을 시도해보세요:

1. **날짜 범위 축소**
   ```sql
   -- 30일 → 7일로 축소
   WHERE block_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
   ```

2. **LIMIT 사용**
   ```sql
   LIMIT 100
   ```

3. **샘플링 사용**
   ```sql
   FROM `table` TABLESAMPLE SYSTEM (1 PERCENT)
   ```

4. **필요한 컬럼만 SELECT**
   ```sql
   -- ❌ 나쁜 예
   SELECT * FROM ...
   
   -- ✅ 좋은 예
   SELECT column1, column2 FROM ...
   ```

### Q: "권한이 없습니다" 오류가 나요

**A**: 다음을 확인하세요:

1. BigQuery API가 활성화되었는지 확인
   - "API 및 서비스" → "라이브러리" → "BigQuery API" 활성화

2. 프로젝트가 올바르게 선택되었는지 확인
   - 상단 프로젝트 선택 드롭다운 확인

3. Public Datasets 접근 권한 확인
   - `bigquery-public-data` 프로젝트는 모든 사용자가 접근 가능합니다

### Q: 쿼리 결과가 비어있어요

**A**: 다음을 확인하세요:

1. **WHERE 절 필터 확인**
   ```sql
   -- 날짜 범위가 너무 좁은지 확인
   WHERE block_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
   ```

2. **NULL 값 처리**
   ```sql
   -- NULL 값 제외
   WHERE column IS NOT NULL
   ```

3. **테이블 이름 확인** (Solana는 테이블명이 대문자로 시작합니다!)
   ```sql
   -- Ethereum (소문자)
   `bigquery-public-data.crypto_ethereum.transactions`
   -- Solana (대문자 T, B 주의)
   `bigquery-public-data.crypto_solana_mainnet_us.Transactions`
   `bigquery-public-data.crypto_solana_mainnet_us.Blocks`
   ```

### Q: 쿼리 결과를 어떻게 저장하나요?

**A**: 여러 방법이 있습니다:

1. **BigQuery 콘솔에서 다운로드**
   - 쿼리 결과 테이블에서 "결과 다운로드" → "CSV로 다운로드"

2. **스크립트 사용**
   ```bash
   python scripts/run_query.py my_query.sql --output results.csv
   ```

3. **Python 코드로 저장**
   ```python
   from google.cloud import bigquery
   import pandas as pd
   
   client = bigquery.Client()
   results = client.query("SELECT ...").result()
   df = results.to_dataframe()
   df.to_csv('results.csv', index=False)
   ```

### Q: 쿼리를 저장하고 재사용할 수 있나요?

**A**: 네, 두 가지 방법이 있습니다:

1. **저장된 쿼리**
   - BigQuery 콘솔에서 "저장" 버튼 클릭
   - 나중에 "저장된 쿼리"에서 재사용

2. **뷰 생성**
   ```sql
   CREATE OR REPLACE VIEW `project.dataset.view_name` AS
   SELECT ...
   ```

---

## Gemini API 관련

### Q: Gemini API 키를 어떻게 발급받나요?

**A**: 다음 단계를 따르세요:

1. [Google AI Studio](https://makersuite.google.com/app/apikey) 접속
2. Google 계정으로 로그인
3. "API 키 만들기" 클릭
4. API 키 복사 및 안전하게 보관

### Q: API 키를 어디에 저장해야 하나요?

**A**: 환경 변수로 저장하는 것을 권장합니다:

```bash
# .bashrc 또는 .zshrc에 추가
export GEMINI_API_KEY="your-api-key"
```

또는 `.env` 파일 사용 (gitignore에 추가 필수).

### Q: "Rate limit exceeded" 오류가 나요

**A**: Gemini API는 분당 60 요청 제한이 있습니다:

1. **요청 간격 늘리기**
   ```python
   import time
   time.sleep(1)  # 1초 대기
   ```

2. **배치 처리**
   - 여러 요약을 한 번에 생성

3. **재시도 로직 추가**
   ```python
   import time
   
   def generate_with_retry(prompt, max_retries=3):
       for i in range(max_retries):
           try:
               return model.generate_content(prompt)
           except Exception as e:
               if "rate limit" in str(e).lower():
                   time.sleep(60)
                   continue
               raise
   ```

### Q: Gemini 응답이 너무 느려요

**A**: 다음을 시도해보세요:

1. **프롬프트 길이 줄이기**
   - 필요한 정보만 포함

2. **쿼리 결과 전처리**
   - BigQuery에서 집계 후 전달

3. **스트리밍 사용** (선택)
   ```python
   response = model.generate_content(prompt, stream=True)
   for chunk in response:
       print(chunk.text, end='')
   ```

---

## 쿼리 작성

### Q: SQL을 잘 모르는데 괜찮나요?

**A**: 템플릿 쿼리를 제공하니 주석을 읽고 이해하는 것부터 시작하세요. 막히면 팀 커뮤니케이션 채널에 질문해주세요.

**학습 순서**:
1. `templates/sql/01_basic_exploration.sql` - 기본 문법
2. `templates/sql/02_aggregation.sql` - 집계 함수
3. `templates/sql/03_join.sql` - 테이블 결합

### Q: 템플릿 쿼리를 그대로 사용해도 되나요?

**A**: 학습용으로는 괜찮지만, 최종 산출물에는 본인만의 쿼리를 작성해야 합니다. 템플릿을 참고하여 수정하세요.

### Q: Ethereum과 Solana 쿼리 차이점이 뭔가요?

**A**: 주요 차이점:

| 항목 | Ethereum | Solana |
|------|----------|--------|
| 트랜잭션 구조 | 단순 (from/to/value) | 복잡 (accounts, log_messages 등) |
| 가스비 | 가변 (gas_price * receipt_gas_used) | 고정 (fee) |
| 실패 표시 | receipt_status (0/1) | status ('Success' 또는 에러), err 컬럼 |
| 데이터 시작 | 2015년 7월 | 2020년 3월 |
| 데이터 종료 | 실시간 업데이트 중 | **2025년 3월 31일 (중단)** |
| 데이터셋 이름 | `crypto_ethereum` | `crypto_solana_mainnet_us` |

### Q: Solana 데이터가 최신이 아닌 것 같아요

**A**: Solana BigQuery Public Dataset(`crypto_solana_mainnet_us`)는 **2025년 3월 31일 이후 업데이트가 중단**되었습니다. Google Blockchain Analytics에서도 Solana는 지원하지 않습니다.

따라서 본 프로그램에서는:
- **Ethereum**: `CURRENT_TIMESTAMP()` 기반 실시간 분석
- **Solana**: 고정 날짜 범위(예: `2025-03-01` ~ `2025-03-31`) 기반 과거 분석

템플릿 쿼리에는 이미 고정 날짜가 적용되어 있으므로 그대로 실행하면 됩니다. 개별 쿼리 작성 시에도 Solana는 2025년 3월 이전 기간을 사용하세요.

### Q: JOIN이 어려워요

**A**: 다음 순서로 학습하세요:

1. **INNER JOIN** (가장 일반적)
   ```sql
   SELECT * FROM table1
   INNER JOIN table2 ON table1.id = table2.id
   ```

2. **LEFT JOIN** (왼쪽 테이블 기준)
   ```sql
   SELECT * FROM table1
   LEFT JOIN table2 ON table1.id = table2.id
   ```

3. **실제 예시**: `templates/sql/03_join.sql` 참고

---

## 대시보드 관련

### Q: Looker Studio가 무료인가요?

**A**: 네, Looker Studio는 무료입니다. Google 계정만 있으면 사용할 수 있습니다.

### Q: Looker Studio 대신 Next.js를 사용할 수 있나요?

**A**: 네, Extension 트랙 A를 선택하면 Next.js로 커스텀 대시보드를 만들 수 있습니다.

### Q: 대시보드를 공유하려면?

**A**: Looker Studio에서:

1. "공유" 버튼 클릭
2. "링크가 있는 모든 사용자" 선택
3. 링크 복사 및 공유

### Q: 대시보드가 너무 느려요

**A**: 다음을 시도해보세요:

1. **데이터 범위 축소**
   - 날짜 필터 사용

2. **집계 쿼리 사용**
   - BigQuery에서 집계 후 연결

3. **캐시 활용**
   - 자동 새로고침 간격 설정

---

## 비용 관련

### Q: BigQuery 비용이 걱정돼요

**A**: Public Datasets는 무료입니다. 쿼리 처리 비용만 발생하지만:

1. **작은 범위로 테스트**
   - 날짜 범위 제한
   - LIMIT 사용

2. **Dry Run으로 비용 확인**
   ```bash
   python scripts/run_query.py my_query.sql --dry-run
   ```

3. **샘플링 사용**
   ```sql
   TABLESAMPLE SYSTEM (1 PERCENT)
   ```

### Q: 예상 비용이 얼마나 드나요?

**A**: 일반적인 쿼리 비용:

- 작은 쿼리 (1-10MB): $0.000005 - $0.00005
- 중간 쿼리 (10-100MB): $0.00005 - $0.0005
- 큰 쿼리 (100MB-1GB): $0.0005 - $0.005

**참고**: 무료 체험 크레딧 $300이면 수만 건의 쿼리를 실행할 수 있습니다.

### Q: 비용을 모니터링하려면?

**A**: GCP 콘솔에서:

1. "청구" 메뉴 선택
2. BigQuery 사용량 확인
3. 일일 예산 알림 설정 (권장: $1/일)

---

## 일정 및 산출물

### Q: W1에서 완성해야 할 것은?

**A**: 다음을 완료하세요:

- [ ] GCP 계정 및 BigQuery 설정
- [ ] 템플릿 쿼리 3개 이상 실행
- [ ] 데이터셋 스키마 이해
- [ ] 쿼리 초안 3개 이상 작성
- [ ] 개별 지표 아이디어 제출

### Q: 쿼리를 몇 개 작성해야 하나요?

**A**: 
- **W1**: 쿼리 초안 약 10개 (학습용)
- **W2**: 핵심 지표 3~4개 확정
- **최종**: BigQuery SQL 쿼리 세트 10~15개

### Q: Demo Video는 어떻게 만들나요?

**A**: 다음 순서로 녹화하세요:

1. **문제 정의** (30초)
   - 분석하고 싶은 지표 소개

2. **대시보드 시연** (1분)
   - 주요 차트 설명
   - 필터 사용 데모

3. **Gemini 요약 생성** (30초)
   - 요약 생성 과정 보여주기

4. **결론/인사이트** (30초)
   - 주요 발견 사항 요약

**도구**: OBS Studio, Loom, 또는 화면 녹화 기능 사용

### Q: 리포트는 어떻게 작성하나요?

**A**: 다음 구조를 권장합니다:

1. **요약** (1-2문단)
   - 분석 목적 및 주요 발견 사항

2. **핵심 지표** (3-4개)
   - 각 지표별 설명 및 인사이트

3. **비교 분석** (Ethereum vs Solana)
   - 처리량, 수수료, 활성도 비교

4. **결론**
   - 기관 투자자 관점에서의 시사점

---

## 기술적 문제 해결

### Q: Python 스크립트가 실행되지 않아요

**A**: 다음을 확인하세요:

1. **패키지 설치 확인**
   ```bash
   pip install -r requirements.txt
   ```

2. **Python 버전 확인**
   ```bash
   python3 --version  # 3.8 이상 필요
   ```

3. **환경 변수 확인**
   ```bash
   echo $GCP_PROJECT_ID
   echo $GEMINI_API_KEY
   ```

### Q: "ModuleNotFoundError" 오류가 나요

**A**: 필요한 패키지를 설치하세요:

```bash
pip install google-cloud-bigquery google-generativeai
```

또는:

```bash
pip install -r requirements.txt
```

### Q: Git 충돌이 발생했어요

**A**: 다음 순서로 해결하세요:

1. **최신 코드 가져오기**
   ```bash
   git pull origin main
   ```

2. **충돌 해결**
   - 충돌 파일 수정
   - `git add .`
   - `git commit`

3. **도움이 필요하면**: 팀장에게 연락

### Q: 레포지토리에 커밋하는 방법이 궁금해요

**A**: [CONTRIBUTING.md](../CONTRIBUTING.md) 문서를 참고하세요.

**기본 흐름**:
1. 브랜치 생성: `git checkout -b members/[본인이름]`
2. 파일 수정
3. 커밋: `git commit -m "[본인이름] 작업 내용"`
4. 푸시: `git push origin members/[본인이름]`
5. PR 생성

---

## 추가 도움

### 질문하기

막히는 부분이 있으면:

1. **팀 커뮤니케이션 채널**에 질문
2. **GitHub Issues**에 버그 리포트
3. **팀장에게 직접 연락** (긴급한 경우)

### 질문할 때 포함할 내용

- 어떤 작업을 하려고 했는지
- 어떤 오류 메시지가 나왔는지
- 어떤 방법을 시도했는지
- 스크린샷 또는 코드 (가능한 경우)

### 유용한 링크

- [BigQuery 문서](https://cloud.google.com/bigquery/docs)
- [Gemini API 문서](https://ai.google.dev/docs)
- [Looker Studio 가이드](https://support.google.com/looker-studio)
- [프로그램 메인 README](../README.md)

---

**마지막 업데이트**: 2026-02-15
