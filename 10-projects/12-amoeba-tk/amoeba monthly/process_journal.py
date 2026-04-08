# -*- coding: utf-8 -*-
"""
분개장정보상세 처리 스크립트 (통합)
- 입력: 02. 분개장정보상세(3월가).xlsx
- 출력: 02. 분개장정보상세(3월가)_처리완료.xlsx (RAW 시트)

처리 내용 (원본 25열 → 29열):
1. 채산계정4 다음 → '부계정' 열 추가
   - 채산계정1=매출원가 → '원가', 나머지 → '매출'
2. 안분된채산조직 기준 → '직접간접' 열 추가
   - 온라인CX개선팀 → '온라인'
   - 일룸유통(일반), 일룸유통(투자) → '직영'
   - 그 외 → '간접'
3. 안분된채산조직 다음 → '세부' 열 추가
   - 괄호 안 값 추출 (일룸 제외)
4. 맨 끝 → '기타일반관리비' 열 추가
   - 채산계정1=매출원가 AND 채산계정2=일반계정 AND 직접간접=간접 → '기타일반관리비_간접'
   - 채산계정1=매출원가 AND 채산계정2=일반계정 AND 직접간접=직접  → '기타일반관리비_직접'
   - 채산계정1=매출원가 AND 채산계정2=일반계정 AND 직접간접=온라인 → '기타일반관리비_간접'  (온라인=간접 취급)
   - 나머지 → NaN
"""

import pandas as pd
import re
from openpyxl.utils import get_column_letter

INPUT_FILE  = "02. 분개장정보상세(3월가).xlsx"
OUTPUT_FILE = "02. 분개장정보상세(3월가)_처리완료.xlsx"

# ── 로딩 ──────────────────────────────────────────────────
print("파일 로딩 중...")
xl = pd.ExcelFile(INPUT_FILE)
sheet = xl.sheet_names[0]
df = pd.read_excel(INPUT_FILE, sheet_name=sheet)
print(f"로딩 완료: {len(df)}행 x {len(df.columns)}열  (원본 시트: '{sheet}')")
print("헤더:", list(df.columns))

# ── Step 1: 채산계정4(col7) 다음에 '부계정' 삽입 ─────────
def get_부계정(val):
    s = str(val) if pd.notna(val) else ''
    return '원가' if '매출원가' in s else '매출'

pos_cc1 = df.columns.get_loc('채산계정1')
부계정_vals = df['채산계정1'].apply(get_부계정)

# 채산계정4 위치 찾기 (없을 수도 있음)
if '채산계정4' in df.columns:
    pos_insert = df.columns.get_loc('채산계정4') + 1
elif '채산계정_계층' in df.columns:
    pos_insert = df.columns.get_loc('채산계정_계층')
else:
    pos_insert = df.columns.get_loc('채산계정1') + 4  # 계정1~4 이후

df.insert(pos_insert, '부계정', 부계정_vals)
print(f"'부계정' 열 삽입 완료 (위치: {pos_insert+1}열)")
print("부계정 분포:", df['부계정'].value_counts().to_dict())

# ── Step 2: 안분된채산조직 기준 '직접간접' 열 삽입 ────────
# 안분된채산조직_계층 바로 앞에 삽입 (원본 기준 실적사업소 계열)
def get_직접간접(val):
    s = str(val) if pd.notna(val) else ''
    if '온라인CX개선팀' in s:
        return '온라인'
    elif '일룸유통(일반)' in s or '일룸유통(투자)' in s:
        return '직영'
    else:
        return '간접'

pos_안분 = df.columns.get_loc('안분된채산조직')
직접간접_vals = df['안분된채산조직'].apply(get_직접간접)
df.insert(pos_안분, '직접간접', 직접간접_vals)
print(f"'직접간접' 열 삽입 완료 (안분된채산조직 앞)")
print("직접간접 분포:", df['직접간접'].value_counts().to_dict())

# ── Step 3: 안분된채산조직 다음에 '세부' 열 삽입 ──────────
def extract_세부(val):
    if pd.isna(val):
        return ''
    s = str(val)
    matches = re.findall(r'\(([^)]+)\)', s)
    filtered = [m for m in matches if m != '일룸']
    return filtered[0] if filtered else ''

pos_안분2 = df.columns.get_loc('안분된채산조직')
df.insert(pos_안분2 + 1, '세부', df['안분된채산조직'].apply(extract_세부))
print(f"'세부' 열 삽입 완료 (안분된채산조직 다음)")
print("세부 샘플:", df['세부'].value_counts().head(5).to_dict())

# ── Step 4: 맨 끝에 '기타일반관리비' 열 추가 ─────────────
def get_기타일반관리비(row):
    cc1 = str(row['채산계정1']) if pd.notna(row['채산계정1']) else ''
    cc2 = str(row['채산계정2']) if pd.notna(row['채산계정2']) else ''
    jj  = str(row['직접간접'])  if pd.notna(row['직접간접'])  else ''

    if '매출원가' in cc1 and '일반계정' in cc2:
        if jj == '직접':
            return '기타일반관리비_직접'
        else:  # 간접 or 온라인
            return '기타일반관리비_간접'
    return None

df['기타일반관리비'] = df.apply(get_기타일반관리비, axis=1)
print(f"'기타일반관리비' 열 추가 완료 (맨 끝)")
print("기타일반관리비 분포:", df['기타일반관리비'].value_counts(dropna=False).to_dict())

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
