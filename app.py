import streamlit as st
import os
import json
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="AI Data Archive Platform", layout="wide")

# 🌟 1. 카테고리 확장 구조 (향후 배터리, 바이오 등 추가 가능)
categories = {
    "💾 반도체 (Semiconductor)": "semiconductor",
    # "🔋 2차전지 (Battery)": "battery", # 나중에 추가할 때 주석만 해제하면 됩니다.
}

st.sidebar.title("📂 카테고리 선택")
selected_cat_name = st.sidebar.radio("데이터 주제를 선택하세요:", list(categories.keys()))
selected_folder = f"data/{categories[selected_cat_name]}"

# 🌟 2. 해당 카테고리의 폴더에서 날짜별 리포트 목록 불러오기
if os.path.exists(selected_folder):
    files = [f for f in os.listdir(selected_folder) if f.endswith('.json')]
    files.sort(reverse=True) # 최신 날짜가 맨 위에 오도록 내림차순 정렬
else:
    files = []

if not files:
    st.title("데이터 대기 중 ⏳")
    st.info("아직 이 카테고리에 수집된 데이터가 없습니다. 봇이 실행되기를 기다려주세요.")
else:
    # 사이드바에 날짜 선택 메뉴 생성
    st.sidebar.divider()
    st.sidebar.title("📅 리포트 날짜 선택")
    
    # 파일명(report_2026-04-06.json)에서 깔끔하게 날짜만 추출해서 딕셔너리로 만듦
    date_options = {f.replace("report_", "").replace(".json", ""): f for f in files}
    selected_date = st.sidebar.selectbox("열람할 날짜를 클릭하세요:", list(date_options.keys()))
    
    # 선택된 날짜의 JSON 파일 읽기
    file_to_read = os.path.join(selected_folder, date_options[selected_date])
    with open(file_to_read, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 🌟 3. 선택된 데이터로 메인 화면 그리기
    st.sidebar.divider()
    lang = st.sidebar.radio("🌐 Language / 언어", ["한국어", "English"])
    
    ui = {
        "한국어": {
            "title": f"📊 {selected_cat_name} 분석 리포트",
            "update": f"리포트 발행일: {selected_date} (데이터 수집: {data['last_updated']})",
            "ai_report": data.get('ai_report_ko', '데이터 오류')
        },
        "English": {
            "title": f"📊 {selected_cat_name} Analysis Report",
            "update": f"Report Date: {selected_date} (Collected: {data['last_updated']})",
            "ai_report": data.get('ai_report_en', 'Data Error')
        }
    }
    
    t = ui[lang]

    # --- 메인 화면 렌더링 ---
    st.title(t["title"])
    st.caption(t["update"])
    
    col1, col2 = st.columns([2, 1.5])
    
    with col1:
        st.subheader("📈 가격 지수 추이 (Price Index)")
        df = pd.DataFrame(list(data['price_history'].items()), columns=['Date', 'Price_Index'])
        df['Date'] = pd.to_datetime(df['Date'])
        df.sort_values('Date', inplace=True)
        df.set_index('Date', inplace=True)
        
        recent_df = df.tail(12)
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(recent_df.index, recent_df['Price_Index'], marker='o', color='royalblue')
        ax.grid(True, linestyle='--', alpha=0.7)
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig)
        
    with col2:
        st.subheader("🧠 AI Insight")
        st.markdown(t["ai_report"])
        
        with st.expander("🔗 Reference (데이터 출처)"):
            for src in data.get('news_sources', []):
                st.write(f"- [{src['title']}]({src['link']})")
            for src in data.get('paper_sources', []):
                st.write(f"- [{src['title']}]({src['link']})")