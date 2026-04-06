import os
import json
from fredapi import Fred
import feedparser
import google.generativeai as genai
from datetime import datetime

# GitHub Actions에서 주입해 줄 환경 변수(API 키) 불러오기
FRED_API_KEY = os.environ.get("FRED_API_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

def collect_data():
    print("1. FRED 데이터 수집 시작...")
    fred = Fred(api_key=FRED_API_KEY)
    semi_data = fred.get_series('PCU334413334413').tail(24) # 최근 2년치만
    
    # JSON 저장을 위해 날짜를 문자열로 변환하고 딕셔너리로 만듦
    price_history = {str(date.date()): value for date, value in semi_data.items()}

    print("2. 뉴스 수집 및 AI 분석 시작...")
    rss_url = "https://news.google.com/rss/search?q=semiconductor+industry&hl=en-US&gl=US&ceid=US:en"
    feed = feedparser.parse(rss_url)
    
    news_titles = [f"{i+1}. {entry.title}" for i, entry in enumerate(feed.entries[:5])]
    combined_news = "\n".join(news_titles)
    
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-2.5-flash')
    prompt = f"다음 반도체 뉴스 5개를 바탕으로 시장 감정(긍정/부정/중립)과 3줄 요약을 마크다운으로 작성해 줘:\n{combined_news}"
    
    ai_response = model.generate_content(prompt).text
    
    # 3. 수집한 모든 데이터를 하나의 딕셔너리로 묶기
    result_data = {
        "last_updated": str(datetime.now()),
        "price_history": price_history,
        "ai_report": ai_response,
        "raw_news": combined_news
    }

    # 4. result.json 이라는 파일로 덮어쓰기 저장
    with open("result.json", "w", encoding="utf-8") as f:
        json.dump(result_data, f, ensure_ascii=False, indent=4)
    print("✅ 데이터 수집 및 저장 완료 (result.json)")

if __name__ == "__main__":
    collect_data()