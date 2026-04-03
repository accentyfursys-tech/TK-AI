# -*- coding: utf-8 -*-
import pandas as pd
import json

df = pd.read_excel('01. 상제품매출상세 (2월찐).xlsx', sheet_name='RAW')

# 상차지창고 unique 값 확인
unique_창고 = sorted(df['상차지창고'].dropna().unique().tolist())

# 건명 샘플 - 각 케이스 확인
samples = {
    'unique_상차지창고': unique_창고,
    '건명_매출조정포함': df[df['건명'].str.contains('매출조정', na=False)]['건명'].unique().tolist()[:30],
    '건명_전시품포함': df[df['건명'].str.contains('전시품', na=False)]['건명'].unique().tolist()[:30],
    '건명_판촉물포함': df[df['건명'].str.contains('판촉물', na=False)]['건명'].unique().tolist()[:20],
    '건명_레이아웃포함': df[df['건명'].str.contains('레이아웃', na=False)]['건명'].unique().tolist()[:20],
    '건명_빈값건수': int(df['건명'].isna().sum()),
}

with open('inspect_건명.json', 'w', encoding='utf-8') as f:
    json.dump(samples, f, ensure_ascii=False, indent=2)

print("완료")
