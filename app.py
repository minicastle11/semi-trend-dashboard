import streamlit as st
import json
import pandas as pd
import matplotlib.pyplot as plt

# 페이지 기본 설정
st.set_page_config(page_title="AI 반도체 트렌드 대시보드", layout="wide")
st.title("📊 AI 기반 글로벌 반도체 공급망 대시보드")

try:
    # API 호출 없이 JSON 파일만 읽어옵니다. (로딩 속도 0.1초)
    with open("result.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        
    st.caption(f"🔄 마지막 데이터 업데이트: {data['last_updated']}")
    
    # 화면을 2개의 컬럼으로 분할
    col1, col2 = st.columns([2, 1.5])
    
    with col1:
        st.subheader("📈 최근 1년 반도체 물가지수(PPI) 추이")
        
        # 딕셔너리를 DataFrame으로 변환 및 정렬
        df = pd.DataFrame(list(data['price_history'].items()), columns=['Date', 'Price_Index'])
        df['Date'] = pd.to_datetime(df['Date'])
        df.sort_values('Date', inplace=True)
        df.set_index('Date', inplace=True)
        
        # 시인성을 위해 최근 12개월치 데이터만 슬라이싱
        recent_df = df.tail(12)
        
        # 그래프 그리기
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(recent_df.index, recent_df['Price_Index'], marker='o', color='royalblue', linewidth=2, label='US Semi PPI')
        
        ax.set_title("Semiconductor Producer Price Index (Last 12 Months)")
        ax.set_ylabel("Price Index")
        ax.grid(True, linestyle='--', alpha=0.7)
        plt.xticks(rotation=45) # 날짜 글씨 겹치지 않게 45도 기울이기
        plt.tight_layout()
        st.pyplot(fig)
        
    with col2:
        st.subheader("🧠 앙상블 AI 심층 분석 리포트")
        st.info("💡 **AI 5회 반복 시뮬레이션 결과 및 변동 원인 분석**")
        
        # AI 분석 텍스트 출력
        st.markdown(data['ai_report'])
        
        st.divider() # 시각적 구분선
        
        # 출처 링크 토글 (아코디언 형태)
        with st.expander("🔗 데이터 출처 확인 (원문 링크)"):
            st.markdown("**📰 주요 뉴스 출처**")
            for src in data.get('news_sources', []):
                st.write(f"- [{src['title']}]({src['link']})")
                
            st.markdown("**🔬 최신 학술 논문(arXiv)**")
            for src in data.get('paper_sources', []):
                st.write(f"- [{src['title']}]({src['link']})")
                
except FileNotFoundError:
    st.warning("아직 수집된 데이터(result.json)가 없습니다. 백엔드 스크립트를 먼저 실행해주세요.")