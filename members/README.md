# 개별 작업 공간

이 폴더는 각 팀원의 개별 작업 공간입니다.

## 폴더 생성 방법

1. 본인 이름으로 폴더 생성
   ```bash
   mkdir members/[본인이름]
   ```

2. README.md 파일 생성
   ```bash
   cd members/[본인이름]
   touch README.md
   ```

3. README.md에 다음 내용 작성:

```markdown
# [본인이름] 작업 공간

## 분석 목표
- [ ] 목표 1
- [ ] 목표 2

## 쿼리 목록
- `queries/01_my_query.sql`: [설명]

## 대시보드
- Looker Studio 링크: [링크]

## Gemini 요약
- [요약 내용 또는 파일 링크]

## 최종 산출물
- Demo Video: [링크]
- 리포트: [파일 경로]
```

## 권장 폴더 구조

```
members/[본인이름]/
├── README.md
├── queries/
│   ├── 01_tx_volume.sql
│   ├── 02_active_addresses.sql
│   └── custom_queries.sql
├── dashboard/
│   └── looker_studio_link.txt
├── gemini/
│   └── summaries/
│       └── weekly_summary_2025-03-15.txt
└── deliverables/
    ├── demo_video.mp4
    └── report.pdf
```

## 작업 규칙

1. **커밋 메시지**: `[본인이름] 작업 내용` 형식 사용
2. **PR 생성**: 주차별로 PR 생성 (예: `[본인이름] W1: 쿼리 초안`)
3. **코드 리뷰**: 다른 팀원들의 피드백 받기

## 질문

막히는 부분이 있으면 팀 커뮤니케이션 채널에 질문해주세요!
