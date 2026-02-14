# 기여 가이드

이화체인 17기 개발 프로그램에 참여하는 모든 분들을 위한 가이드입니다.

## 작업 흐름

### 1. 레포지토리 포크 및 클론

```bash
# 레포지토리 포크 후
git clone https://github.com/[본인계정]/ewha-chain-17-core.git
cd ewha-chain-17-core
```

### 2. 개인 브랜치 생성

```bash
git checkout -b members/[본인이름]
```

### 3. 작업 진행

- `members/[본인이름]/` 폴더에서 작업
- 쿼리 파일, 코드, 문서 등 모든 작업물을 이 폴더에 저장

### 4. 커밋 규칙

커밋 메시지는 다음 형식을 따릅니다:

```
[타입] 간단한 설명

- 타입: query, dashboard, gemini, docs, fix 등
- 예: [query] Add Solana active addresses analysis
```

### 5. Pull Request 생성

- 작업이 완료되면 `main` 브랜치로 PR 생성
- PR 제목: `[본인이름] W1: BigQuery 쿼리 초안`
- PR 설명에 다음 포함:
  - 작업 내용 요약
  - 실행 방법 (필요시)
  - 스크린샷/결과 링크

### 6. 코드 리뷰

- 팀장 및 다른 팀원들의 리뷰를 받고 피드백 반영
- 리뷰어가 승인하면 머지

## 파일 명명 규칙

### SQL 쿼리
- 형식: `[번호]_[기능명].sql`
- 예: `01_tx_volume.sql`, `02_active_addresses.sql`

### Python 스크립트
- 형식: `[기능명].py`
- 예: `gemini_summary.py`, `query_executor.py`

### 문서
- 형식: `[제목].md`
- 예: `README.md`, `dashboard_setup.md`

## 코드 스타일

### SQL
- 키워드는 대문자 (`SELECT`, `FROM`, `WHERE`)
- 들여쓰기 2칸
- 주석은 `--` 사용

```sql
-- 거래량 추이 분석
SELECT
  DATE(block_timestamp) AS date,
  COUNT(*) AS tx_count
FROM
  `bigquery-public-data.crypto_ethereum.transactions`
WHERE
  block_timestamp >= TIMESTAMP('2025-01-01')
GROUP BY
  date
ORDER BY
  date DESC
```

### Python
- PEP 8 스타일 가이드 준수
- 함수/클래스에 docstring 작성

```python
def generate_summary(query_result: dict) -> str:
    """
    BigQuery 결과를 기반으로 Gemini로 요약 생성
    
    Args:
        query_result: BigQuery 쿼리 결과 딕셔너리
        
    Returns:
        생성된 요약 텍스트
    """
    # 구현
    pass
```

## 질문하기

막히는 부분이 있으면:

1. **슬랙 #core-questions 채널**에 질문
2. GitHub Issues에 버그 리포트
3. 팀장에게 직접 연락 (긴급한 경우)

## 템플릿 수정 제안

템플릿에 개선 사항이 있으면:

1. `templates/` 폴더의 해당 파일 수정
2. PR 생성 시 `[TEMPLATE]` 태그 추가
3. 변경 이유와 개선 효과 설명

## 최종 산출물 제출

W4 마지막 주에 다음을 `deliverables/` 폴더에 제출:

- [ ] Demo Video (YouTube 링크 또는 파일)
- [ ] 리포트 PDF
- [ ] 실행 가이드 문서
- [ ] 대시보드 링크
