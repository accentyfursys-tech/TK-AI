# -*- coding: utf-8 -*-
import pandas as pd
import json

df = pd.read_excel('01. 상제품매출상세 (2월찐).xlsx', sheet_name='RAW')

# 전체 데이터 unique 값 확인
unique_hierarchy = sorted(df['안분된채산조직_계층'].unique().tolist())
unique_채산조직 = sorted(df['안분된채산조직'].unique().tolist())
unique_account = sorted(df['채산계정'].unique().tolist())
unique_order_type = sorted(df['수주유형'].unique().tolist())
unique_bizoffice = sorted(df['실적사업소'].unique().tolist())

result = {
    '전체행수': len(df),
    'unique_안분된채산조직_계층': unique_hierarchy,
    'unique_안분된채산조직': unique_채산조직,
    'unique_채산계정': unique_account,
    'unique_수주유형': unique_order_type,
    'unique_실적사업소': unique_bizoffice,
}

with open('inspect_result3.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2, default=str)

print(f"전체 행수: {len(df)}")
print("완료")
