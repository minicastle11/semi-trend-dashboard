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

    print("4. Gemini AI 다국어(Ko/En) 앙상블 분석 시작...")
    genai.configure(api_key=GEMINI_API_KEY)
    
    # JSON 형태로 답변을 받기 위해 모델 설정 (안정성 강화)
    model = genai.GenerativeModel('gemini-2.5-flash', generation_config={"response_mime_type": "application/json"})
    # 앙상블 분석 및 심층 원인 파악을 위한 고도화된 프롬프트
    prompt = f"""
        당신은 세계 최고의 반도체 시장 분석가입니다. 다음 뉴스와 논문을 분석하세요.
        
        [뉴스]: {combined_news}
        [논문]: {combined_papers}

        [명령어]
        반드시 아래의 JSON 스키마에 맞춰 답변을 생성하세요. 
        'ko' 키에는 한국어 리포트를, 'en' 키에는 영어 리포트를 작성합니다.
        
        각 리포트는 반드시 다음 3가지 항목을 포함하는 마크다운 형식이어야 합니다:
        1. 시장 감정 종합 (앙상블): 5번 반복 시뮬레이션한 긍정/부정/중립 확률(%) (예: 🟢 긍정 60%, 🔴 부정 20%, 🟡 중립 20%)
        2. 핵심 트렌드 요약: 뉴스/논문을 결합한 2~3줄 요약
        3. 가격 변동 메커니즘: 수요 측면, 공급/기술 측면, 매크로 변수 측면에서의 심층 분석

        [⚠️ 매우 중요한 제약사항]
        JSON의 value(값) 부분에 마크다운을 작성할 때, 실제 줄바꿈(Enter)을 사용하지 마세요.
        반드시 줄바꿈 기호('\\n')와 탭 기호('\\t')를 사용하여 한 줄의 올바른 JSON 문자열 포맷으로 출력해야 합니다. 큰따옴표 안에는 큰따옴표를 직접 쓰지 말고 반드시 '\\"' 로 이스케이프 하세요.

        {{
            "ko": "### 🧠 AI 심층 분석 리포트\\n\\n#### 1. 시장 감정 종합\\n🟢 긍정 ...",
            "en": "### 🧠 AI In-depth Analysis Report\\n\\n#### 1. Market Sentiment\\n🟢 Positive ..."
        }}
        """
    try:
        ai_response_text = model.generate_content(prompt).text
        ai_reports = json.loads(ai_response_text) # AI가 준 JSON 텍스트를 파이썬 딕셔너리로 변환
    except Exception as e:
        print(f"AI 분석 중 오류: {e}")
        ai_reports = {"ko": "분석 오류", "en": "Analysis Error"}

    print("5. 결과물 결합 및 JSON 파일 저장 중...")
    result_data = {
        "last_updated": str(datetime.now()),
        "price_history": price_history,
        "news_sources": news_sources,
        "paper_sources": paper_sources,
        "ai_report_ko": ai_reports.get("ko", ""), 
        "ai_report_en": ai_reports.get("en", "")  
    }

    # 🌟 변경점: 데이터를 폴더별/날짜별로 누적 저장합니다.
    today_str = datetime.now().strftime("%Y-%m-%d")
    folder_path = "data/semiconductor" # 향후 'data/battery' 등으로 확장 가능
    
    # 폴더가 없으면 자동으로 생성
    os.makedirs(folder_path, exist_ok=True)
    
    # 파일명 예시: data/semiconductor/report_2026-04-06.json
    file_path = f"{folder_path}/report_{today_str}.json"

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(result_data, f, ensure_ascii=False, indent=4)
        
    print(f"✅ 모든 작업 완료! ({file_path} 생성됨)")

if __name__ == "__main__":
    collect_data()