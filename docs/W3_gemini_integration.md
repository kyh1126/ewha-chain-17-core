# W3 Gemini API 연동 가이드

**기간**: 3월 3주  
**목표**: 대시보드 1차 완성 + Gemini API 연동(주간 요약/이상징후 코멘트) + 프롬프트 커스터마이징

## 📋 W3 체크리스트

- [ ] Gemini API 키 발급 완료
- [ ] Python 샘플 코드 실행 성공
- [ ] 프롬프트 템플릿 3개 이해 및 수정해 보기
- [ ] 각자 대시보드 데이터로 Gemini 요약 생성
- [ ] 본인 지표에 맞게 프롬프트 커스터마이징
- [ ] 결과물 스크린샷 + 코드 제출

## 1. 팀장 준비물 (세션 전 확인)

- Gemini API 키 발급 가이드
- Python 샘플 코드 (템플릿 기반)
- 프롬프트 템플릿 3개: 주간 요약, 이상징후 후보, 비교 결론 3줄

**라이브 코딩 세션(1.5시간)** 에서 API 키 발급 → 샘플 실행 → 프롬프트 수정까지 함께 진행합니다.

## 2. Gemini API 키 발급 (15분)

### 2.1 API 키 만들기

1. [Google AI Studio](https://makersuite.google.com/app/apikey) 접속
2. Google 계정으로 로그인
3. "API 키 만들기" 또는 "Create API key" 클릭
4. 프로젝트 선택 (또는 새 프로젝트 생성)
5. 생성된 API 키 복사

### 2.2 보안 설정

⚠️ **API 키를 공개 레포지토리에 커밋하지 마세요.**

```bash
# 프로젝트 루트에 .env 파일 생성 (이미 .gitignore에 포함되어 있음)
echo "GEMINI_API_KEY=your-api-key-here" > .env
```

Python에서 사용할 때:

```python
import os
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
```

또는 터미널에서:

```bash
export GEMINI_API_KEY="your-api-key-here"
```

자세한 내용: [Gemini API 설정 가이드](./onboarding/03_gemini_api.md)

**✅ 확인**: API 키 발급 완료, `.env`에 저장, `.gitignore`에 `.env` 포함 여부 확인

## 3. Python 환경 및 샘플 코드 실행 (30분)

### 3.1 Python 확인 및 패키지 설치

```bash
# Python 버전 확인 (3.8 이상 필요)
python3 --version

# 프로젝트 루트로 이동
cd /path/to/ewha-chain-17-core

# 패키지 설치
pip install -r requirements.txt
```

### 3.2 BigQuery 로컬 인증 설정

`example_usage.py`는 BigQuery에 쿼리를 보내므로 **로컬 인증**이 필요합니다.

```bash
# 1) gcloud CLI 설치 (아직 없다면)
#    https://cloud.google.com/sdk/docs/install 참고

# 2) 로그인
gcloud auth login

# 3) 애플리케이션 기본 인증 설정 (Python 스크립트에서 사용)
gcloud auth application-default login

# 4) GCP_PROJECT_ID 환경 변수 설정
export GCP_PROJECT_ID="ewha-chain-17-[본인이름]"
```

> **BigQuery 콘솔에서만 쿼리를 실행했다면** 이 단계가 처음일 수 있습니다. 꼭 진행하세요.

### 3.3 샘플 코드 실행

**방법 A** — BigQuery 연동 포함 (전체 파이프라인):

```bash
# GEMINI_API_KEY, GCP_PROJECT_ID 환경 변수가 설정된 상태에서
cd ewha-chain-17-core
python templates/gemini/example_usage.py
```

`example_usage.py`는 BigQuery에서 데이터를 가져온 뒤 Gemini로 요약을 생성합니다.

**방법 B** — Gemini만 테스트 (BigQuery 없이 간단 확인):

BigQuery 인증이 번거로우면, **CSV를 직접 로드**해서 Gemini만 테스트할 수도 있습니다:

```python
# simple_gemini_test.py (프로젝트 루트에서 실행)
import os, json
from dotenv import load_dotenv
load_dotenv()

import google.generativeai as genai
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-2.0-flash')

# BigQuery 콘솔에서 CSV로 내려받은 결과를 여기에 붙여넣기
sample_data = {
    "ethereum_daily_tx": [
        {"date": "2025-03-10", "tx_count": 1200000},
        {"date": "2025-03-11", "tx_count": 1150000},
    ]
}

prompt = f"""다음 온체인 데이터를 분석하여 주간 요약을 3-5문장으로 작성해주세요:
{json.dumps(sample_data, indent=2)}"""

response = model.generate_content(prompt)
print(response.text)
```

이 방법이면 `GCP_PROJECT_ID`와 `gcloud auth` 없이도 Gemini 연동을 먼저 확인할 수 있습니다.

**✅ 확인**: 방법 A 또는 B로 Gemini 요약 텍스트가 정상 출력되는지 확인

### 3.4 프롬프트 템플릿 참고

`templates/gemini/prompt_template.py` 파일에 3가지 함수가 준비되어 있습니다:
- `generate_weekly_summary()`: 주간 요약
- `generate_comparison_insight()`: 체인 비교
- `detect_anomalies()`: 이상 징후 후보

## 4. 프롬프트 템플릿 3개 이해 (라이브 세션)

### 4.1 제공되는 템플릿

| 용도 | 함수/템플릿 | 설명 |
|------|-------------|------|
| 주간 요약 | `generate_weekly_summary()` | 핵심 지표 3가지, 전주 대비 변화, 3-5문장 |
| 이상징후 후보 | `detect_anomalies()` | 주목할 만한 패턴·이상 징후 탐지 |
| 비교 결론 3줄 | `generate_comparison_insight()` | 체인 비교(예: Ethereum vs Solana) 결론 3줄 |

### 4.2 프롬프트 수정해 보기

- `prompt_template.py` 내 프롬프트 문자열을 복사해 본인 지표에 맞게 문구 수정
- 예: "거래량" 대신 "일별 활성 주소 수"를 강조하도록 지시 문 추가

**✅ 확인**: 세션 중 최소 1개 프롬프트를 수정해 보고 실행해 봄

## 5. 대시보드 데이터로 Gemini 요약 생성 (개별 숙제)

### 5.1 입력 데이터 준비

- W2에서 만든 대시보드(또는 쿼리)의 **결과 데이터**를 텍스트/CSV/딕셔너리 형태로 준비
- 예: 일별 tx_count, 활성 주소 수, 수수료 합계 등

### 5.2 요약 생성 절차

1. BigQuery 쿼리 결과를 Python으로 가져오기 (또는 CSV 로드)
2. `generate_weekly_summary()` 등에 맞는 형식으로 넘기기
3. Gemini 응답을 파일로 저장하거나 화면에 출력
4. (선택) 동일 데이터로 `detect_anomalies()`, `generate_comparison_insight()` 실행

### 5.3 프롬프트 커스터마이징

- 자신이 선택한 **개별 지표**에 맞게 프롬프트 문구 수정
- 예: "Solana 일별 TPS 유사 지표를 중심으로 요약해 주세요"

**✅ 확인**: 본인 대시보드 데이터로 요약 1개 이상 생성 성공

## 6. 결과물 제출 (개별 숙제)

다음을 제출하세요:

1. **결과물 스크린샷**  
   - Gemini가 생성한 요약 텍스트가 보이는 화면
2. **사용한 코드**  
   - `members/[본인이름]/` 아래에 Python 스크립트 또는 노트북 저장  
   - 예: `members/yoonhee/gemini_summary.py` 또는 `gemini_weekly.ipynb`

제출 방법: GitHub에 커밋 후 PR 생성 또는 팀 커뮤니케이션 채널에 링크 공유

**✅ 확인**: 스크린샷 + 코드가 `members/[본인이름]/` 에 있음

## 7. 자주 묻는 질문 (W3)

**Q: API 키 오류가 나요.**  
A: `.env` 경로가 스크립트 실행 위치 기준으로 맞는지 확인하세요. `python-dotenv`로 `load_dotenv()` 호출 시 프로젝트 루트에서 실행하거나, `load_dotenv(".env")`에 절대 경로를 넣어 보세요.

**Q: Rate limit exceeded.**  
A: 분당 60 요청 제한이 있습니다. 요청 간격을 두거나, 한 번에 여러 요약을 묶어서 하나의 프롬프트로 보내 보세요. [에러 처리 참고](./onboarding/03_gemini_api.md)

**Q: BigQuery 결과를 어떻게 Python으로 넘기나요?**  
A: `scripts/run_query.py` 또는 BigQuery 클라이언트로 쿼리 실행 후 결과를 리스트/딕셔너리로 변환해 `generate_weekly_summary()` 등에 넘기면 됩니다. [03_gemini_api.md](./onboarding/03_gemini_api.md)의 "BigQuery 결과와 연동" 참고.

**Q: 프롬프트를 한국어로 써도 되나요?**  
A: 네. 템플릿은 한국어로 작성되어 있으며, 한국어로 요약을 요청하면 됩니다.

## 8. W3 마무리 체크리스트

- [ ] Gemini API 키 발급 및 로컬 설정 완료
- [ ] 샘플 코드 및 프롬프트 템플릿 1개 이상 실행
- [ ] 대시보드 데이터로 요약 1개 이상 생성
- [ ] 프롬프트 커스터마이징 후 본인 지표 기준 요약 생성
- [ ] 결과물 스크린샷 + 코드를 `members/[본인이름]/` 에 제출
- [ ] (선택) Looker Studio 대시보드 1차 완성

## 9. 다음 주 (W4) 준비

W4에서는 다음을 진행합니다:

- 개별 포트폴리오 완성 (대시보드 최종, Demo Video, 리포트)
- 코드 리뷰(PR 기반)
- 최종 발표 리허설 및 피드백

W3에서 만든 요약 문구와 차트를 정리해 두면, W4 리포트와 Demo Video 스크립트에 그대로 활용할 수 있습니다.

## 10. 관련 문서

- [W2 핵심 쿼리 가이드](./W2_core_queries.md)
- [Gemini API 설정 가이드](./onboarding/03_gemini_api.md)
- [대시보드 생성 가이드](./guides/dashboard_creation.md)
- [쿼리 실행 가이드](./guides/query_execution.md)
- [FAQ](./FAQ.md)
