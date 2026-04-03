"""
채산 데이터 자동 추출 스크립트
아메바어카운트 엑셀 → 매출/매출원가 추출
"""

import os
import glob
import tkinter as tk
import pandas as pd
from datetime import date, timedelta

# ── 설정 ──────────────────────────────────────────────
FOLDER = r"C:\iloom-workspace\10-projects\12-amoeba-tk\amoeba weekly"
# ───────────────────────────────────────────────────────


def get_last_week_range():
    """전주 월요일 ~ 토요일 날짜 반환"""
    today = date.today()
    # 이번 주 월요일
    this_monday = today - timedelta(days=today.weekday())
    # 전주 월요일 ~ 토요일
    last_monday = this_monday - timedelta(weeks=1)
    last_saturday = last_monday + timedelta(days=5)
    return last_monday, last_saturday


def find_latest_excel(folder):
    """폴더에서 가장 최근 엑셀 파일 찾고, 나머지 이전 파일 삭제"""
    patterns = ["*.xlsx", "*.xls", "*.csv"]
    files = []
    for pattern in patterns:
        files.extend(glob.glob(os.path.join(folder, pattern)))
    if not files:
        raise FileNotFoundError(f"엑셀 파일을 찾을 수 없어요: {folder}")
    latest = max(files, key=os.path.getmtime)
    print(f"파일 감지: {os.path.basename(latest)}")
    # 이전 파일 자동 삭제
    for f in files:
        if f != latest:
            os.remove(f)
            print(f"이전 파일 삭제: {os.path.basename(f)}")
    return latest


def extract_chaasan(file_path, start_date, end_date):
    """매출/매출원가 추출"""
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".csv":
        df = pd.read_csv(file_path, encoding="euc-kr")
    else:
        df = pd.read_excel(file_path)

    # 매출일자 컬럼 날짜 변환
    df["매출일자"] = pd.to_datetime(df["매출일자"], errors="coerce")

    # 전주 월~토 필터링
    mask = (df["매출일자"].dt.date >= start_date) & (df["매출일자"].dt.date <= end_date)
    filtered = df[mask]

    if filtered.empty:
        print(f"[경고] {start_date} ~ {end_date} 기간 데이터가 없어요.")
        return None

    # 합산
    매출 = filtered["매출금액(안분후)"].sum()
    매출원가 = filtered["매출원가(안분후)"].sum()
    매출원가율 = (매출원가 / 매출 * 100) if 매출 != 0 else 0

    return {
        "기간": f"{start_date} ~ {end_date}",
        "매출": 매출,
        "매출원가": 매출원가,
        "매출원가율": 매출원가율,
    }


def copy_to_clipboard(text):
    """클립보드에 복사"""
    root = tk.Tk()
    root.withdraw()
    root.clipboard_clear()
    root.clipboard_append(text)
    root.update()
    root.after(3000, root.destroy)
    root.mainloop()


def print_result(result):
    """결과 출력 및 클립보드 복사"""
    매출_백만 = round(result['매출'] / 1_000_000)
    매출원가_백만 = round(result['매출원가'] / 1_000_000)
    비율 = f"{result['매출원가율']:.1f}%"

    print("\n" + "=" * 40)
    print(f"  집계 기간: {result['기간']}")
    print("=" * 40)
    print(f"  {'구분':<10} {'금액(백만원)':>12}  {'비율':>6}")
    print("-" * 40)
    print(f"  {'매출':<10} {매출_백만:>12,}  {'100.0%':>6}")
    print(f"  {'매출원가':<10} {매출원가_백만:>12,}  {비율:>6}")
    print("=" * 40)

    # 클립보드 복사 (매출 / 매출원가 / 비율 탭 구분)
    clip_text = f"{매출_백만}\t{매출원가_백만}\t{비율}"
    copy_to_clipboard(clip_text)
    print("\n[클립보드 복사 완료] 컨플루언스에서 Ctrl+V 로 붙여넣으세요!")
    print(f"복사된 값: 매출 {매출_백만:,} / 매출원가 {매출원가_백만:,} / 비율 {비율}")


def main():
    start_date, end_date = get_last_week_range()
    print(f"집계 기간: {start_date} (월) ~ {end_date} (토)")

    file_path = find_latest_excel(FOLDER)
    result = extract_chaasan(file_path, start_date, end_date)

    if result:
        print_result(result)


if __name__ == "__main__":
    main()
    input("\n엔터를 누르면 창이 닫힙니다...")
