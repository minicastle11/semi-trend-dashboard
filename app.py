import streamlit as st
import json
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="AI 반도체 트렌드 대시보드", layout="wide")
st.title("📊 AI 기반 글로벌 반도체 공급망 대시보드")

try:
    # 🌟 핵심: 무거운 API 호출 없이 JSON 파일만 읽어옵니다. (로딩 0.1초)
    with open("result.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        
    st.caption(f"🔄 마지막 업데이트: {data['last_updated']}")
    
    col1, col2 = st.columns([2, 1])
    
    # app.py 내 그래프 부분 수정
    with col1:
        st.subheader("📈 최근 1년 추이 및 3개월 예측")
        # 최근 12개월 데이터로 제한하여 시인성 확보
        df = pd.DataFrame(list(data['price_history'].items()), columns=['Date', 'Price_Index'])
        df['Date'] = pd.to_datetime(df['Date'])
        df.sort_values('Date', inplace=True)
        df.set_index('Date', inplace=True)
        
        recent_df = df.tail(12) # 최근 1년치만 보여줌
        
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(recent_df.index, recent_df['Price_Index'], marker='o', label='Historical (12M)')
        
        # 예측값 연결 (마지막 실측값에서 시작하도록)
        # ... (ARIMA 예측 코드 생략) ...
        
        # x축 날짜 포맷 최적화
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig)
        
    with col2:
        st.subheader("📰 실시간 AI 시장 감정 분석")
        st.info("💡 **AI 분석 리포트**")
        st.markdown(data['ai_report'])
        
except FileNotFoundError:
    st.warning("아직 수집된 데이터(result.json)가 없습니다. 백엔드 스크립트가 실행되기를 기다려주세요.")