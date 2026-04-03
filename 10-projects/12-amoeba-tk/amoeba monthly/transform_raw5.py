# -*- coding: utf-8 -*-
"""
매출구분 열 값 부여
1) extra: 건명 빈값 OR (매출조정 포함 AND 전시품 미포함)
2) 판촉물: 건명에 '판촉물' 포함
3) 전시품:
   - 상차지창고 == '일룸전시품창고' (무조건, 이름prefix 여부 무관)
   - 건명에 '영업장구' 포함
   - 건명에 '(레이아웃)' 또는 '전시품' 포함
   - 단 제외 조건:
     a) 앞에 사람 이름 (한글 2-4글자로 시작) → 일반
     b) '전시품 시공병행' 또는 '전시품시공병행' 포함 (괄호 여부 무관) → 일반
4) 일반: 위 모두 해당 없는 경우
"""

import pandas as pd
import re

print("파일 로딩 중...")
df = pd.read_excel('01. 상제품매출상세 (2월찐).xlsx', sheet_name='RAW')
print(f"로딩 완료: {len(df)}행 x {len(df.columns)}열")

# 사람 이름이 앞에 붙은 패턴: 한글 2~4글자로 시작
# 예: 염현희(전시품), 오다혜(현)(전시품), 최송화(전시품)(현)
NAME_PATTERN = re.compile(r'^[가-힣]{2,4}[\(\(]')

def classify_매출구분(row):
    건명 = row['건명']
    창고 = row['상차지창고']

    건명_str = str(건명) if pd.notna(건명) else ''
    창고_str = str(창고) if pd.notna(창고) else ''

    has_매출조정 = '매출조정' in 건명_str
    has_전시품 = '전시품' in 건명_str
    has_레이아웃 = '(레이아웃)' in 건명_str
    has_판촉물 = '판촉물' in 건명_str
    has_영업장구 = '영업장구' in 건명_str
    # 괄호 여부 무관: '전시품 시공병행', '전시품(시공병행)', '(전시품 시공병행)' 등 모두 처리
    has_시공병행 = bool(re.search(r'전시품\s*\(?\s*시공병행', 건명_str))
    is_전시품창고 = 창고_str == '일룸전시품창고'
    is_빈값 = pd.isna(건명) or 건명_str.strip() == ''

    # 사람 이름이 앞에 붙은 경우 (한글 2~4글자로 시작)
    has_이름prefix = bool(NAME_PATTERN.match(건명_str))

    # 1) extra
    if is_빈값:
        return 'extra'
    if has_매출조정 and not has_전시품:
        return 'extra'

    # 2) 판촉물
    if has_판촉물:
        return '판촉물'

    # 3-a) 상차지창고 == 일룸전시품창고 → 무조건 전시품 (이름prefix 무관)
    if is_전시품창고:
        return '전시품'

    # 3-b) 이름prefix 있으면 일반
    if has_이름prefix:
        return '일반'

    # 3-c) 영업장구 → 전시품
    if has_영업장구:
        return '전시품'

    # 3-d) 전시품 시공병행 → 일반 (괄호 여부 무관)
    if has_시공병행:
        return '일반'

    if has_전시품 or has_레이아웃:
        return '전시품'

    # 4) 일반
    return '일반'

df['매출구분'] = df.apply(classify_매출구분, axis=1)
print("매출구분 분류 완료")

counts = df['매출구분'].value_counts().to_dict()
print("분류 결과:", counts)

# 경계 케이스 재확인
import json
edge = df[df['건명'].str.contains('전시품', na=False) &
          df['건명'].apply(lambda x: bool(NAME_PATTERN.match(str(x) if pd.notna(x) else '')))][['건명', '매출구분']].drop_duplicates().head(10)

samples = {
    'counts': counts,
    'edge_이름+전시품': edge.to_dict('records')
}
with open('verify_매출구분2.json', 'w', encoding='utf-8') as f:
    json.dump(samples, f, ensure_ascii=False, indent=2)

print("저장 중...")
with pd.ExcelWriter('01. 상제품매출상세 (2월찐).xlsx', engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
    df.to_excel(writer, sheet_name='RAW', index=False)

print("저장 완료!")
