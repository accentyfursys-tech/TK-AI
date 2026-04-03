---
description: 세션 마무리 - 대화 기록 저장, 데일리노트 업데이트, GitHub 커밋 푸시
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

세션을 마무리합니다. 오늘 대화 내용을 기록하고 저장합니다.

**수행할 작업:**

## 1. 세션 기록 수집

지금까지 이 대화에서 수행한 작업을 요약합니다:
- 어떤 주제/프로젝트를 다뤘는지
- 어떤 파일을 생성/수정했는지
- 어떤 문제를 해결했는지
- 주요 결정사항 및 인사이트

## 2. 세션 로그 파일 저장

다음 경로에 세션 기록 저장:
- 파일 경로: `./40-personal/42-sessions/YYYY-MM-DD_HH-MM_session.md`
- 오늘 날짜와 현재 시각 확인 후 파일명 결정
- 이미 같은 날짜 파일이 있으면 새 번호로 구분 (예: `2026-04-03_01_session.md`, `2026-04-03_02_session.md`)

**세션 파일 템플릿:**
```markdown
# 세션 로그 - {{date}}

> 시작: {{session_start_time}}  
> 종료: {{session_end_time}}  
> 주요 주제: {{main_topic}}

---

## 작업 요약

{{session_summary}}

## 생성/수정된 파일

{{changed_files}}

## 주요 결정사항

{{decisions}}

## 인사이트 & 배운 점

{{insights}}

## 다음 액션

{{next_actions}}

---

#session-log #{{date_tag}}
```

## 3. 데일리노트 업데이트

- `./40-personal/41-daily/YYYY-MM-DD.md` 파일 읽기
- 없으면 `/daily-note` 로직대로 생성
- **"오늘의 업무 > 완료"** 섹션에 이번 세션 주요 작업 추가
- **"Daily Reflection > 잘한 점"** 에 성과 추가
- **"오늘 배운 것"** 에 인사이트 추가
- **"내일 우선순위"** 에 next actions 추가

## 4. GitHub 커밋 & 푸시

```bash
# 변경된 파일 스테이징
git add -A

# 커밋 메시지 형식: "docs: YYYY-MM-DD 세션 기록 및 데일리노트 저장"
git commit -m "docs: $(date +%Y-%m-%d) 세션 기록 및 데일리노트 저장"

# 푸시
git push
```

커밋 후 성공 메시지와 함께 세션 마무리 인사를 건넵니다.

---

**마무리 멘트 예시:**
> "오늘도 수고하셨습니다! 세션 기록이 저장되었고, GitHub에 푸시 완료했습니다. 내일 또 시작할 때 `/daily-note` 로 이어가세요."