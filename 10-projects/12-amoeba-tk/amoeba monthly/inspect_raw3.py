# -*- coding: utf-8 -*-
import pandas as pd
import json

df = pd.read_excel('01. 상제품매출상세 (2월찐).xlsx', sheet_name='RAW', nrows=1000)

# 안분된채산조직_계층의 unique 값 확인
unique_hierarchy = df['안분된채산조직_계층'].unique().tolist()

# 채산계정 unique 값 확인
unique_account = df['채산계정'].unique().tolist()

# 수주유형 unique 값 (매출구분 후보)
unique_order_type = df['수주유형'].unique().tolist()

# 실적사업소 unique 값
unique_bizoffice = df['실적사업소'].unique().tolist()

result = {
    'unique_안분된채산조직_계층': unique_hierarchy,
    'unique_채산계정': unique_account,
    'unique_수주유형': unique_order_type,
    'unique_실적사업소': unique_bizoffice,
    '전체행수': len(df)
}

with open('inspect_result2.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2, default=str)

print("완료")
