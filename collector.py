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
    prompt = f"""
당신은 세계 최고의 반도체 시장 분석가입니다. 다음 뉴스들을 정밀 분석해 주세요:
{combined_news}

[명령어]
1. 위 뉴스들의 논조를 5번 반복 검토하여 '긍정/부정/중립'의 비율(%)을 산출하세요.
2. 현재 반도체 가격(PPI)이 변동하는 근본적인 이유를 다음 3가지 관점에서 설명하세요:
   - 수요 측면 (AI 서버, 모바일, PC 등)
   - 공급 측면 (제조사 가동률, 재고, 기술 공정 등)
   - 대외 변수 (금리, 지정학적 리스크 등)

[출력 포맷]
- 종합 시장 감정 점수: (긍정 OO%, 부정 OO%, 중립 OO%)
- 핵심 요약: (1줄)
- 상세 변동 요인 분석: (위 3가지 관점 포함)
"""
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