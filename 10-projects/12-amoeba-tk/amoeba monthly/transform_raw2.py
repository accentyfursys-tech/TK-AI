# -*- coding: utf-8 -*-
"""
수정 작업:
1. 매출구분 값 공란으로 비우기
2. 채널구분 값 공란으로 비우기
3. 안분된채산조직에서 괄호 안 값 추출 → "세부" 열 추가 (안분된채산조직 바로 다음)
   - (일룸) 은 무시
"""

import pandas as pd
import re

print("파일 로딩 중...")
df = pd.read_excel('01. 상제품매출상세 (2월찐).xlsx', sheet_name='RAW')
print(f"로딩 완료: {len(df)}행 x {len(df.columns)}열")

# ============================
# 1. 매출구분, 채널구분 공란
# ============================
df['매출구분'] = ''
df['채널구분'] = ''
print("매출구분, 채널구분 공란 처리 완료")

# ============================
# 2. 안분된채산조직에서 괄호값 추출 → 세부 열
# ============================
def extract_세부(val):
    if pd.isna(val):
        return ''
    s = str(val)
    # 모든 괄호 추출
    matches = re.findall(r'\(([^)]+)\)', s)
    # (일룸) 제외
    filtered = [m for m in matches if m != '일룸']
    if filtered:
        return filtered[0]  # 첫 번째 유효 괄호값
    return ''

세부_values = df['안분된채산조직'].apply(extract_세부)

# 안분된채산조직 바로 다음에 세부 열 삽입
pos = df.columns.get_loc('안분된채산조직')
df.insert(pos + 1, '세부', 세부_values)
print("세부 열 삽입 완료")

# 샘플 확인
import json
sample = df[['안분된채산조직', '세부']].drop_duplicates().head(20)
with open('verify_세부.json', 'w', encoding='utf-8') as f:
    json.dump(sample.to_dict('records'), f, ensure_ascii=False, indent=2)

# ============================
# 저장
# ============================
print(f"\n최종 컬럼 수: {len(df.columns)}")
output_file = '01. 상제품매출상세 (2월찐).xlsx'
print(f"저장 중: {output_file}")

with pd.ExcelWriter(output_file, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
    df.to_excel(writer, sheet_name='RAW', index=False)

print("저장 완료!")
