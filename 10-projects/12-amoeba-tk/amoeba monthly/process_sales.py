# -*- coding: utf-8 -*-
"""
상제품매출상세 처리 스크립트 (통합)
- transform_raw ~ transform_raw5 로직 통합
- 입력: 01. 상제품매출상세 (3월가).xlsx
- 출력: 01. 상제품매출상세 (3월가)_처리완료.xlsx

처리 내용:
1. 시트명 RAW로 변경
2. E열에 매출구분 삽입 (공란, 이후 분류)
3. 실적사업소 다음에 채널구분 삽입
4. 안분된채산조직에서 세부 열 추가 (괄호값 추출)
5. 안분된채산조직 괄호 제거
6. 채널구분 값 부여 (오프라인/온라인)
7. 안분된채산조직_계층 → 3열 세분화
8. 매출구분 값 부여 (일반/전시품/extra/판촉물)
"""

import pandas as pd
import re
from openpyxl.utils import get_column_letter

INPUT_FILE  = "01. 상제품매출상세 (3월가).xlsx"
OUTPUT_FILE = "01. 상제품매출상세 (3월가)_처리완료.xlsx"

# ── 로딩 ──────────────────────────────────────────────────
print("파일 로딩 중...")
xl = pd.ExcelFile(INPUT_FILE)
sheet = xl.sheet_names[0]
df = pd.read_excel(INPUT_FILE, sheet_name=sheet)
print(f"로딩 완료: {len(df)}행 x {len(df.columns)}열  (원본 시트: '{sheet}')")

# ── Step 1: E열에 매출구분 삽입 (공란) ───────────────────
cols = list(df.columns)
insert_pos_e = 4  # 0-based, 5번째 열 앞 (매출일자 다음)
df.insert(insert_pos_e, '매출구분', '')
print("매출구분 열 삽입 완료 (E열, 공란)")

# ── Step 2: 실적사업소 다음에 채널구분 삽입 (공란) ────────
pos_사업소 = df.columns.get_loc('실적사업소')
df.insert(pos_사업소 + 1, '채널구분', '')
print("채널구분 열 삽입 완료 (실적사업소 다음, 공란)")

# ── Step 3: 안분된채산조직 → 세부 열 추출 ────────────────
def extract_세부(val):
    if pd.isna(val):
        return ''
    s = str(val)
    matches = re.findall(r'\(([^)]+)\)', s)
    filtered = [m for m in matches if m != '일룸']
    return filtered[0] if filtered else ''

pos_안분 = df.columns.get_loc('안분된채산조직')
df.insert(pos_안분 + 1, '세부', df['안분된채산조직'].apply(extract_세부))
print("세부 열 삽입 완료 (안분된채산조직 다음)")

# ── Step 4: 안분된채산조직 괄호 제거 ─────────────────────
df['안분된채산조직'] = df['안분된채산조직'].apply(
    lambda v: re.sub(r'\([^)]*\)', '', str(v)).strip() if pd.notna(v) else v
)
print("안분된채산조직 괄호 제거 완료")

# ── Step 5: 채널구분 값 부여 ──────────────────────────────
def get_채널구분(val):
    if pd.isna(val):
        return ''
    s = str(val)
    if s in ('일룸유통', '일룸직영'):
        return '오프라인'
    elif s == '온라인CX개선팀':
        return '온라인'
    return ''

df['채널구분'] = df['안분된채산조직'].apply(get_채널구분)
print("채널구분 값 부여 완료")

# ── Step 6: 안분된채산조직_계층 → 3열 세분화 ─────────────
def split_hierarchy(val):
    if pd.isna(val):
        return '', '', ''
    parts = str(val).split('//')
    l1 = parts[0].strip() if len(parts) > 0 else ''
    l2 = parts[1].strip() if len(parts) > 1 else ''
    l3 = parts[2].strip() if len(parts) > 2 else ''
    return l1, l2, l3

hierarchy_split = df['안분된채산조직_계층'].apply(split_hierarchy)
df['채산조직_사업부'] = [x[0] for x in hierarchy_split]
df['채산조직_팀']    = [x[1] for x in hierarchy_split]
df['채산조직_채널']  = [x[2] for x in hierarchy_split]

# 안분된채산조직_계층 바로 다음으로 재배치
cols_now = list(df.columns)
new_cols, seen = [], set()
for c in cols_now:
    if c in seen:
        continue
    new_cols.append(c)
    seen.add(c)
    if c == '안분된채산조직_계층':
        for sub in ['채산조직_사업부', '채산조직_팀', '채산조직_채널']:
            if sub not in seen:
                new_cols.append(sub)
                seen.add(sub)

df = df[new_cols]
print("안분된채산조직_계층 세분화 완료")

# ── Step 7: 매출구분 값 부여 ──────────────────────────────
NAME_PATTERN = re.compile(r'^[가-힣]{2,4}[\(\(]')

def classify_매출구분(row):
    건명  = row['건명']
    창고  = row['상차지창고']

    건명_str = str(건명) if pd.notna(건명) else ''
    창고_str = str(창고) if pd.notna(창고) else ''

    has_매출조정 = '매출조정' in 건명_str
    has_전시품   = '전시품'   in 건명_str
    has_레이아웃 = '(레이아웃)' in 건명_str
    has_판촉물   = '판촉물'   in 건명_str
    has_영업장구 = '영업장구' in 건명_str
    has_시공병행 = bool(re.search(r'전시품\s*\(?\s*시공병행', 건명_str))
    is_전시품창고 = 창고_str == '일룸전시품창고'
    is_빈값      = pd.isna(건명) or 건명_str.strip() == ''
    has_이름prefix = bool(NAME_PATTERN.match(건명_str))

    if is_빈값:
        return 'extra'
    if has_매출조정 and not has_전시품:
        return 'extra'
    if has_판촉물:
        return '판촉물'
    if is_전시품창고:
        return '전시품'
    if has_이름prefix:
        return '일반'
    if has_영업장구:
        return '전시품'
    if has_시공병행:
        return '일반'
    if has_전시품 or has_레이아웃:
        return '전시품'
    return '일반'

df['매출구분'] = df.apply(classify_매출구분, axis=1)
counts = df['매출구분'].value_counts().to_dict()
print("매출구분 분류 완료:", counts)

# ── 최종 컬럼 확인 ────────────────────────────────────────
print(f"\n최종 컬럼 수: {len(df.columns)}")
for i, c in enumerate(df.columns):
    print(f"  {get_column_letter(i+1)}열: {c}")

# ── 저장 ─────────────────────────────────────────────────
print(f"\n저장 중: {OUTPUT_FILE}")
with pd.ExcelWriter(OUTPUT_FILE, engine='openpyxl') as writer:
    df.to_excel(writer, sheet_name='RAW', index=False)

print(f"저장 완료!")
print(f"최종: {len(df)}행 x {len(df.columns)}열")
