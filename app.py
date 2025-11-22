import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# -----------------------------------------------------------------------------
# 1. 페이지 기본 설정 및 스타일
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="NASDAQ Growth & Liquidity Tracker",
    page_icon="📈",
    layout="wide"
)

# 스타일 커스터마이징 (CSS)
st.markdown("""
    <style>
    .big-font { font-size:20px !important; font-weight: bold; }
    .metric-card { background-color: #f0f2f6; padding: 15px; border-radius: 10px; border-left: 5px solid #4e8cff; }
    </style>
    """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. 데이터 생성 (Mock Data)
# 실제로는 yfinance나 Alpha Vantage API 등을 연동해야 하지만,
# 구조를 보여주기 위해 나스닥 상위 기업 느낌의 가상 데이터를 생성합니다.
# -----------------------------------------------------------------------------
@st.cache_data
def load_data():
    tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'TSLA', 'META', 'AVGO', 'PEP', 'COST',
               'CSCO', 'TMUS', 'ADBE', 'TXN', 'CMCSA', 'AMGN', 'NFLX', 'QCOM', 'SBUX', 'INTC',
               'AMD', 'INTU', 'HON', 'IBM', 'GE', 'AMAT', 'BKNG', 'ISRG', 'GILD', 'MDLZ']
    
    data = []
    np.random.seed(42)
    
    for ticker in tickers:
        # 성장 지표 (Growth)
        eps_growth = np.random.normal(15, 10)  # 예상 EPS 성장률 (%)
        rev_growth = np.random.normal(12, 8)   # 매출 성장률 (%)
        tam_penetration = np.random.randint(10, 90) # 시장 침투율 (%)
        
        # 유동성/밸류에이션 지표 (Liquidity)
        pe_ratio = np.random.normal(30, 15)    # PER (유동성이 높을수록 고평가 경향)
        pe_ratio = max(pe_ratio, 5)            # 최소값 보정
        volume_change = np.random.normal(0, 20) # 거래량 변동률 (%)
        momentum = np.random.uniform(-10, 30)   # 최근 주가 모멘텀 (%)
        
        market_cap = np.random.randint(100, 3000) # 시가총액 (Billion $)
        
        # 섹터 및 트렌드 키워드 할당
        if ticker in ['NVDA', 'AMD', 'MSFT', 'GOOGL']:
            sector = "AI & Cloud"
            tags = ["#AI", "#DataCenter", "#Generative"]
        elif ticker in ['AAPL', 'TSLA', 'AMZN']:
            sector = "Consumer Tech"
            tags = ["#Platform", "#Ecosystem", "#Loyalty"]
        else:
            sector = "Others"
            tags = ["#Stable", "#Dividend"]

        data.append({
            "Ticker": ticker,
            "Sector": sector,
            "Market_Cap_B": market_cap,
            "PE_Ratio": round(pe_ratio, 2),          # X축: 유동성/가격
            "Growth_Score": round((eps_growth + rev_growth)/2, 2), # Y축: 성장성
            "EPS_Growth": round(eps_growth, 2),
            "Revenue_Growth": round(rev_growth, 2),
            "PEG_Ratio": round(pe_ratio / max(eps_growth, 0.1), 2), # 성장 대비 가격
            "Momentum": round(momentum, 2),
            "Volume_Change": round(volume_change, 1),
            "TAM_Penetration": tam_penetration,
            "Tags": tags
        })
        
    return pd.DataFrame(data)

df = load_data()

# -----------------------------------------------------------------------------
# 3. 상단 헤더 & 매크로 환경 (Macro Environment)
# -----------------------------------------------------------------------------
st.title("📈 NASDAQ Top 30: Growth vs Liquidity Map")
st.markdown("### *\"가격은 유동성이 결정하고, 바닥은 성장이 지지한다.\"*")

# 매크로 신호등 (가상 데이터)
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("미국 10년물 국채금리", "4.25%", "+0.05% (유동성 축소)")
with col2:
    st.metric("나스닥 변동성(VIX)", "14.5", "-2.1% (심리 안정)")
with col3:
    st.metric("시장 유동성 점수", "65/100", "Neutral")
with col4:
    st.markdown("""
    <div style='background-color:#d4edda; padding:10px; border-radius:5px; color:#155724; text-align:center;'>
        <b>Macro Status: ☁️ 흐림 뒤 갬</b><br>금리 인하 기대감 유효
    </div>
    """, unsafe_allow_html=True)

st.divider()

# -----------------------------------------------------------------------------
# 4. 메인 대시보드: The Map (Scatter Plot)
# -----------------------------------------------------------------------------
col_main, col_sidebar = st.columns([3, 1])

with col_main:
    st.subheader("📍 Market Map: 성장성(Y) vs 밸류에이션(X)")
    
    # Plotly Scatter Plot
    fig = px.scatter(
        df,
        x="PE_Ratio", 
        y="Growth_Score",
        size="Market_Cap_B",
        color="Momentum",
        text="Ticker",
        hover_name="Ticker",
        hover_data=["EPS_Growth", "PEG_Ratio", "Sector"],
        color_continuous_scale="RdBu_r", # 빨간색이 상승(Hot), 파란색이 하락(Cool)
        title="버블 크기: 시가총액 | 색상: 최근 모멘텀",
        labels={"PE_Ratio": "유동성/밸류에이션 (PER)", "Growth_Score": "종합 성장 점수 (Growth)"}
    )
    
    # Magic Zone 등 기준선 추가
    fig.add_hline(y=15, line_dash="dash", line_color="green", annotation_text="고성장 기준선")
    fig.add_vline(x=30, line_dash="dash", line_color="orange", annotation_text="고평가 경계선")
    
    # 배경 구역 표시 (Shape) - 직관적 이해
    fig.add_shape(type="rect", x0=0, y0=15, x1=30, y1=50, 
                  fillcolor="green", opacity=0.1, line_width=0)
    fig.add_annotation(x=15, y=40, text="💎 Magic Zone (고성장/저평가)", showarrow=False)
    
    fig.update_layout(height=600)
    st.plotly_chart(fig, use_container_width=True)

with col_sidebar:
    st.subheader("🔍 필터링 & 리스트")
    sector_filter = st.multiselect("섹터 선택", df['Sector'].unique(), default=df['Sector'].unique())
    
    filtered_df = df[df['Sector'].isin(sector_filter)].sort_values(by="Market_Cap_B", ascending=False)
    
    st.dataframe(
        filtered_df[['Ticker', 'PE_Ratio', 'Growth_Score', 'PEG_Ratio']],
        hide_index=True,
        use_container_width=True,
        height=500
    )

st.divider()

# -----------------------------------------------------------------------------
# 5. 상세 페이지: Growth Engine & Liquidity Flow
# -----------------------------------------------------------------------------
st.subheader("🔬 개별 기업 심층 분석 (The Growth Engine)")

selected_ticker = st.selectbox("분석할 기업을 선택하세요:", df['Ticker'].unique(), index=4) # Default NVDA
company_data = df[df['Ticker'] == selected_ticker].iloc[0]

# 3단 탭 구성
tab1, tab2, tab3 = st.tabs(["📊 1. 정량적 성장 (Numbers)", "🔭 2. 정성적 성장 (Story)", "🌊 3. 유동성 & 수급 (Liquidity)"])

# --- Tab 1: 정량적 지표 ---
with tab1:
    c1, c2, c3 = st.columns(3)
    
    # PEG Ratio 시각화 (핵심)
    peg = company_data['PEG_Ratio']
    peg_color = "green" if peg < 1.5 else "orange" if peg < 2.5 else "red"
    c1.markdown(f"""
        <div class="metric-card">
            <h4>PEG Ratio (성장 가성비)</h4>
            <h2 style='color:{peg_color}'>{peg}</h2>
            <p>1.0 미만: 저평가 / 2.0 초과: 고평가<br>
            PER {company_data['PE_Ratio']} ÷ 성장률 {company_data['EPS_Growth']}%</p>
        </div>
    """, unsafe_allow_html=True)
    
    c2.metric("EPS 성장률 (이익)", f"{company_data['EPS_Growth']}%", "기초 체력")
    c3.metric("매출 성장률 (외형)", f"{company_data['Revenue_Growth']}%", "시장 확대")
    
    # 가상 차트: 실적 추이
    st.markdown("#### 📈 주가 vs EPS 추이 (Trend)")
    dates = pd.date_range(start='2023-01-01', periods=12, freq='M')
    fake_stock = np.cumsum(np.random.randn(12) + 1) * 10 + 100
    fake_eps = np.linspace(1, 1.5, 12) * (fake_stock/100)
    
    chart_df = pd.DataFrame({'Date': dates, 'Price': fake_stock, 'EPS': fake_eps})
    
    line_fig = go.Figure()
    line_fig.add_trace(go.Scatter(x=chart_df['Date'], y=chart_df['Price'], name='주가 (Price)', yaxis='y1'))
    line_fig.add_trace(go.Scatter(x=chart_df['Date'], y=chart_df['EPS'], name='주당순이익 (EPS)', yaxis='y2', line=dict(dash='dot')))
    
    line_fig.update_layout(
        yaxis=dict(title='Price'),
        yaxis2=dict(title='EPS', overlaying='y', side='right'),
        hovermode="x unified"
    )
    st.plotly_chart(line_fig, use_container_width=True)

# --- Tab 2: 정성적 지표 ---
with tab2:
    col_story, col_moat = st.columns([1, 1])
    
    with col_story:
        st.markdown("#### 🏷️ 핵심 성장 키워드")
        tags_html = "".join([f"<span style='background:#e0e0e0; padding:5px 10px; border-radius:15px; margin-right:5px;'>{tag}</span>" for tag in company_data['Tags']])
        st.markdown(tags_html, unsafe_allow_html=True)
        
        st.markdown("#### 🚀 미래 성장 동력 (New Capex)")
        st.info(f"이 기업은 **{company_data['Sector']}** 분야에서 주도권을 잡기 위해 공격적인 투자를 진행 중입니다.")
    
    with col_moat:
        st.markdown("#### 🌏 TAM 침투율 (남은 성장 여력)")
        penetration = company_data['TAM_Penetration']
        st.progress(penetration / 100)
        st.caption(f"현재 시장 침투율: {penetration}% (아직 {100-penetration}%의 시장이 남아있습니다)")
        
        st.markdown("#### 🏰 경제적 해자 (Moat)")
        st.text_area("Analyst Note", "강력한 브랜드 파워와 네트워크 효과를 보유하고 있어 가격 결정력(Pricing Power)이 높음.", disabled=True)

# --- Tab 3: 유동성 지표 ---
with tab3:
    l1, l2 = st.columns(2)
    
    with l1:
        st.metric("최근 거래량 변동", f"{company_data['Volume_Change']}%", "수급 강도")
        st.bar_chart(np.random.randint(50, 150, 10)) # 가상 최근 10일 거래량
        st.caption("최근 10일 거래량 추이")
        
    with l2:
        st.markdown("#### 🌡️ 시장 심리 (Sentiment)")
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = company_data['Momentum'] + 50, # 0~100 스케일로 변환 가정
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Momentum Score"},
            gauge = {'axis': {'range': [0, 100]},
                     'bar': {'color': "darkblue"},
                     'steps': [
                         {'range': [0, 30], 'color': "lightgray"},
                         {'range': [30, 70], 'color': "gray"},
                         {'range': [70, 100], 'color': "lightblue"}]}))
        fig_gauge.update_layout(height=250)
        st.plotly_chart(fig_gauge, use_container_width=True)

# -----------------------------------------------------------------------------
# 6. Action Card (최종 요약)
# -----------------------------------------------------------------------------
st.divider()
st.subheader(f"📢 Action Plan for {selected_ticker}")

# 간단한 로직에 따른 코멘트 생성
score_g = company_data['Growth_Score']
score_l = company_data['Momentum']

if score_g > 20 and company_data['PEG_Ratio'] < 1.5:
    action = "STRONG BUY (강력 매수)"
    desc = "성장성은 폭발적인데 가격은 아직 저렴합니다. 유동성이 붙기 시작하면 급등할 수 있습니다."
    color = "#d4edda" # Green
elif score_g > 15 and company_data['PEG_Ratio'] > 2.5:
    action = "HOLD (관망/분할 매수)"
    desc = "훌륭한 기업이지만 유동성이 과하게 쏠려 비쌉니다. 조정 시 매수를 고려하세요."
    color = "#fff3cd" # Yellow
else:
    action = "WATCH (관찰 필요)"
    desc = "성장 동력이 약화되었거나, 모멘텀이 부족합니다."
    color = "#f8d7da" # Red

st.markdown(f"""
<div style='background-color:{color}; padding:20px; border-radius:10px; text-align:center; border: 1px solid gray;'>
    <h2 style='margin:0;'>{action}</h2>
    <p style='font-size:18px; margin-top:10px;'>{desc}</p>
</div>
""", unsafe_allow_html=True)