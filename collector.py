import os
import json
import urllib.request
import xml.etree.ElementTree as ET
from fredapi import Fred
import feedparser
import google.generativeai as genai
from datetime import datetime

# GitHub Actions에서 주입해 줄 환경 변수(API 키) 불러오기
# (로컬에서 테스트할 때는 os.environ.get 대신 본인 키를 직접 문자열로 넣고 테스트하세요)
FRED_API_KEY = os.environ.get("FRED_API_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

def collect_data():
    print("1. FRED 반도체 물가지수 데이터 수집 중...")
    fred = Fred(api_key=FRED_API_KEY)
    # 최근 24개월 데이터 수집
    semi_data = fred.get_series('PCU334413334413').tail(24) 
    # JSON 저장을 위해 날짜를 문자열로 변환
    price_history = {str(date.date()): value for date, value in semi_data.items()}

    print("2. 최신 글로벌 반도체 뉴스 수집 중...")
    rss_url = "https://news.google.com/rss/search?q=semiconductor+industry&hl=en-US&gl=US&ceid=US:en"
    feed = feedparser.parse(rss_url)
    # 출처 링크와 제목을 함께 딕셔너리로 저장 (대시보드 표시용)
    news_sources = [{"title": entry.title, "link": entry.link} for entry in feed.entries[:5]]
    # AI에게 먹일 텍스트 형태로 결합
    combined_news = "\n".join([f"- {src['title']}" for src in news_sources])

    print("3. 최신 반도체 학술 논문(arXiv) 수집 중...")
    arxiv_url = "http://export.arxiv.org/api/query?search_query=all:semiconductor&start=0&max_results=3&sortBy=submittedDate&sortOrder=descending"
    paper_sources = []
    
    try:
        # 실제 XML 파싱 로직 적용
        with urllib.request.urlopen(arxiv_url) as response:
            papers_xml = response.read().decode('utf-8')
            root = ET.fromstring(papers_xml)
            # arXiv XML의 네임스페이스 설정
            ns = {'atom': 'http://www.w3.org/2005/Atom'}
            
            for entry in root.findall('atom:entry', ns):
                # 제목에서 줄바꿈 제거 및 정리
                title = entry.find('atom:title', ns).text.strip().replace('\n', ' ')
                link = entry.find('atom:id', ns).text
                paper_sources.append({"title": title, "link": link})
    except Exception as e:
        print(f"논문 수집 중 에러 발생: {e}")
        paper_sources = [{"title": "논문 수집 일시 오류", "link": "#"}]
        
    combined_papers = "\n".join([f"- {src['title']}" for src in paper_sources])

    print("4. Gemini AI 앙상블 분석 시작...")
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    # 앙상블 분석 및 심층 원인 파악을 위한 고도화된 프롬프트
    prompt = f"""
    당신은 세계 최고의 반도체 시장 분석가입니다. 다음 수집된 뉴스 5건과 최신 논문 3건을 정밀 분석해 주세요.
    
    [최신 뉴스 헤드라인]
    {combined_news}
    
    [최신 학술 논문 동향]
    {combined_papers}

    [명령어 - 반드시 아래 양식에 맞춰 마크다운으로 작성할 것]
    1. **시장 감정 종합 (앙상블)**: 위 정보들의 논조를 5번 반복 시뮬레이션하여 '긍정/부정/중립'의 확률(%)을 도출하세요. (예: 🟢 긍정 60%, 🔴 부정 20%, 🟡 중립 20%)
    2. **핵심 트렌드 요약**: 뉴스 이슈와 논문 기술 동향을 결합하여 현재 가장 중요한 트렌드를 2~3줄로 요약하세요.
    3. **가격 변동 메커니즘 분석**: 현재 반도체 지수(PPI)가 변동하는 이유를 다음 3가지 관점에서 설명하세요.
       - 수요 측면 (AI, 모바일, PC 등 주요 수요처 동향)
       - 공급/기술 측면 (제조사 가동률, 재고, 신소재/공정 발전 등)
       - 매크로/대외 변수 (금리, 지정학적 리스크 등)
    """
    
    try:
        ai_response = model.generate_content(prompt).text
    except Exception as e:
        ai_response = f"AI 분석 중 오류가 발생했습니다: {e}"

    print("5. 결과물 결합 및 JSON 파일 저장 중...")
    result_data = {
        "last_updated": str(datetime.now()),
        "price_history": price_history,
        "news_sources": news_sources,      # 출처 링크 포함
        "paper_sources": paper_sources,    # 논문 링크 포함
        "ai_report": ai_response
    }

    with open("result.json", "w", encoding="utf-8") as f:
        json.dump(result_data, f, ensure_ascii=False, indent=4)
        
    print("✅ 모든 작업 완료! (result.json 생성됨)")

if __name__ == "__main__":
    collect_data()