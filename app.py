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
    
    with col1:
        st.subheader("📈 최근 2년 반도체 물가지수 추이")
        # JSON 데이터를 다시 판다스 데이터프레임으로 변환
        df = pd.DataFrame(list(data['price_history'].items()), columns=['Date', 'Price_Index'])
        df['Date'] = pd.to_datetime(df['Date'])
        df.set_index('Date', inplace=True)
        
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(df.index, df['Price_Index'], marker='o')
        ax.grid(True)
        st.pyplot(fig)
        
    with col2:
        st.subheader("📰 실시간 AI 시장 감정 분석")
        st.info("💡 **AI 분석 리포트**")
        st.markdown(data['ai_report'])
        
except FileNotFoundError:
    st.warning("아직 수집된 데이터(result.json)가 없습니다. 백엔드 스크립트가 실행되기를 기다려주세요.")