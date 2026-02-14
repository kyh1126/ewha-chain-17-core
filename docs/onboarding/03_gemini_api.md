# Gemini API 설정 가이드

## 1. API 키 발급

### Google AI Studio 접속

1. [Google AI Studio](https://makersuite.google.com/app/apikey) 접속
2. Google 계정으로 로그인
3. "API 키 만들기" 클릭
4. API 키 복사 및 안전하게 보관

### API 키 보안

⚠️ **주의**: API 키를 절대 공개 레포지토리에 커밋하지 마세요!

```bash
# .env 파일에 저장 (gitignore에 추가)
GEMINI_API_KEY=your-api-key-here
```

## 2. Python 환경 설정

### 필요한 패키지 설치

```bash
pip install google-generativeai
```

### 환경 변수 설정

```bash
# .env 파일
export GEMINI_API_KEY="your-api-key-here"
```

또는 Python 코드에서 직접 설정:

```python
import os
os.environ["GEMINI_API_KEY"] = "your-api-key-here"
```

## 3. 기본 사용법

### 간단한 예제

```python
import google.generativeai as genai

# API 키 설정
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# 모델 선택
model = genai.GenerativeModel('gemini-2.0-flash')

# 프롬프트 생성
prompt = "온체인 데이터 분석 결과를 요약해주세요."

# 응답 생성
response = model.generate_content(prompt)
print(response.text)
```

## 4. BigQuery 결과와 연동

### 예제: 쿼리 결과 요약

```python
from google.cloud import bigquery
import google.generativeai as genai

# BigQuery 클라이언트
client = bigquery.Client()

# 쿼리 실행
query = """
SELECT
  DATE(block_timestamp) AS date,
  COUNT(*) AS tx_count
FROM
  `bigquery-public-data.crypto_ethereum.transactions`
WHERE
  block_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
GROUP BY date
ORDER BY date DESC
"""

results = client.query(query).result()

# 결과를 텍스트로 변환
data_summary = "\n".join([
    f"{row.date}: {row.tx_count} transactions"
    for row in results
])

# Gemini로 요약 생성
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-2.0-flash')

prompt = f"""
다음 온체인 데이터를 분석하여 주간 요약을 작성해주세요:

{data_summary}

요약은 3-5문장으로 작성하고, 주요 변화와 패턴을 언급해주세요.
"""

response = model.generate_content(prompt)
print(response.text)
```

## 5. 프롬프트 템플릿 활용

템플릿 폴더의 `prompt_template.py` 파일을 참고하세요:

- `generate_weekly_summary()`: 주간 요약 생성
- `generate_comparison_insight()`: 체인 비교 분석
- `detect_anomalies()`: 이상 징후 탐지

## 6. 비용 관리

### 무료 할당량

- Gemini 2.0 Flash: 분당 60 요청
- 일일 무료 할당량 제공

### 비용 절감 팁

1. **배치 처리**: 여러 요약을 한 번에 생성
2. **캐싱**: 동일한 데이터는 캐시 활용
3. **프롬프트 최적화**: 불필요한 텍스트 제거

## 7. 에러 처리

### 일반적인 에러

```python
try:
    response = model.generate_content(prompt)
except Exception as e:
    print(f"에러 발생: {e}")
    # 재시도 로직 또는 기본값 반환
```

### Rate Limit 처리

```python
import time

def generate_with_retry(prompt, max_retries=3):
    for i in range(max_retries):
        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            if "rate limit" in str(e).lower():
                time.sleep(60)  # 1분 대기
                continue
            raise
```

## 8. 고급 활용

### 스트리밍 응답

```python
response = model.generate_content(
    prompt,
    stream=True
)

for chunk in response:
    print(chunk.text, end='')
```

### 시스템 프롬프트 설정

```python
model = genai.GenerativeModel(
    'gemini-2.0-flash',
    system_instruction="당신은 블록체인 데이터 분석 전문가입니다."
)
```

## 9. 다음 단계

- [템플릿 코드 실행](../../templates/gemini/example_usage.py)
- [대시보드에 통합](../guides/dashboard_creation.md)
- [최종 산출물 준비](../../deliverables/README.md)

## 문제 해결

### "API 키가 유효하지 않습니다"

- API 키가 올바르게 설정되었는지 확인
- 환경 변수가 제대로 로드되었는지 확인

### "Rate limit exceeded"

- 요청 간격을 늘리기
- 배치 처리로 변경

### 응답이 느림

- 프롬프트 길이 줄이기
- 필요한 정보만 포함
