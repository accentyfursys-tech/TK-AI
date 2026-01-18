#!/usr/bin/env python3
"""
다나와 리뷰 수집기 (경량 버전)

Firecrawl로 리뷰 텍스트만 추출 → 구글 시트에 업로드

사용법:
  python danawa-reviews.py <다나와_URL_또는_pcode> [--sheet SHEET_URL]

예시:
  python danawa-reviews.py 6268026
  python danawa-reviews.py https://prod.danawa.com/info/?pcode=6268026
  python danawa-reviews.py 6268026 --sheet https://docs.google.com/spreadsheets/d/xxx
"""

import os
import sys
import re
import json
import argparse
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")

# 색상 출력
class Colors:
    BLUE = '\033[0;34m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    RED = '\033[0;31m'
    NC = '\033[0m'

def print_color(text, color):
    print(f"{color}{text}{Colors.NC}")


def extract_pcode(url_or_pcode):
    """URL 또는 pcode에서 상품코드 추출"""
    if url_or_pcode.isdigit():
        return url_or_pcode

    match = re.search(r'pcode=(\d+)', url_or_pcode)
    if match:
        return match.group(1)

    raise ValueError(f"pcode를 찾을 수 없습니다: {url_or_pcode}")


def crawl_reviews(pcode):
    """Firecrawl로 리뷰 페이지 크롤링 (텍스트만)"""
    url = f"https://prod.danawa.com/info/?pcode={pcode}&tab=review"
    print_color(f"🔍 리뷰 수집 중: {url}", Colors.BLUE)

    try:
        from firecrawl import FirecrawlApp

        app = FirecrawlApp(api_key=FIRECRAWL_API_KEY)

        # Firecrawl v2 API
        result = app.scrape(
            url,
            formats=['markdown'],
            only_main_content=True,
            wait_for=3000
        )

        markdown = getattr(result, 'markdown', '') or ''
        metadata = getattr(result, 'metadata', {}) or {}

        print_color(f"✅ 텍스트 추출 완료 ({len(markdown)} 글자)", Colors.GREEN)

        return {
            'markdown': markdown,
            'metadata': metadata,
            'url': url,
            'pcode': pcode
        }

    except Exception as e:
        print_color(f"❌ 크롤링 실패: {e}", Colors.RED)
        return None


def parse_reviews(markdown):
    """마크다운에서 리뷰 추출"""
    reviews = []

    # 리뷰 패턴 (다나와 리뷰 구조에 맞게 조정 필요)
    # 기본적으로 20자 이상의 한글 포함 텍스트를 리뷰로 간주
    lines = markdown.split('\n')

    current_review = []
    for line in lines:
        line = line.strip()

        # 리뷰 시작/종료 패턴 감지
        if len(line) > 20 and re.search(r'[가-힣]', line):
            # 메뉴, 네비게이션 등 제외
            skip_patterns = [
                r'^(홈|로그인|회원가입|장바구니|마이페이지)',
                r'^(상품정보|상품평|추천|Q&A)',
                r'^\d+원$',
                r'^(무료배송|당일배송)',
            ]

            if not any(re.match(p, line) for p in skip_patterns):
                reviews.append({
                    'content': line,
                    'length': len(line)
                })

    print_color(f"📝 리뷰 {len(reviews)}개 추출", Colors.GREEN)
    return reviews


def upload_to_sheets(reviews, sheet_url, product_info):
    """구글 시트에 리뷰 업로드 (OAuth 인증)"""
    print_color(f"📊 구글 시트 업로드 중...", Colors.BLUE)

    try:
        import gspread
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        import os.path

        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        creds = None
        creds_path = os.path.expanduser('~/.config/gspread/credentials.json')
        token_path = os.path.expanduser('~/.config/gspread/authorized_user.json')

        # 저장된 토큰이 있으면 로드
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)

        # 유효한 자격증명이 없으면 인증 진행
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
                # 로컬 서버로 OAuth 인증 (브라우저 자동 열림)
                creds = flow.run_local_server(port=0)

            # 토큰 저장
            with open(token_path, 'w') as token:
                token.write(creds.to_json())

        gc = gspread.authorize(creds)

        # 시트 열기
        sheet_id = re.search(r'/d/([a-zA-Z0-9-_]+)', sheet_url)
        if not sheet_id:
            print_color(f"❌ 시트 URL이 올바르지 않습니다", Colors.RED)
            return False

        spreadsheet = gc.open_by_key(sheet_id.group(1))

        # 워크시트 생성 또는 선택
        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        worksheet_name = f"리뷰_{product_info.get('pcode', 'unknown')}_{timestamp}"

        try:
            worksheet = spreadsheet.add_worksheet(title=worksheet_name, rows=len(reviews)+10, cols=5)
        except:
            worksheet = spreadsheet.sheet1

        # 헤더 작성
        headers = ['번호', '리뷰 내용', '글자수', '수집일시', 'URL']
        worksheet.update('A1:E1', [headers])

        # 데이터 작성
        rows = []
        for i, review in enumerate(reviews, 1):
            rows.append([
                i,
                review['content'],
                review['length'],
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                product_info.get('url', '')
            ])

        if rows:
            worksheet.update(f'A2:E{len(rows)+1}', rows)

        print_color(f"✅ 구글 시트 업로드 완료: {worksheet_name}", Colors.GREEN)
        print(f"   📎 {sheet_url}")
        return True

    except ImportError:
        print_color("⚠️ gspread 미설치. pip install gspread google-auth", Colors.YELLOW)
        return False
    except Exception as e:
        print_color(f"❌ 시트 업로드 실패: {e}", Colors.RED)
        return False


def save_to_file(reviews, product_info, output_path=None):
    """로컬 파일로 저장"""
    if not output_path:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = f"/tmp/danawa_reviews_{product_info['pcode']}_{timestamp}.json"

    data = {
        'pcode': product_info['pcode'],
        'url': product_info['url'],
        'crawled_at': datetime.now().isoformat(),
        'total_reviews': len(reviews),
        'reviews': reviews
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print_color(f"💾 로컬 저장: {output_path}", Colors.GREEN)
    return output_path


def main():
    parser = argparse.ArgumentParser(description='다나와 리뷰 수집기')
    parser.add_argument('url_or_pcode', help='다나와 URL 또는 상품코드(pcode)')
    parser.add_argument('--sheet', help='구글 시트 URL (선택)')
    parser.add_argument('--output', '-o', help='출력 파일 경로 (선택)')

    args = parser.parse_args()

    # API 키 확인
    if not FIRECRAWL_API_KEY:
        print_color("❌ FIRECRAWL_API_KEY가 설정되지 않았습니다", Colors.RED)
        print("\n.env 파일에 추가:")
        print("  FIRECRAWL_API_KEY='your_key_here'")
        sys.exit(1)

    print_color(f"\n{'='*60}", Colors.BLUE)
    print_color("🛒 다나와 리뷰 수집기", Colors.BLUE)
    print_color(f"{'='*60}\n", Colors.BLUE)

    # 1. pcode 추출
    try:
        pcode = extract_pcode(args.url_or_pcode)
        print_color(f"📦 상품코드: {pcode}", Colors.GREEN)
    except ValueError as e:
        print_color(str(e), Colors.RED)
        sys.exit(1)

    # 2. 크롤링
    result = crawl_reviews(pcode)
    if not result:
        sys.exit(1)

    # 3. 리뷰 파싱
    reviews = parse_reviews(result['markdown'])

    # 4. 로컬 저장
    output_path = save_to_file(reviews, result, args.output)

    # 5. 구글 시트 업로드 (옵션)
    if args.sheet:
        upload_to_sheets(reviews, args.sheet, result)

    print_color(f"\n{'='*60}", Colors.GREEN)
    print_color(f"✅ 완료: {len(reviews)}개 리뷰 수집", Colors.GREEN)
    print_color(f"{'='*60}\n", Colors.GREEN)

    print("💡 다음 단계:")
    print(f"   Claude: '{output_path} 읽고 분석해줘'")
    if not args.sheet:
        print("   구글 시트: --sheet 옵션으로 업로드 가능")


if __name__ == "__main__":
    main()
