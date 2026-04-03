# -*- coding: utf-8 -*-
import pandas as pd
import json

df = pd.read_excel('01. 상제품매출상세 (2월찐).xlsx', sheet_name='RAW', nrows=5)

result = {}
result['columns'] = list(df.columns)
result['sample_row1'] = df.iloc[0].tolist()
result['sample_row2'] = df.iloc[1].tolist()

# 안분된채산조직_경로 컬럼 샘플
for col in df.columns:
    if '채산' in str(col) or '안분' in str(col):
        result[f'sample_{col}'] = df[col].tolist()

with open('inspect_result.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2, default=str)

print("완료")
