# -*- coding: utf-8 -*-
"""
채널구분 값 채우기
- 일룸유통, 일룸직영 → 오프라인
- 온라인CX개선팀 → 온라인
"""

import pandas as pd

print("파일 로딩 중...")
df = pd.read_excel('01. 상제품매출상세 (2월찐).xlsx', sheet_name='RAW')
print(f"로딩 완료: {len(df)}행 x {len(df.columns)}열")

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

# 검증
import json
check = df[['안분된채산조직', '채널구분']].drop_duplicates().to_dict('records')
with open('verify_채널.json', 'w', encoding='utf-8') as f:
    json.dump(check, f, ensure_ascii=False, indent=2)

print("저장 중...")
with pd.ExcelWriter('01. 상제품매출상세 (2월찐).xlsx', engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
    df.to_excel(writer, sheet_name='RAW', index=False)

print("저장 완료!")
