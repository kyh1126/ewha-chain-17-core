# Google Cloud X EWHA-CHAIN 17기 개발 프로그램

> **기간**: 3월 + 5월 (총 8주)  
> **대상**: 이화체인 개발팀(블록체인 엔지니어 트랙)  
> **형태**: Core(전원 공통, **3월** W1–W4) + Extension(선택 1, **5월** W5–W8)

## 📋 목차

- [프로그램 개요](#프로그램-개요)
- [Core 목표](#core-목표)
- [레포지토리 구조](#레포지토리-구조)
- [온보딩 가이드](#온보딩-가이드)
- [주차별 진행 사항](#주차별-진행-사항)
- [산출물 체크리스트](#산출물-체크리스트)
- [자주 묻는 질문](#자주-묻는-질문)

## 프로그램 개요

학부생 수준에서 구현 가능한 범위로 **GCP 기반 Web3 실증 포트폴리오**를 구축합니다.

### 핵심 목표
1. BigQuery로 온체인 데이터(Ethereum, Solana) 분석·시각화
2. Gemini로 인사이트 요약 자동 생성
3. Demo Video + 가이드/리포트 패키징

### ⚠️ Solana 데이터 안내

Solana BigQuery Public Dataset(`crypto_solana_mainnet_us`)는 **2025년 3월 31일 이후 업데이트가 중단**되었습니다.

| 체인 | 데이터셋 | 상태 | 분석 방식 |
|------|----------|------|-----------|
| Ethereum | `crypto_ethereum` | 실시간 업데이트 | `CURRENT_TIMESTAMP()` 기반 |
| Solana | `crypto_solana_mainnet_us` | 2025-03-31 중단 | 고정 기간(2025년 3월) 기반 |

- Solana 과거 데이터는 정상 조회 가능하며, 체인 비교·학습 목적으로 충분합니다.
- 템플릿 쿼리에는 이미 고정 날짜 범위가 적용되어 있습니다.

## Core 목표

**BigQuery 기반 온체인 리서치: 표준 대시보드 + Gemini 인사이트 생성**

- BigQuery Blockchain Datasets 활용
- 재현 가능한 표준 리서치 대시보드 구축
- "기관 관점에서 Solana의 처리량·패턴을 데이터로 설명" 가능한 레퍼런스 확보

## 레포지토리 구조

```
.
├── README.md                    # 이 파일
├── CONTRIBUTING.md              # 기여 가이드
├── .gitignore                   # Git 제외 파일
├── requirements.txt             # Python 패키지 목록
│
├── templates/                   # 팀장 제공 템플릿
│   ├── queries/                 # SQL 쿼리 템플릿 (분석용)
│   │   ├── 01_tx_volume.sql
│   │   ├── 02_active_addresses.sql
│   │   ├── 03_fee_gas.sql
│   │   └── 04_failed_transactions.sql
│   ├── sql/                     # SQL 학습용 샘플 쿼리
│   │   ├── 01_basic_exploration.sql
│   │   ├── 02_aggregation.sql
│   │   └── 03_join.sql
│   ├── gemini/                  # Gemini API 템플릿
│   │   ├── prompt_template.py
│   │   └── example_usage.py
│   └── dashboard/               # 대시보드 가이드
│       └── looker_studio_guide.md
│
├── scripts/                     # 자동화 스크립트 (선택)
│   ├── README.md                # 스크립트 사용 가이드
│   ├── run_query.py             # BigQuery 쿼리 실행 자동화
│   ├── run_query.sh
│   ├── summarize_with_gemini.py # Gemini 요약 자동화
│   └── summarize_with_gemini.sh
│
├── members/                     # 개별 작업 공간
│   ├── README.md                # 개인 폴더 생성 가이드
│   ├── yoonhee/                 # 예시 (각자 생성)
│   │   ├── queries/
│   │   ├── dashboard/
│   │   └── README.md
│   ├── jihye/
│   └── [이름]/
│
├── docs/                        # 문서
│   ├── W1_onboarding.md         # W1 종합 온보딩 가이드
│   ├── W2_core_queries.md       # W2 핵심 쿼리 + Looker Studio
│   ├── W3_gemini_integration.md # W3 Gemini API 연동
│   ├── W4_portfolio_final.md    # W4 포트폴리오 완성
│   ├── FAQ.md                   # 자주 묻는 질문
│   ├── onboarding/              # 온보딩 가이드
│   │   ├── 01_bigquery_setup.md
│   │   ├── 02_dataset_schema.md
│   │   └── 03_gemini_api.md
│   ├── guides/                  # 실행 가이드
│   │   ├── query_execution.md
│   │   └── dashboard_creation.md
│   └── resources/               # 참고 자료
│       └── bigquery_datasets.md
│
└── deliverables/                # 최종 산출물 (W4 이후)
    ├── README.md                # 산출물 제출 가이드
    ├── demo_videos/
    ├── reports/
    └── guides/
```

## 온보딩 가이드

### 빠른 시작

**주차별 가이드:**
- [W1 온보딩 가이드](./docs/W1_onboarding.md) - W1 전체 가이드
- [W2 핵심 쿼리 가이드](./docs/W2_core_queries.md) - 표준 지표 쿼리 + Looker Studio
- [W3 Gemini 연동 가이드](./docs/W3_gemini_integration.md) - Gemini API + 프롬프트 커스터마이징
- [W4 포트폴리오 완성 가이드](./docs/W4_portfolio_final.md) - 대시보드·Demo Video·리포트 마무리
- [FAQ](./docs/FAQ.md) - 자주 묻는 질문

### 단계별 가이드

#### 1단계: 환경 설정

1. **GCP 계정 생성**
   - [Google Cloud Console](https://console.cloud.google.com/) 접속
   - 프로젝트 생성 (프로젝트 ID: `ewha-chain-17-[본인이름]` 권장)
   - BigQuery API 활성화
   - 자세한 내용: [BigQuery 설정 가이드](./docs/onboarding/01_bigquery_setup.md)

2. **BigQuery 접근**
   - BigQuery 콘솔 열기
   - Public Datasets 확인: `bigquery-public-data.crypto_ethereum`, `bigquery-public-data.crypto_solana_mainnet_us`

3. **개인 폴더 생성**
   ```bash
   mkdir members/[본인이름]
   cd members/[본인이름]
   ```
   - 자세한 내용: [members/README.md](./members/README.md)

#### 2단계: 첫 쿼리 실행

**학습용 샘플 쿼리** (순서대로 실행 권장):
1. `templates/sql/01_basic_exploration.sql` - 기본 문법 학습
2. `templates/sql/02_aggregation.sql` - 집계 함수 학습
3. `templates/sql/03_join.sql` - 테이블 결합 학습

**분석용 템플릿 쿼리**:
- `templates/queries/01_tx_volume.sql` - 거래량 추이 분석
- `templates/queries/02_active_addresses.sql` - 활성 주소/컨트랙트 Top N
- `templates/queries/03_fee_gas.sql` - 수수료/가스비 분석
- `templates/queries/04_failed_transactions.sql` - 실패 트랜잭션 분석

각 쿼리의 주석을 읽고, "왜 이렇게 썼는지" 이해한 후 수정해보세요.

#### 3단계: 자동화 스크립트 사용 (선택)

쿼리 실행과 요약 생성을 자동화하려면:
- [스크립트 가이드](./scripts/README.md) 참고
- `python scripts/run_query.py` - 쿼리 실행 자동화
- `python scripts/summarize_with_gemini.py` - Gemini 요약 자동화

## 주차별 진행 사항

### W1: 목표/지표 확정 + 데이터셋 스키마 파악
- [W1 가이드](./docs/W1_onboarding.md) 참고
- [ ] GCP 계정 셋업 완료
- [ ] BigQuery 샘플 쿼리 실행 성공
- [ ] 데이터셋 스키마 문서 읽기
- [ ] "내가 분석하고 싶은 지표 1개" 아이디어 제출

### W2: 핵심 지표 확정 + SQL 안정화
- [W2 가이드](./docs/W2_core_queries.md) 참고
- [ ] 표준 지표 쿼리 3~4개 작성 완료
- [ ] Looker Studio 연동 시작
- [ ] 개별 지표 쿼리 1개 이상 작성

### W3: 대시보드 완성 + Gemini 연동
- [W3 가이드](./docs/W3_gemini_integration.md) 참고
- [ ] Looker Studio 대시보드 1차 완성
- [ ] Gemini API 연동 성공
- [ ] 프롬프트 커스터마이징 완료

### W4: 산출물 마무리
- [W4 가이드](./docs/W4_portfolio_final.md) 참고
- [ ] 최종 대시보드 완성
- [ ] Demo Video 제작 (2~3분)
- [ ] 리포트 작성 (1~2p)
- [ ] Extension 트랙 선택 확정

## 산출물 체크리스트

### 필수 산출물
- [ ] BigQuery SQL 쿼리 세트 (10~15개)
- [ ] 표준 대시보드 (Looker Studio 링크 또는 웹 URL)
- [ ] Demo Video (2~3분)
- [ ] 요약 리포트 (1~2p)
- [ ] 실행 가이드 (온보딩 문서)

### 개별 산출물 (members/[이름]/)
- [ ] 개별 쿼리 파일들
- [ ] 대시보드 스크린샷/링크
- [ ] Gemini 프롬프트 코드
- [ ] README.md (본인 작업 설명)

## 자주 묻는 질문

자세한 FAQ는 [FAQ 문서](./docs/FAQ.md)를 참고하세요.

### Q1. BigQuery 비용이 걱정돼요
**A**: Public Datasets는 무료입니다. 쿼리 비용은 처리한 데이터 양에 따라 과금되지만, 샘플링과 기간 제한으로 비용을 관리할 수 있습니다. Dry Run으로 비용을 미리 확인할 수 있습니다. 자세한 내용은 [쿼리 실행 가이드](./docs/guides/query_execution.md) 참고.

### Q2. SQL을 잘 모르는데 괜찮나요?
**A**: 학습용 샘플 쿼리(`templates/sql/`)를 제공하니, 주석을 읽고 이해하는 것부터 시작하세요. 막히면 팀 커뮤니케이션 채널에 질문해주세요.

### Q3. 개별 지표는 뭘 해야 할까요?
**A**: 본인이 관심 있는 블록체인 현상이나 질문을 데이터로 답하는 것이 좋습니다. 예: "Solana에서 가장 활발한 프로그램은?", "이더리움 가스비 급등 시점 분석" 등. [W1 온보딩 가이드](./docs/W1_onboarding.md) 참고.

### Q4. Demo Video는 어떻게 만들까요?
**A**: 화면 녹화 도구(OBS, Loom 등)를 사용해 다음 순서로 녹화하세요:
1. 문제 정의 (30초)
2. 대시보드 시연 (1분)
3. Gemini 요약 생성 (30초)
4. 결론/인사이트 (30초)

### Q5. 스크립트는 필수인가요?
**A**: 아니요, 선택 사항입니다. BigQuery 콘솔에서 직접 쿼리를 실행해도 됩니다. 스크립트는 반복 작업을 자동화하고 싶을 때 사용하세요. [스크립트 가이드](./scripts/README.md) 참고.

## 커뮤니케이션

- **질문**: 팀 커뮤니케이션 채널 (추후 안내)
- **코드 리뷰**: GitHub Pull Request
- **일일 체크인**: 온라인 미팅 (선택)

## 라이선스

이 레포지토리는 이화체인 17기 개발 프로그램 전용입니다.
