# -*- coding: utf-8 -*-
import pandas as pd

df = pd.read_excel('01. 상제품매출상세 (2월찐).xlsx', sheet_name='RAW', nrows=5)
print("=== 컬럼 목록 ===")
for i, col in enumerate(df.columns):
    print(f"col {i+1}: {col}")

print("\n=== 안분된 채산조직 샘플 ===")
# 안분된 채산조직 컬럼 찾기
for col in df.columns:
    if '채산' in str(col) or '안분' in str(col):
        print(f"\n[{col}]")
        print(df[col].tolist())

print("\n=== 실적사업소 컬럼 찾기 ===")
for col in df.columns:
    if '사업소' in str(col) or '실적' in str(col):
        print(f"found: {col}")
        print(df[col].tolist())

print("\n=== 판매 관련 컬럼 찾기 ===")
for col in df.columns:
    if '판매' in str(col) or '매출' in str(col):
        print(f"found: {col}")
        print(df[col].tolist())
