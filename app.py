import streamlit as st
import requests
import pandas as pd
import sqlite3
import os
from datetime import datetime
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 페이지 설정
st.set_page_config(
    page_title="대출 상품 운영 대시보드",
    page_icon="💳",
    layout="wide"
)

# 스타일
st.markdown("""
<style>
    @import url('https://cdn.jsdelivr.net/npm/pretendard@1.3.9/dist/web/static/pretendard.min.css');
    
    /* 로딩 프로그레스 바 */
    .stProgress > div > div > div > div {
        background-image: linear-gradient(90deg, #fee500, #fee500) !important;
        background-color: #fee500 !important;
    }

    .stSpinner > div {
        border-top-color: #fee500 !important;
    }

    div[data-testid="stDecoration"] {
        background-image: linear-gradient(90deg, #fee500, #fee500) !important;
    }

    header[data-testid="stHeader"] {
        background: transparent !important;
    }
            
    :root {
        --bg: #ffffff;
        --bg-secondary: #f9fafb;
        --border: #e5e7eb;
        --text: #111827;
        --text-secondary: #6b7280;
        --text-muted: #9ca3af;
        --accent: #fee500;
        --success: #10b981;
        --error: #ef4444;
        --info: #3b82f6;
    }
    
    .stApp {
        background: var(--bg);
    }
    
    .block-container {
        max-width: 1100px;
        padding: 48px 24px;
    }
        
    /* 헤더 */
    .header {
        margin-bottom: 40px;
    }
    .header-top {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 8px;
    }
    .logo-icon {
        width: 32px;
        height: 32px;
        background: var(--accent);
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 14px;
    }
    .header-title {
        font-size: 24px;
        font-weight: 700;
        color: var(--text);
        letter-spacing: -0.5px;
    }
    .header-desc {
        color: var(--text-secondary);
        font-size: 15px;
    }
    
    /* 상태코드 가이드 */
    .status-guide {
        display: flex;
        gap: 24px;
        padding: 14px 20px;
        background: var(--bg-secondary);
        border-radius: 8px;
        margin-bottom: 32px;
        font-size: 13px;
        flex-wrap: wrap;
    }
    .status-item {
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .status-code {
        font-family: 'SF Mono', monospace;
        font-weight: 600;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 12px;
    }
    .code-200 { background: #d1fae5; color: #065f46; }
    .code-400 { background: #fef3c7; color: #92400e; }
    .code-401 { background: #fee2e2; color: #991b1b; }
    .code-500 { background: #fce7f3; color: #9d174d; }
    .status-desc { color: var(--text-muted); }
    
    /* 시나리오 배너 */
    .scenario-banner {
        padding: 16px 20px;
        background: var(--bg-secondary);
        border-radius: 8px;
        margin-bottom: 24px;
        font-size: 14px;
    }
    .scenario-banner.error {
        background: #fef2f2;
    }
    .scenario-label {
        font-size: 14px;
        font-weight: 600;
        color: var(--info);
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 4px;
    }
    .scenario-label.error {
        color: var(--error);
    }
    .scenario-text {
        color: var(--text-secondary);
        line-height: 1.7;
    }
    
    /* API 응답 정보 */
    .response-info {
        display: flex;
        gap: 24px;
        padding: 14px 20px;
        background: var(--bg-secondary);
        border-radius: 8px;
        margin: 16px 0;
        font-size: 13px;
    }
    .response-info.error {
        background: #fef2f2;
    }
    .response-item {
        display: flex;
        gap: 8px;
    }
    .response-label {
        color: var(--text-muted);
    }
    .response-value {
        font-weight: 600;
        color: var(--text);
    }
    .response-value.success { color: var(--success); }
    .response-value.error { color: var(--error); }
    
    /* API 코드박스 */
    .api-code-box {
        background: #1e1e1e;
        border-radius: 8px;
        padding: 16px 20px;
        margin: 16px 0;
        font-family: 'SF Mono', Monaco, monospace;
        font-size: 13px;
        color: #d4d4d4;
        overflow-x: auto;
    }
    .api-method { color: #22c55e; font-weight: 600; }
    .api-url { color: #e4e4e7; }
    
    /* 필터 카드 (새 디자인) */
    .filter-wrap {
        display: flex;
        gap: 12px;
        margin: 20px 0;
    }
    .filter-item {
        flex: 1;
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 16px 20px;
        background: #fff;
        border: 1px solid var(--border);
        border-radius: 12px;
        transition: all 0.15s;
    }
    .filter-item.active {
        border-color: var(--text);
        box-shadow: 0 0 0 1px var(--text);
    }
    .filter-item .dot {
        width: 10px;
        height: 10px;
        border-radius: 50%;
        flex-shrink: 0;
    }
    .filter-item .dot.gray { background: #9ca3af; }
    .filter-item .dot.green { background: #22c55e; }
    .filter-item .dot.yellow { background: #eab308; }
    .filter-item .dot.red { background: #ef4444; }
    .filter-item .info {
        display: flex;
        flex-direction: column;
    }
    .filter-item .num {
        font-size: 24px;
        font-weight: 700;
        color: var(--text);
        line-height: 1;
        font-family: 'Pretendard', -apple-system, sans-serif;
    }
    .filter-item .label {
        font-size: 13px;
        color: var(--text-muted);
        margin-top: 2px;
    }
    
    /* 에러 박스 */
    .error-box {
        padding: 16px 20px;
        background: #fef2f2;
        border: 1px solid #fecaca;
        border-radius: 8px;
        margin-top: 16px;
    }
    .error-title {
        font-weight: 600;
        color: #991b1b;
        margin-bottom: 8px;
    }
    .error-text {
        font-size: 14px;
        color: #7f1d1d;
        line-height: 1.7;
    }
    
    /* 성공 박스 */
    .success-box {
        padding: 16px 20px;
        background: #ecfdf5;
        border: 1px solid #a7f3d0;
        border-radius: 8px;
        color: #065f46;
        font-size: 14px;
    }
    
    /* 탭 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        border-bottom: 1px solid var(--border);
        background: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 12px 20px;
        font-size: 14px;
        font-weight: 500;
        color: var(--text-secondary);
        background: transparent;
        border: none;
        border-bottom: 2px solid transparent;
        margin-bottom: -1px;
    }
    .stTabs [aria-selected="true"] {
        color: #111827 !important;
        background: transparent !important;
        border-bottom: 2px solid #fee500 !important;
    }
    
    /* 버튼 */
    .stButton > button {
        background: var(--text) !important;
        color: var(--bg) !important;
        font-weight: 600 !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 10px 20px !important;
        font-size: 14px !important;
    }
    .stButton > button:hover {
        background: #374151 !important;
    }
            
    /* 폼 */
    .stSelectbox > div > div,
    .stTextInput > div > div > input {
        border: 1px solid var(--border) !important;
        border-radius: 6px !important;
        font-size: 14px !important;
    }
    .stSelectbox > div > div:focus-within,
    .stTextInput > div > div > input:focus {
        border-color: var(--text) !important;
    }
    
    /* 라벨 */
    .stSelectbox label, .stTextInput label, .stNumberInput label {
        font-size: 13px !important;
        font-weight: 500 !important;
        color: var(--text-secondary) !important;
    }
    
    /* 테이블 */
    .stDataFrame {
        border: 1px solid var(--border);
        border-radius: 8px;
    }
    
    /* 푸터 */
    .footer {
        text-align: center;
        padding: 48px 0 24px;
        color: var(--text-muted);
        font-size: 13px;
    }
    
    /* 섹션 타이틀 */
    .section-title {
        font-size: 16px;
        font-weight: 600;
        color: var(--text);
        margin-bottom: 16px;
    }
            
    /* 라디오 숨기기 */
    div[data-testid="stRadio"] {
        height: 1px;
        overflow: hidden;
        opacity: 0;
        margin: 0;
        padding: 0;
    }
</style>
""", unsafe_allow_html=True)

# 환경변수
API_KEY = os.getenv("FSS_API_KEY", "")
BASE_URL = "https://finlife.fss.or.kr/finlifeapi"

ENDPOINTS = {
    "주택담보대출": "mortgageLoanProductsSearch",
    "전세자금대출": "rentHouseLoanProductsSearch", 
    "개인신용대출": "creditLoanProductsSearch"
}

# DB
def init_db():
    conn = sqlite3.connect("loan_products.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fin_co_no TEXT,
            kor_co_nm TEXT,
            fin_prdt_cd TEXT,
            fin_prdt_nm TEXT,
            loan_type TEXT,
            lend_rate_min REAL,
            lend_rate_max REAL,
            loan_lmt TEXT,
            dcls_month TEXT,
            created_at TEXT,
            updated_at TEXT,
            UNIQUE(fin_co_no, fin_prdt_cd, loan_type)
        )
    """)
    conn.commit()
    return conn

def fetch_loan_products(loan_type, top_fin_grp_no="020000"):
    endpoint = ENDPOINTS.get(loan_type, "mortgageLoanProductsSearch")
    url = f"{BASE_URL}/{endpoint}.json"
    params = {"auth": API_KEY, "topFinGrpNo": top_fin_grp_no, "pageNo": 1}
    
    try:
        response = requests.get(url, params=params, timeout=10, verify=False)
        response.raise_for_status()
        return response.json(), response.elapsed.total_seconds() * 1000, response.status_code
    except requests.exceptions.Timeout:
        return {"error": "Timeout"}, 0, 408
    except requests.exceptions.HTTPError as e:
        return {"error": str(e)}, 0, e.response.status_code if e.response else 500
    except Exception as e:
        return {"error": str(e)}, 0, 500

def get_products_from_db(conn, filters=None):
    query = "SELECT * FROM products"
    if filters:
        conditions = []
        if filters.get("loan_type"):
            conditions.append(f"loan_type = '{filters['loan_type']}'")
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
    return pd.read_sql_query(query, conn)

def save_products_to_db(conn, products_df, loan_type):
    c = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    saved = 0
    for _, row in products_df.iterrows():
        try:
            c.execute("""
                INSERT OR REPLACE INTO products 
                (fin_co_no, kor_co_nm, fin_prdt_cd, fin_prdt_nm, loan_type, 
                 lend_rate_min, lend_rate_max, loan_lmt, dcls_month, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                row.get("금융회사코드", ""), row.get("금융회사", ""), row.get("상품코드", ""),
                row.get("상품명", ""), loan_type, row.get("최저금리"), row.get("최고금리"),
                row.get("대출한도", ""), row.get("공시월", ""), now, now
            ))
            saved += 1
        except:
            pass
    conn.commit()
    return saved

def api_to_dataframe(data, loan_type):
    result = data.get("result", {})
    base_list = result.get("baseList", [])
    option_list = result.get("optionList", [])
    
    option_map = {}
    for opt in option_list:
        cd = opt.get("fin_prdt_cd", "")
        if cd not in option_map:
            option_map[cd] = []
        option_map[cd].append(opt)
    
    rows = []
    for base in base_list:
        cd = base.get("fin_prdt_cd", "")
        opts = option_map.get(cd, [])
        rate_min = rate_max = None
        if opts:
            mins = [o.get("lend_rate_min") for o in opts if o.get("lend_rate_min")]
            maxs = [o.get("lend_rate_max") for o in opts if o.get("lend_rate_max")]
            if mins: rate_min = min(mins)
            if maxs: rate_max = max(maxs)
        
        rows.append({
            "금융회사코드": base.get("fin_co_no", ""),
            "금융회사": base.get("kor_co_nm", ""),
            "상품명": base.get("fin_prdt_nm", ""),
            "상품코드": cd,
            "유형": loan_type,
            "최저금리": rate_min,
            "최고금리": rate_max,
            "대출한도": base.get("loan_lmt", ""),
            "공시월": base.get("dcls_month", "")
        })
    return pd.DataFrame(rows)

# 메인
def main():
    # 헤더
    st.markdown("""
    <div class="header">
        <div class="header-top">
            <div class="logo-icon">K</div>
            <div class="header-title">대출 상품 운영 대시보드</div>
        </div>
        <div class="header-desc">대출 제휴사 API 데이터 조회 · 검증 · 등록</div>
    </div>
    """, unsafe_allow_html=True)
    
    if not API_KEY:
        st.error("⚠️ API 키가 설정되지 않았습니다. 환경변수 `FSS_API_KEY`를 설정해주세요.")
        st.stop()
    
    conn = init_db()
    
    tab1, tab2, tab3, tab4 = st.tabs(["신규 제휴사 연동", "금리 변경 반영", "장애 대응", "DB 관리"])
    
    # ==================== 탭 1 ====================
    with tab1:
        st.markdown("""
        <div class="scenario-banner">
            <div class="scenario-label">시나리오</div>
            <div class="scenario-text">
                <strong>상황:</strong> 새로운 금융사와 제휴를 맺었습니다. 금감원에 공시된 상품 정보를 가져와서 DB에 등록합니다.<br>
                <strong>할 일:</strong> 금감원 API 조회 → DB 등록<br>
                <strong>유의점:</strong> 상품코드가 은행마다 같을 수 있어 (금융회사코드 + 상품코드) 복합 유니크 처리 
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="section-title">API 데이터 조회</div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            loan_type = st.selectbox("상품 유형", ["주택담보대출", "전세자금대출", "개인신용대출"], key="t1_loan")
        with col2:
            fin_grp = st.selectbox("권역", [("은행", "020000"), ("저축은행", "030200")], format_func=lambda x: x[0], key="t1_grp")
        with col3:
            st.markdown("<div style='height:32px'></div>", unsafe_allow_html=True)
            fetch_btn = st.button("조회", key="t1_fetch", use_container_width=True)
        
        if fetch_btn:
            with st.spinner("조회 중..."):
                data, elapsed, status = fetch_loan_products(loan_type, fin_grp[1])
            
            if "error" not in data:
                df = api_to_dataframe(data, loan_type)
                total = data.get("result", {}).get("total_count", len(df))
                endpoint = ENDPOINTS[loan_type]
                
                st.session_state.t1_result = {
                    "df": df, "elapsed": elapsed, "total": total, 
                    "loan_type": loan_type, "status": status, "endpoint": endpoint,
                    "fin_grp": fin_grp[1]
                }
            else:
                st.session_state.t1_result = {"error": data["error"], "status": status, "elapsed": elapsed}
        
        if "t1_result" in st.session_state and st.session_state.t1_result:
            res = st.session_state.t1_result
            
            if "error" in res:
                st.markdown(f"""
                <div class="response-info error">
                    <div class="response-item">
                        <span class="response-label">상태</span>
                        <span class="response-value error">{res['status']} Error</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="api-code-box">
                    <span class="api-method">GET</span> <span class="api-url">/{res['endpoint']}.json?topFinGrpNo={res['fin_grp']}</span>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="response-info">
                    <div class="response-item">
                        <span class="response-label">상태</span>
                        <span class="response-value success">{res['status']} OK</span>
                    </div>
                    <div class="response-item">
                        <span class="response-label">응답시간</span>
                        <span class="response-value">{res['elapsed']:.0f}ms</span>
                    </div>
                    <div class="response-item">
                        <span class="response-label">건수</span>
                        <span class="response-value">{res['total']}건</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown('<div class="section-title">조회 결과</div>', unsafe_allow_html=True)
                
                company_filter = st.text_input("금융회사 필터", placeholder="예: 카카오, 토스", key="t1_filter")
                
                df = res["df"].copy()
                if company_filter:
                    df = df[df["금융회사"].str.contains(company_filter, case=False, na=False)]
                
                if df.empty:
                    st.info("조회된 상품이 없습니다.")
                else:
                    df_disp = df.reset_index(drop=True)
                    df_disp["금리"] = df_disp.apply(
                        lambda x: f"{x['최저금리']:.2f}~{x['최고금리']:.2f}%" if pd.notna(x['최저금리']) else "-", axis=1
                    )
                    df_disp["선택"] = True
                    
                    edited = st.data_editor(
                        df_disp[["선택", "금융회사", "상품명", "상품코드", "금리", "대출한도"]],
                        use_container_width=True, hide_index=True,
                        column_config={"선택": st.column_config.CheckboxColumn("", default=True)},
                        disabled=["금융회사", "상품명", "상품코드", "금리", "대출한도"],
                        key="t1_editor"
                    )
                    
                    sel_count = int(edited["선택"].sum())
                    
                    col1, col2 = st.columns([5, 1])
                    with col1:
                        st.caption(f"{sel_count}건 선택됨")
                    with col2:
                        if st.button("DB 등록", key="t1_save", disabled=sel_count==0, use_container_width=True):
                            mask = edited["선택"].tolist()
                            sel_df = df_disp[mask]
                            saved = save_products_to_db(conn, sel_df, res["loan_type"])
                            st.success(f"✓ {saved}건 등록 완료")

    # ==================== 탭 2 ====================
    with tab2:
        st.markdown("""
        <div class="scenario-banner">
            <div class="scenario-label">시나리오</div>
            <div class="scenario-text">
                <strong>상황:</strong> 제휴사 담당자가 "금리가 변경되었으니 반영 부탁드립니다"라고 연락했습니다.<br>
                <strong>할 일:</strong> 금감원 API 최신 데이터 조회 → 내부 DB와 비교 → 불일치 항목 업데이트
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="section-title">데이터 비교</div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            loan_type2 = st.selectbox("상품 유형", ["주택담보대출", "전세자금대출", "개인신용대출"], key="t2_loan")
        with col2:
            fin_grp2 = st.selectbox("권역", [("은행", "020000"), ("저축은행", "030200")], format_func=lambda x: x[0], key="t2_grp")
        with col3:
            st.markdown("<div style='height:32px'></div>", unsafe_allow_html=True)
            cmp_btn = st.button("비교 실행", key="t2_cmp", use_container_width=True)
        
        if cmp_btn:
            with st.spinner("비교 중..."):
                api_data, elapsed, status = fetch_loan_products(loan_type2, fin_grp2[1])
                
                if "error" not in api_data:
                    db_df = get_products_from_db(conn, {"loan_type": loan_type2})
                    api_df = api_to_dataframe(api_data, loan_type2)
                    endpoint = ENDPOINTS[loan_type2]
                    
                    match = mismatch = new = 0
                    results = []
                    
                    for _, row in api_df.iterrows():
                        db_match = db_df[db_df["fin_prdt_cd"] == row["상품코드"]]
                        
                        if db_match.empty:
                            new += 1
                            results.append({
                                "선택": True, "금융회사": row["금융회사"], "상품명": row["상품명"],
                                "상품코드": row["상품코드"], "DB 금리": "-",
                                "API 금리": f"{row['최저금리']:.2f}%" if pd.notna(row['최저금리']) else "-",
                                "상태": "신규"
                            })
                        else:
                            db_rate = db_match.iloc[0]["lend_rate_min"]
                            api_rate = row["최저금리"]
                            
                            if pd.isna(db_rate) or pd.isna(api_rate):
                                match += 1
                                results.append({
                                    "선택": False, "금융회사": row["금융회사"], "상품명": row["상품명"],
                                    "상품코드": row["상품코드"], "DB 금리": "-", "API 금리": "-", "상태": "일치"
                                })
                            elif abs(float(db_rate) - float(api_rate)) > 0.001:
                                mismatch += 1
                                arrow = "↓" if api_rate < db_rate else "↑"
                                results.append({
                                    "선택": True, "금융회사": row["금융회사"], "상품명": row["상품명"],
                                    "상품코드": row["상품코드"], "DB 금리": f"{db_rate:.2f}%",
                                    "API 금리": f"{api_rate:.2f}% {arrow}", "상태": "불일치"
                                })
                            else:
                                match += 1
                                results.append({
                                    "선택": False, "금융회사": row["금융회사"], "상품명": row["상품명"],
                                    "상품코드": row["상품코드"], "DB 금리": f"{db_rate:.2f}%",
                                    "API 금리": f"{api_rate:.2f}%", "상태": "일치"
                                })
                    
                    st.session_state.t2_result = {
                        "match": match, "mismatch": mismatch, "new": new,
                        "results": results, "api_df": api_df, "loan_type": loan_type2,
                        "elapsed": elapsed, "status": status, "endpoint": endpoint, "fin_grp": fin_grp2[1]
                    }
        
        if "t2_result" in st.session_state and st.session_state.t2_result:
            res = st.session_state.t2_result
            
            st.markdown(f"""
            <div class="api-code-box">
                <span class="api-method">GET</span> <span class="api-url">/{res['endpoint']}.json?topFinGrpNo={res['fin_grp']}</span>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="response-info">
                <div class="response-item">
                    <span class="response-label">상태</span>
                    <span class="response-value success">{res['status']} OK</span>
                </div>
                <div class="response-item">
                    <span class="response-label">응답시간</span>
                    <span class="response-value">{res['elapsed']:.0f}ms</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # 필터 카드 (새 디자인)
            total = res['match'] + res['mismatch'] + res['new']
            current = st.session_state.get('t2_filter', 'total')
            
            st.markdown(f"""
            <div class="filter-wrap">
                <div class="filter-item">
                    <div class="dot gray"></div>
                    <div class="info">
                        <span class="num">{total}</span>
                        <span class="label">Total</span>
                    </div>
                </div>
                <div class="filter-item {'active' if current == 'match' else ''}">
                    <div class="dot green"></div>
                    <div class="info">
                        <span class="num">{res['match']}</span>
                        <span class="label">Match</span>
                    </div>
                </div>
                <div class="filter-item {'active' if current == 'mismatch' else ''}">
                    <div class="dot yellow"></div>
                    <div class="info">
                        <span class="num">{res['mismatch']}</span>
                        <span class="label">Mismatch</span>
                    </div>
                </div>
                <div class="filter-item {'active' if current == 'new' else ''}">
                    <div class="dot red"></div>
                    <div class="info">
                        <span class="num">{res['new']}</span>
                        <span class="label">New</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # 상태 필터 (selectbox)
            selected_filter = st.selectbox(
                "상태 필터", 
                ["전체", "일치", "불일치", "신규"], 
                key="t2_status_filter"
            )

            # 필터링된 데이터
            if res["results"]:
                cmp_df = pd.DataFrame(res["results"])
                
                # 필터 적용
                if selected_filter == "일치":
                    filtered_df = cmp_df[cmp_df["상태"] == "일치"]
                elif selected_filter == "불일치":
                    filtered_df = cmp_df[cmp_df["상태"] == "불일치"]
                elif selected_filter == "신규":
                    filtered_df = cmp_df[cmp_df["상태"] == "신규"]
                else:
                    filtered_df = cmp_df
                
                if filtered_df.empty:
                    st.info("해당 항목이 없습니다.")
                else:
                    edited = st.data_editor(
                        filtered_df, use_container_width=True, hide_index=True,
                        column_config={"선택": st.column_config.CheckboxColumn("", default=True)},
                        disabled=["금융회사", "상품명", "상품코드", "DB 금리", "API 금리", "상태"],
                        key="t2_editor"
                    )
                    
                    sel_count = int(edited["선택"].sum())
                    col1, col2 = st.columns([5, 1])
                    with col1:
                        st.caption(f"{sel_count}건 선택됨")
                    with col2:
                        if st.button("DB 반영", key="t2_save", disabled=sel_count==0, use_container_width=True):
                            codes = edited[edited["선택"]]["상품코드"].tolist()
                            sel_df = res["api_df"][res["api_df"]["상품코드"].isin(codes)]
                            saved = save_products_to_db(conn, sel_df, res["loan_type"])
                            st.success(f"✓ {saved}건 반영 완료")
            else:
                st.markdown('<div class="success-box">✓ 모든 데이터가 일치합니다.</div>', unsafe_allow_html=True)
    
    # ==================== 탭 3 ====================
    with tab3:
        st.markdown("""
        <div class="scenario-banner error">
            <div class="scenario-label error">장애 상황</div>
            <div class="scenario-text">
                <strong>상황:</strong> 고객센터에서 "대출 조회가 안 됩니다"라는 문의가 들어왔습니다.<br>
                <strong>할 일:</strong> 해당 API 직접 호출 테스트 → 에러 코드 확인 → 원인 파악 후 조치
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="status-guide">
            <div class="status-item">
                <span class="status-code code-200">200</span>
                <span class="status-desc">정상 응답</span>
            </div>
            <div class="status-item">
                <span class="status-code code-400">400</span>
                <span class="status-desc">잘못된 요청</span>
            </div>
            <div class="status-item">
                <span class="status-code code-401">401</span>
                <span class="status-desc">인증 오류</span>
            </div>
            <div class="status-item">
                <span class="status-code code-500">500</span>
                <span class="status-desc">서버 오류</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="section-title">API 테스트</div>', unsafe_allow_html=True)

        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            loan_type3 = st.selectbox("대출 유형", ["주택담보대출", "전세자금대출", "개인신용대출"], key="t3_loan")
        with col2:
            fin_grp3 = st.selectbox("권역", [("은행", "020000"), ("저축은행", "030200")], format_func=lambda x: x[0], key="t3_grp")
        with col3:
            st.markdown("<div style='height:32px'></div>", unsafe_allow_html=True)
            test_btn = st.button("테스트 실행", key="t3_test", use_container_width=True)
        
        if test_btn:
            with st.spinner("테스트 중..."):
                data, elapsed, status = fetch_loan_products(loan_type3, fin_grp3[1])
            
            endpoint = ENDPOINTS[loan_type3]
            st.session_state.t3_result = {
                "data": data, "elapsed": elapsed, "status": status,
                "endpoint": endpoint, "fin_grp": fin_grp3[1], "loan_type": loan_type3
            }
        
        if "t3_result" in st.session_state and st.session_state.t3_result:
            res = st.session_state.t3_result
            
            st.markdown('<div class="section-title">응답 결과</div>', unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="api-code-box">
                <span class="api-method">GET</span> <span class="api-url">/{res['endpoint']}.json?topFinGrpNo={res['fin_grp']}</span>
            </div>
            """, unsafe_allow_html=True)
            
            if "error" in res["data"]:
                st.markdown(f"""
                <div class="response-info error">
                    <div class="response-item">
                        <span class="response-label">상태</span>
                        <span class="response-value error">{res['status']} Error</span>
                    </div>
                    <div class="response-item">
                        <span class="response-label">응답시간</span>
                        <span class="response-value">{res['elapsed']:.0f}ms</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="error-box">
                    <div class="error-title">장애 원인</div>
                    <div class="error-text">
                        {res['loan_type']} API 호출 실패 ({res['status']})<br>
                        원인: {res['data'].get('error', '알 수 없음')}<br>
                        조치: 금감원 서버 상태 확인 또는 네트워크 점검 필요
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                total = res["data"].get("result", {}).get("total_count", 0)
                
                st.markdown(f"""
                <div class="response-info">
                    <div class="response-item">
                        <span class="response-label">상태</span>
                        <span class="response-value success">{res['status']} OK</span>
                    </div>
                    <div class="response-item">
                        <span class="response-label">응답시간</span>
                        <span class="response-value">{res['elapsed']:.0f}ms</span>
                    </div>
                    <div class="response-item">
                        <span class="response-label">건수</span>
                        <span class="response-value">{total}건</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="success-box">
                    ✓ API 정상 작동<br>
                    {res['loan_type']} API가 정상 응답 중입니다. 문제 지속시 내부 시스템 점검 필요.
                </div>
                """, unsafe_allow_html=True)
    
    # ==================== 탭 4 ====================
    with tab4:
        st.markdown('<div class="section-title">공시정보 조회</div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            companies = pd.read_sql_query("SELECT DISTINCT kor_co_nm FROM products", conn)["kor_co_nm"].tolist()
            filter_co = st.selectbox("금융회사", ["전체"] + companies, key="t4_co")
        with col2:
            filter_type = st.selectbox("상품 유형", ["전체", "주택담보대출", "전세자금대출", "개인신용대출"], key="t4_type")
        with col3:
            search = st.text_input("검색", placeholder="상품명", key="t4_search")
        
        query = "SELECT * FROM products WHERE 1=1"
        if filter_co != "전체":
            query += f" AND kor_co_nm = '{filter_co}'"
        if filter_type != "전체":
            query += f" AND loan_type = '{filter_type}'"
        if search:
            query += f" AND fin_prdt_nm LIKE '%{search}%'"
        
        df = pd.read_sql_query(query, conn)
        
        if df.empty:
            st.info("등록된 상품이 없습니다.")
        else:
            df_disp = df.rename(columns={
                "id": "ID", "kor_co_nm": "금융회사", "fin_prdt_nm": "상품명",
                "loan_type": "유형", "lend_rate_min": "최저금리", "lend_rate_max": "최고금리",
                "loan_lmt": "한도", "updated_at": "최종수정"
            })
            st.dataframe(
                df_disp[["ID", "금융회사", "상품명", "유형", "최저금리", "최고금리", "한도", "최종수정"]],
                use_container_width=True, hide_index=True
            )
            st.caption(f"전체 {len(df)}건")
        
        st.markdown("---")
        st.markdown('<div class="section-title">데이터 수정</div>', unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)
        with col1:
            edit_id = st.number_input("수정할 ID", min_value=1, step=1, key="edit_id")
        with col2:
            new_rate_min = st.number_input("새 최저금리 (%)", min_value=0.0, max_value=30.0, step=0.01, key="new_min")
        with col3:
            new_rate_max = st.number_input("새 최고금리 (%)", min_value=0.0, max_value=30.0, step=0.01, key="new_max")

        if st.button("수정", key="edit_btn"):
            conn.execute("""
                UPDATE products 
                SET lend_rate_min = ?, lend_rate_max = ?, updated_at = ?
                WHERE id = ?
            """, (new_rate_min, new_rate_max, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), edit_id))
            conn.commit()
            st.success(f"✓ ID {edit_id} 금리 수정 완료")
            st.rerun()

        col1, col2 = st.columns([5, 1])
        with col2:
            if st.button("전체 삭제", key="del_all", use_container_width=True):
                st.session_state.confirm_del = True
        
        if st.session_state.get("confirm_del"):
            st.warning("정말 모든 데이터를 삭제하시겠습니까?")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("취소", use_container_width=True):
                    st.session_state.confirm_del = False
                    st.rerun()
            with c2:
                if st.button("삭제 확인", use_container_width=True):
                    conn.execute("DELETE FROM products")
                    conn.commit()
                    st.session_state.confirm_del = False
                    st.success("✓ 삭제 완료")
                    st.rerun()
    
    st.markdown('<div class="footer">Provided by 강유진</div>', unsafe_allow_html=True)
    conn.close()

if __name__ == "__main__":
    main()