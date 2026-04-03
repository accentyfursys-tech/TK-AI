import pandas as pd
import sys
sys.stdout.reconfigure(encoding='utf-8')

src = 'C:/iloom-workspace/10-projects/12-amoeba-tk/amoeba monthly/02. 분개장정보상세.xlsx'
out = 'C:/iloom-workspace/10-projects/12-amoeba-tk/amoeba monthly/02. 분개장정보상세_처리완료.xlsx'

df = pd.read_excel(src)
df['채산계정3_원본'] = df['채산계정3']

# 1. 직접간접
keywords_direct = ['유통경쟁력강화팀','온라인CX개선팀','리테일','직영+리테일','영업효율','일룸유통']
def 직접간접분류(val):
    if pd.isna(val): return '간접'
    for kw in keywords_direct:
        if kw in str(val): return '직접'
    return '간접'
df['직접간접'] = df['채산코스트센터'].apply(직접간접분류)

# 2. 팀세부
def 팀세부분류(val):
    if pd.isna(val): return ''
    val = str(val)
    if '온라인CX개선팀' in val: return '온라인'
    if '일룸유통' in val: return '리테일'
    if '일룸직영' in val: return '직영'
    return ''
df['팀세부'] = df['안분된채산조직'].apply(팀세부분류)

# 3. 세부
def 세부분류(val):
    if pd.isna(val): return ''
    val = str(val)
    if '(' in val and ')' in val:
        return val[val.index('(')+1:val.index(')')]
    return ''
df['세부'] = df['안분된채산조직'].apply(세부분류)

# 4. 채산계정3
def 채산계정3분류(row):
    g = str(row['채산계정3_원본']) if not pd.isna(row['채산계정3_원본']) else ''
    f = str(row['채산계정2']) if not pd.isna(row['채산계정2']) else ''
    m = str(row['비고(적요)']) if not pd.isna(row['비고(적요)']) else ''
    s = str(row['세부']) if row['세부'] else ''

    if g == '(판)물류비(물류)':
        return '(판)물류비(물류)_시디즈' if '안성' in m else '(판)물류비(물류)_바로스'
    if g == '(판)물류비(운송)':
        return '(판)물류비(운송)_시디즈' if '안성' in m else '(판)물류비(운송)_바로스'
    if f == '(판)판매수수료':
        if 'PSA' in m: return '(판)판매수수료_PSA'
        if 'SPC' in m or '페이' in m: return '(판)판매수수료_PG사'
        if any(kw in m for kw in ['쿠팡','네이버','29CM','씨제이몰','에스에스지','엘롯데','오늘의집','LG홈스타일']): return '(판)판매수수료_외부몰'
        if any(kw in m for kw in ['롯데','스타필드','신세계','송도']): return '(판)판매수수료_입점몰'
        if '투자' in s: return '(판)판매수수료_투자B'
        if '일반' in s: return '(판)판매수수료_B/S'
        return '(판)판매수수료_기타'
    if g == '' or g == 'nan':
        return f
    return g

df['채산계정3'] = df.apply(채산계정3분류, axis=1)

# 5. 기타일반관리비
간접항목 = ['(판)교육훈련비','(판)도서인쇄비','(판)보험료','(판)비품비','(판)소모품비',
           '(판)수도광열비','(판)여비교통비','(판)접대비','(판)차량유지비','(판)통신비']
직접항목 = ['(판)도서인쇄비','(판)경상연구개발비','(판)보험료','(판)세금과공과',
           '(판)소모품비','(판)차량유지비','(판)하자보수비']

def 기타분류(row):
    g = str(row['채산계정3']) if not pd.isna(row['채산계정3']) else ''
    d = str(row['직접간접']) if not pd.isna(row['직접간접']) else ''
    if g in 간접항목 and d == '간접': return '기타일반관리비_간접'
    if g in 직접항목 and d == '직접': return '기타일반관리비_직접'
    return ''

df['기타일반관리비'] = df.apply(기타분류, axis=1)

# 컬럼 순서 재배치
cols = list(df.columns)
for c in ['직접간접','팀세부','세부','채산계정3_원본','기타일반관리비']:
    cols.remove(c)

j_idx = cols.index('공통직접구분')
cols.insert(j_idx+1, '직접간접')
o_idx = cols.index('안분된채산조직')
cols.insert(o_idx, '팀세부')
o_idx2 = cols.index('안분된채산조직')
cols.insert(o_idx2+1, '세부')
cols.append('기타일반관리비')

df = df[cols]

df.to_excel(out, sheet_name='RAW', index=False)
print(f'완료! 총 {len(df)}행, {len(df.columns)}열')
print(f'기타일반관리비 분류: {df["기타일반관리비"].value_counts().to_dict()}')
