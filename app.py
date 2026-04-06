import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from fredapi import Fred
from statsmodels.tsa.arima.model import ARIMA
import feedparser
import google.generativeai as genai
import warnings

warnings.filterwarnings('ignore')

# --- API 키 설정 (본인의 키로 변경하세요!) ---
FRED_API_KEY = st.secrets["FRED_API_KEY"]
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]

# 웹 페이지 기본 설정
st.set_page_config(page_title="AI 반도체 트렌드 대시보드", layout="wide")
st.title("📊 AI 기반 글로벌 반도체 공급망 대시보드")
st.markdown("과거 물가지수 기반의 **가격 예측(ARIMA)**과 최신 뉴스의 **AI 감정 분석**을 통합한 리포트입니다.")

# 화면을 두 개의 컬럼으로 나누기
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📈 1. 반도체 물가지수 추이 및 3개월 예측")
    
    with st.spinner("데이터를 불러오고 예측 모델을 구동 중입니다... (약 10초 소요)"):
        # FRED 데이터 불러오기
        fred = Fred(api_key=FRED_API_KEY)
        semi_data = fred.get_series('PCU334413334413')
        df = pd.DataFrame(semi_data, columns=['Semi_Price_Index'])
        df.index.name = 'Date'
        
        # ARIMA 예측 모델 구동
        model = ARIMA(df['Semi_Price_Index'], order=(1, 1, 1))
        model_fit = model.fit()
        forecast_steps = 3
        forecast = model_fit.forecast(steps=forecast_steps)
        
        last_date = df.index[-1]
        forecast_dates = pd.date_range(start=last_date, periods=forecast_steps + 1, freq='MS')[1:]
        forecast.index = forecast_dates
        
        # 그래프 그리기
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(df.index[-24:], df['Semi_Price_Index'][-24:], label='Historical Data (Last 2 Years)', marker='o') # 최근 2년치만 보여주기
        ax.plot(forecast.index, forecast, label='Forecast (Next 3 Months)', color='red', marker='x', linestyle='--')
        ax.set_title('US Semiconductor PPI & Forecast')
        ax.grid(True)
        ax.legend()
        
        # 스트림릿 화면에 그래프 띄우기
        st.pyplot(fig)

with col2:
    st.subheader("📰 2. 실시간 AI 시장 감정 분석")
    
    with st.spinner("글로벌 뉴스를 수집하고 AI가 분석 중입니다..."):
        # 뉴스 수집
        rss_url = "https://news.google.com/rss/search?q=semiconductor+industry&hl=en-US&gl=US&ceid=US:en"
        feed = feedparser.parse(rss_url)
        
        news_titles = []
        for i, entry in enumerate(feed.entries[:5]):
            news_titles.append(f"{i+1}. {entry.title}")
        combined_news = "\n".join(news_titles)
        
        # Gemini AI 분석
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt = f"""
        다음은 오늘자 글로벌 반도체 산업 관련 최신 뉴스 헤드라인 5개입니다:
        {combined_news}

        위 기사들을 바탕으로 다음 사항을 작성해 줘. 마크다운 포맷을 사용해 깔끔하게 정리해 줘:
        - **시장 감정:** (긍정 🟢 / 부정 🔴 / 중립 🟡 중 택 1)
        - **핵심 이슈 3줄 요약:**
        """
        
        try:
            response = model.generate_content(prompt)
            st.info("💡 **AI 분석 리포트**")
            st.markdown(response.text)
            
            with st.expander("원문 뉴스 헤드라인 보기"):
                st.write(combined_news)
        except Exception as e:
            st.error(f"AI 분석 중 오류 발생: {e}")