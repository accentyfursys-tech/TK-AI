import sys
sys.stdout.reconfigure(encoding='utf-8')
import xlwings as xw
import openpyxl.utils as oxl

FILE = 'C:/iloom-workspace/10-projects/12-amoeba-tk/amoeba monthly/02. 분개장정보상세_처리완료.xlsx'

app = xw.App(visible=False)
app.display_alerts = False
app.screen_updating = False

try:
    wb = app.books.open(FILE)

    # 기존 피봇 시트 삭제
    for sname in ['채산피봇', '엑셀피봇(표1)', '분석피봇']:
        for s in wb.sheets:
            if s.name == sname:
                s.delete()
                break

    raw_sheet = wb.sheets['RAW']
    last_row = raw_sheet.range('A1').current_region.last_cell.row
    last_col = raw_sheet.range('A1').current_region.last_cell.column
    last_col_letter = oxl.get_column_letter(last_col)
    data_range_str = f"RAW!$A$1:${last_col_letter}${last_row}"
    print(f"데이터 범위: {data_range_str}")

    # ============================================================
    # 1. 채산피봇: 행=채산계정2, 열=팀세부, 필터=직접간접/채산계정1
    # ============================================================
    s1 = wb.sheets.add('채산피봇', after=wb.sheets['RAW'])
    pc1 = wb.api.PivotCaches().Create(SourceType=1, SourceData=data_range_str)
    pt1 = pc1.CreatePivotTable(TableDestination=s1.range('B2').api, TableName='채산피봇')

    pt1.PivotFields('직접간접').Orientation = 3
    pt1.PivotFields('직접간접').Position = 1
    pt1.PivotFields('채산계정1').Orientation = 3
    pt1.PivotFields('채산계정1').Position = 2

    pt1.PivotFields('채산계정2').Orientation = 1
    pt1.PivotFields('채산계정2').Position = 1

    pt1.PivotFields('팀세부').Orientation = 2
    pt1.PivotFields('팀세부').Position = 1

    pt1.AddDataField(pt1.PivotFields('금액(안분후)'), '합계', -4157)
    pt1.ColumnGrand = True
    pt1.RowGrand = True
    print("채산피봇 완료")

    # ============================================================
    # 2. 엑셀피봇(표1): 행=채산계정3, 열=팀세부, 필터=직접간접/채산계정1/채산계정2
    # ============================================================
    s2 = wb.sheets.add('엑셀피봇(표1)', after=wb.sheets['채산피봇'])
    pc2 = wb.api.PivotCaches().Create(SourceType=1, SourceData=data_range_str)
    pt2 = pc2.CreatePivotTable(TableDestination=s2.range('B2').api, TableName='엑셀피봇표1')

    pt2.PivotFields('직접간접').Orientation = 3
    pt2.PivotFields('직접간접').Position = 1
    pt2.PivotFields('채산계정1').Orientation = 3
    pt2.PivotFields('채산계정1').Position = 2
    pt2.PivotFields('채산계정2').Orientation = 3
    pt2.PivotFields('채산계정2').Position = 3

    pt2.PivotFields('채산계정3').Orientation = 1
    pt2.PivotFields('채산계정3').Position = 1

    pt2.PivotFields('팀세부').Orientation = 2
    pt2.PivotFields('팀세부').Position = 1

    pt2.AddDataField(pt2.PivotFields('금액(안분후)'), '합계', -4157)
    pt2.ColumnGrand = True
    pt2.RowGrand = True
    print("엑셀피봇(표1) 완료")

    # ============================================================
    # 3. 분析피봇: 감가상각 / 물류비 / 기타일반관리비
    # ============================================================
    s3 = wb.sheets.add('분석피봇', after=wb.sheets['엑셀피봇(표1)'])

    # --- 3-1. 감가상각피봇 (B2) ---
    pc3a = wb.api.PivotCaches().Create(SourceType=1, SourceData=data_range_str)
    pt3a = pc3a.CreatePivotTable(TableDestination=s3.range('B2').api, TableName='감가상각피봇')

    pf_c3a = pt3a.PivotFields('채산계정3')
    pf_c3a.Orientation = 3
    pf_c3a.Position = 1
    감가항목 = ['(판)유형자산감가상각비', '(판)무형자산상각비']
    for item in pf_c3a.PivotItems():
        if item.Name not in 감가항목:
            try: item.Visible = False
            except: pass

    pt3a.PivotFields('채산계정2').Orientation = 1
    pt3a.PivotFields('채산계정2').Position = 1
    pt3a.PivotFields('팀세부').Orientation = 2
    pt3a.PivotFields('팀세부').Position = 1
    pt3a.AddDataField(pt3a.PivotFields('금액(안분후)'), '합계', -4157)
    pt3a.ColumnGrand = True
    pt3a.RowGrand = True
    print("감가상각피봇 완료")

    gap1 = pt3a.TableRange2.Rows.Count + 4

    # --- 3-2. 물류비피봇 ---
    dest_b = f'B{2 + gap1}'
    pc3b = wb.api.PivotCaches().Create(SourceType=1, SourceData=data_range_str)
    pt3b = pc3b.CreatePivotTable(TableDestination=s3.range(dest_b).api, TableName='물류비피봇')

    pf_c3b = pt3b.PivotFields('채산계정3')
    pf_c3b.Orientation = 3
    pf_c3b.Position = 1
    물류항목 = ['(판)물류비(물류)_바로스', '(판)물류비(물류)_시디즈',
               '(판)물류비(운송)_바로스', '(판)물류비(운송)_시디즈',
               '(판)물류비(AS)', '(판)물류비(재고보관)']
    for item in pf_c3b.PivotItems():
        if item.Name not in 물류항목:
            try: item.Visible = False
            except: pass

    pt3b.PivotFields('세부').Orientation = 1
    pt3b.PivotFields('세부').Position = 1
    pt3b.PivotFields('팀세부').Orientation = 2
    pt3b.PivotFields('팀세부').Position = 1
    pt3b.AddDataField(pt3b.PivotFields('금액(안분후)'), '합계', -4157)
    pt3b.ColumnGrand = True
    pt3b.RowGrand = True
    print("물류비피봇 완료")

    gap2 = gap1 + pt3b.TableRange2.Rows.Count + 4

    # --- 3-3. 기타일반관리비피봇 ---
    dest_c = f'B{2 + gap2}'
    pc3c = wb.api.PivotCaches().Create(SourceType=1, SourceData=data_range_str)
    pt3c = pc3c.CreatePivotTable(TableDestination=s3.range(dest_c).api, TableName='기타관리비피봇')

    pf_기타 = pt3c.PivotFields('기타일반관리비')
    pf_기타.Orientation = 3
    pf_기타.Position = 1
    기타항목 = ['기타일반관리비_간접', '기타일반관리비_직접']
    for item in pf_기타.PivotItems():
        if item.Name not in 기타항목:
            try: item.Visible = False
            except: pass

    pt3c.PivotFields('채산계정3').Orientation = 1
    pt3c.PivotFields('채산계정3').Position = 1
    pt3c.PivotFields('팀세부').Orientation = 2
    pt3c.PivotFields('팀세부').Position = 1
    pt3c.AddDataField(pt3c.PivotFields('금액(안분후)'), '합계', -4157)
    pt3c.ColumnGrand = True
    pt3c.RowGrand = True
    print("기타관리비피봇 완료")

    wb.save()
    print("\n모든 피봇 시트 생성 완료! 저장됨.")

except Exception as e:
    print(f"오류: {e}")
    import traceback
    traceback.print_exc()
finally:
    app.quit()
