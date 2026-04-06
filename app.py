import streamlit as st
import json
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="AI Semiconductor Dashboard", layout="wide")

try:
    with open("result.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        
    # 🌟 사이드바: 언어 선택 메뉴 추가
    st.sidebar.title("🌐 Language / 언어")
    lang = st.sidebar.radio("Select your language:", ["English", "한국어"])
    
    # 🌟 언어별 UI 텍스트 딕셔너리 설정
    ui = {
        "English": {
            "title": "📊 AI-Driven Global Semiconductor Supply Chain Dashboard",
            "update": f"🔄 Last Updated: {data['last_updated']}",
            "chart_title": "📈 US Semiconductor PPI (Last 12 Months)",
            "ai_title": "🧠 AI Ensemble Analysis Report",
            "ai_report": data.get('ai_report_en', 'Data not available.'),
            "source_title": "🔗 Data Sources (News & Papers)",
            "news_subtitle": "**📰 Top News**",
            "paper_subtitle": "**🔬 Latest arXiv Papers**"
        },
        "한국어": {
            "title": "📊 AI 기반 글로벌 반도체 공급망 대시보드",
            "update": f"🔄 마지막 업데이트: {data['last_updated']}",
            "chart_title": "📈 최근 1년 반도체 물가지수(PPI) 추이",
            "ai_title": "🧠 앙상블 AI 심층 분석 리포트",
            "ai_report": data.get('ai_report_ko', '데이터가 없습니다.'),
            "source_title": "🔗 데이터 출처 확인 (원문 링크)",
            "news_subtitle": "**📰 주요 뉴스 출처**",
            "paper_subtitle": "**🔬 최신 학술 논문(arXiv)**"
        }
    }
    
    # 선택된 언어의 텍스트 불러오기
    t = ui[lang]

    # 화면 렌더링 시작
    st.title(t["title"])
    st.caption(t["update"])
    
    col1, col2 = st.columns([2, 1.5])
    
    with col1:
        st.subheader(t["chart_title"])
        df = pd.DataFrame(list(data['price_history'].items()), columns=['Date', 'Price_Index'])
        df['Date'] = pd.to_datetime(df['Date'])
        df.sort_values('Date', inplace=True)
        df.set_index('Date', inplace=True)
        
        recent_df = df.tail(12)
        
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(recent_df.index, recent_df['Price_Index'], marker='o', color='royalblue', linewidth=2)
        ax.grid(True, linestyle='--', alpha=0.7)
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig)
        
    with col2:
        st.subheader(t["ai_title"])
        st.markdown(t["ai_report"]) # 선택한 언어의 AI 리포트 출력
        
        st.divider()
        
        with st.expander(t["source_title"]):
            st.markdown(t["news_subtitle"])
            for src in data.get('news_sources', []):
                st.write(f"- [{src['title']}]({src['link']})")
                
            st.markdown(t["paper_subtitle"])
            for src in data.get('paper_sources', []):
                st.write(f"- [{src['title']}]({src['link']})")
                
except FileNotFoundError:
    st.warning("No data found. Please run the backend script first. / 수집된 데이터가 없습니다.")