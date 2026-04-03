import sys
sys.stdout.reconfigure(encoding='utf-8')
import xlwings as xw
import openpyxl.utils as oxl

FILE = 'C:/iloom-workspace/10-projects/12-amoeba-tk/amoeba monthly/2025년 일룸 사업부 분개장_처리완료.xlsx'

app = xw.App(visible=False)
app.display_alerts = False
app.screen_updating = False

try:
    wb = app.books.open(FILE)

    # 기존 채산피봇(라이브) 시트 삭제
    for s in wb.sheets:
        if s.name == '채산피봇(라이브)':
            s.delete()
            break

    raw_sheet = wb.sheets['RAW']
    last_row = raw_sheet.range('A1').current_region.last_cell.row
    last_col = raw_sheet.range('A1').current_region.last_cell.column
    last_col_letter = oxl.get_column_letter(last_col)
    data_range_str = f"RAW!$A$1:${last_col_letter}${last_row}"
    print(f"데이터 범위: {data_range_str}")

    # 채산피봇 시트 뒤에 추가
    s_live = wb.sheets.add('채산피봇(라이브)', after=wb.sheets['채산피봇'])

    pc = wb.api.PivotCaches().Create(SourceType=1, SourceData=data_range_str)
    pt = pc.CreatePivotTable(
        TableDestination=s_live.range('A1').api,
        TableName='채산피봇라이브'
    )

    # 행: 채산계정1 → 채산계정2 → 채산계정3
    pt.PivotFields('채산계정1').Orientation = 1
    pt.PivotFields('채산계정1').Position = 1
    pt.PivotFields('채산계정2').Orientation = 1
    pt.PivotFields('채산계정2').Position = 2
    pt.PivotFields('채산계정3').Orientation = 1
    pt.PivotFields('채산계정3').Position = 3

    # 열: 팀세부 → 직접간접
    pt.PivotFields('팀세부').Orientation = 2
    pt.PivotFields('팀세부').Position = 1
    pt.PivotFields('직접간접').Orientation = 2
    pt.PivotFields('직접간접').Position = 2

    # 값: 금액(안분후) 합계
    pt.AddDataField(pt.PivotFields('금액(안분후)'), '합계', -4157)

    pt.ColumnGrand = True
    pt.RowGrand = True

    # 팀세부 순서: 리테일 → 직영 → 온라인
    try:
        item_order = ['리테일', '직영', '온라인']
        pf_팀 = pt.PivotFields('팀세부')
        for idx, name in enumerate(item_order, 1):
            pf_팀.PivotItems(name).Position = idx
    except Exception as e:
        print(f"열 순서 조정 실패 (무시): {e}")

    # 채산계정1 순서: 고정비 → 변동비 → 영업외손익
    try:
        c1_order = ['고정비', '변동비', '영업외손익']
        pf_c1 = pt.PivotFields('채산계정1')
        for idx, name in enumerate(c1_order, 1):
            pf_c1.PivotItems(name).Position = idx
    except Exception as e:
        print(f"행 순서 조정 실패 (무시): {e}")

    pt.TableStyle2 = 'PivotStyleMedium9'

    for i in range(1, pt.DataFields.Count + 1):
        pt.DataFields.Item(i).NumberFormat = '#,##0'

    wb.save()
    print("완료! 채산피봇(라이브) 시트 생성됨.")

except Exception as e:
    print(f"오류: {e}")
    import traceback
    traceback.print_exc()
finally:
    app.quit()
