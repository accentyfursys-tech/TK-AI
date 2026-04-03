# -*- coding: utf-8 -*-
import pandas as pd
import json

df = pd.read_excel('01. 상제품매출상세 (2월찐).xlsx', sheet_name='RAW', nrows=3)

result = {
    'columns': list(df.columns),
    'sample_E_매출구분': df['매출구분'].tolist(),
    'sample_채널구분': df['채널구분'].tolist(),
    'sample_채산조직_사업부': df['채산조직_사업부'].tolist(),
    'sample_채산조직_팀': df['채산조직_팀'].tolist(),
    'sample_채산조직_채널': df['채산조직_채널'].tolist(),
    'sample_안분된채산조직_계층': df['안분된채산조직_계층'].tolist(),
}

with open('verify_result.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2, default=str)

print("검증 완료")
