# -*- coding: utf-8 -*-
"""
안분된채산조직 값에서 괄호 및 괄호 안 내용 모두 제거
예: 일룸유통(일반) → 일룸유통
    온라인CX개선팀(공식몰)(일룸) → 온라인CX개선팀
    일룸직영(송파) → 일룸직영
"""

import pandas as pd
import re

print("파일 로딩 중...")
df = pd.read_excel('01. 상제품매출상세 (2월찐).xlsx', sheet_name='RAW')
print(f"로딩 완료: {len(df)}행 x {len(df.columns)}열")

def remove_brackets(val):
    if pd.isna(val):
        return val
    return re.sub(r'\([^)]*\)', '', str(val)).strip()

df['안분된채산조직'] = df['안분된채산조직'].apply(remove_brackets)
print("괄호 제거 완료")

# 샘플 확인
import json
sample = df[['안분된채산조직', '세부']].drop_duplicates().head(20)
with open('verify_안분.json', 'w', encoding='utf-8') as f:
    json.dump(sample.to_dict('records'), f, ensure_ascii=False, indent=2)

print("저장 중...")
with pd.ExcelWriter('01. 상제품매출상세 (2월찐).xlsx', engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
    df.to_excel(writer, sheet_name='RAW', index=False)

print("저장 완료!")
