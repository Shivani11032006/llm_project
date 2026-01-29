import streamlit as st
import pandas as pd
import time
import os

from dotenv import load_dotenv
load_dotenv()
try:
    from auth import login
    from utils.router import choose_models
    from utils.parallel import run_parallel
    from utils.rate_limiter import check_limit
    from utils.report import generate_report
except Exception as e:
    st.error(e)
    st.stop()

st.set_page_config(
    page_title="LLM Nexus | Enterprise Comparison",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

/* -------------------- GLOBAL -------------------- */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: radial-gradient(circle at top left, #020617, #020617 40%, #020617);
    color: #e5e7eb;
}

/* Scrollbar */
::-webkit-scrollbar {
    width: 8px;
}
::-webkit-scrollbar-thumb {
    background: #334155;
    border-radius: 10px;
}
::-webkit-scrollbar-thumb:hover {
    background: #475569;
}

/* -------------------- HEADERS -------------------- */
h1, h2, h3 {
    color: #f8fafc !important;
    font-weight: 800;
}

.main-header {
    font-size: 3rem;
    font-weight: 900;
    background: linear-gradient(90deg, #38bdf8, #818cf8, #22d3ee);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.3rem;
    animation: fadeIn 0.8s ease-in-out;
}

.sub-header {
    font-size: 1.1rem;
    color: #94a3b8;
    margin-bottom: 2.2rem;
}

/* -------------------- SIDEBAR -------------------- */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #020617, #020617);
    border-right: 1px solid #1f2937;
}

section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2 {
    font-weight: 700;
}

/* -------------------- INPUTS -------------------- */
.stTextArea textarea {
    background: rgba(2, 6, 23, 0.8);
    backdrop-filter: blur(12px);
    border: 1px solid #1f2937;
    color: #f9fafb;
    border-radius: 16px;
    padding: 14px;
    font-size: 0.95rem;
    transition: all 0.25s ease;
}

.stTextArea textarea:focus {
    border-color: #38bdf8;
    box-shadow: 0 0 0 3px rgba(56,189,248,0.25);
}

/* Selectbox */
div[data-baseweb="select"] > div {
    background: rgba(2, 6, 23, 0.9);
    border: 1px solid #1f2937;
    border-radius: 14px;
    color: white;
}

/* -------------------- BUTTONS -------------------- */
div.stButton > button {
    background: linear-gradient(135deg, #38bdf8, #6366f1);
    color: #020617;
    border: none;
    padding: 1rem 2.2rem;
    font-weight: 800;
    border-radius: 18px;
    width: 100%;
    font-size: 1rem;
    letter-spacing: 0.5px;
    transition: all 0.3s ease;
}

div.stButton > button:hover {
    transform: translateY(-2px) scale(1.01);
    box-shadow: 0 15px 35px rgba(56,189,248,0.45);
}

div.stButton > button:active {
    transform: scale(0.98);
}

/* -------------------- CARDS -------------------- */
.model-card {
    background: linear-gradient(180deg, rgba(2,6,23,0.85), rgba(2,6,23,0.95));
    backdrop-filter: blur(14px);
    border: 1px solid #1f2937;
    border-radius: 20px;
    padding: 22px;
    height: 100%;
    box-shadow: 0 12px 40px rgba(0,0,0,0.45);
    transition: all 0.3s ease;
}

.model-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 18px 55px rgba(56,189,248,0.25);
}

.model-name {
    font-weight: 800;
    color: #38bdf8;
    font-size: 0.85rem;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-bottom: 14px;
    border-bottom: 1px solid #1f2937;
    padding-bottom: 8px;
}

/* -------------------- METRICS -------------------- */
div[data-testid="metric-container"] {
    background: linear-gradient(180deg, rgba(2,6,23,0.9), rgba(2,6,23,1));
    border: 1px solid #1f2937;
    padding: 20px;
    border-radius: 18px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.35);
}

div[data-testid="metric-container"] label {
    color: #94a3b8 !important;
    font-weight: 600;
}

div[data-testid="metric-container"] div {
    font-size: 1.4rem;
    font-weight: 800;
}

/* -------------------- TABS -------------------- */
button[data-baseweb="tab"] {
    font-weight: 700;
    font-size: 0.9rem;
    color: #9ca3af;
    padding-bottom: 8px;
}

button[data-baseweb="tab"][aria-selected="true"] {
    color: #38bdf8;
    border-bottom: 3px solid #38bdf8;
}

/* -------------------- STATUS -------------------- */
div[data-testid="stStatusWidget"] {
    background: rgba(2,6,23,0.9);
    border: 1px solid #1f2937;
    border-radius: 16px;
}

/* -------------------- ANIMATIONS -------------------- */
@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

/* -------------------- GLOBAL -------------------- */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: radial-gradient(circle at top left, #020617, #020617 40%, #020617);
    color: #e5e7eb;
}

/* Scrollbar */
::-webkit-scrollbar {
    width: 8px;
}
::-webkit-scrollbar-thumb {
    background: #334155;
    border-radius: 10px;
}
::-webkit-scrollbar-thumb:hover {
    background: #475569;
}

/* -------------------- HEADERS -------------------- */
h1, h2, h3 {
    color: #f8fafc !important;
    font-weight: 800;
}

.main-header {
    font-size: 3rem;
    font-weight: 900;
    background: linear-gradient(90deg, #38bdf8, #818cf8, #22d3ee);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.3rem;
    animation: fadeIn 0.8s ease-in-out;
}

.sub-header {
    font-size: 1.1rem;
    color: #94a3b8;
    margin-bottom: 2.2rem;
}

/* -------------------- SIDEBAR -------------------- */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #020617, #020617);
    border-right: 1px solid #1f2937;
}

section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2 {
    font-weight: 700;
}

/* -------------------- INPUTS -------------------- */
.stTextArea textarea {
    background: rgba(2, 6, 23, 0.8);
    backdrop-filter: blur(12px);
    border: 1px solid #1f2937;
    color: #f9fafb;
    border-radius: 16px;
    padding: 14px;
    font-size: 0.95rem;
    transition: all 0.25s ease;
}

.stTextArea textarea:focus {
    border-color: #38bdf8;
    box-shadow: 0 0 0 3px rgba(56,189,248,0.25);
}

/* Selectbox */
div[data-baseweb="select"] > div {
    background: rgba(2, 6, 23, 0.9);
    border: 1px solid #1f2937;
    border-radius: 14px;
    color: white;
}

/* -------------------- BUTTONS -------------------- */
div.stButton > button {
    background: linear-gradient(135deg, #38bdf8, #6366f1);
    color: #020617;
    border: none;
    padding: 1rem 2.2rem;
    font-weight: 800;
    border-radius: 18px;
    width: 100%;
    font-size: 1rem;
    letter-spacing: 0.5px;
    transition: all 0.3s ease;
}

div.stButton > button:hover {
    transform: translateY(-2px) scale(1.01);
    box-shadow: 0 15px 35px rgba(56,189,248,0.45);
}

div.stButton > button:active {
    transform: scale(0.98);
}

/* -------------------- CARDS -------------------- */
.model-card {
    background: linear-gradient(180deg, rgba(2,6,23,0.85), rgba(2,6,23,0.95));
    backdrop-filter: blur(14px);
    border: 1px solid #1f2937;
    border-radius: 20px;
    padding: 22px;
    height: 100%;
    box-shadow: 0 12px 40px rgba(0,0,0,0.45);
    transition: all 0.3s ease;
}

.model-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 18px 55px rgba(56,189,248,0.25);
}

.model-name {
    font-weight: 800;
    color: #38bdf8;
    font-size: 0.85rem;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-bottom: 14px;
    border-bottom: 1px solid #1f2937;
    padding-bottom: 8px;
}

/* -------------------- METRICS -------------------- */
div[data-testid="metric-container"] {
    background: linear-gradient(180deg, rgba(2,6,23,0.9), rgba(2,6,23,1));
    border: 1px solid #1f2937;
    padding: 20px;
    border-radius: 18px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.35);
}

div[data-testid="metric-container"] label {
    color: #94a3b8 !important;
    font-weight: 600;
}

div[data-testid="metric-container"] div {
    font-size: 1.4rem;
    font-weight: 800;
}

/* -------------------- TABS -------------------- */
button[data-baseweb="tab"] {
    font-weight: 700;
    font-size: 0.9rem;
    color: #9ca3af;
    padding-bottom: 8px;
}

button[data-baseweb="tab"][aria-selected="true"] {
    color: #38bdf8;
    border-bottom: 3px solid #38bdf8;
}

/* -------------------- STATUS -------------------- */
div[data-testid="stStatusWidget"] {
    background: rgba(2,6,23,0.9);
    border: 1px solid #1f2937;
    border-radius: 16px;
}

/* -------------------- ANIMATIONS -------------------- */
@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}
</style>
""", unsafe_allow_html=True)


with st.sidebar:
    st.title("⚙️ Controls")
    
    if "user" in st.session_state:
        st.info(f"👤 Logged in as: **{st.session_state.user}**")
    
    st.markdown("---")
    
    st.subheader("Configuration")
    model_temp = st.slider("Temperature (Creativity)", 0.0, 1.0, 0.7)
    max_tokens = st.number_input("Max Tokens", value=1024, step=256)
    
    st.markdown("---")
    st.caption("v2.1.0 | Enterprise Edition")


def main():
    
    login()
    if "user" not in st.session_state:
        st.stop()

   
    st.markdown('<div class="main-header">LLM Nexus</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Intelligent routing & cost-analysis engine for Generative AI.</div>', unsafe_allow_html=True)

    
    col1, col2 = st.columns([1, 3])

    with col1:
        task = st.selectbox(
            "Target Objective",
            ["General", "Coding", "Fast Response", "Cost Saving"],
            help="This determines which models are selected via the router."
        )
        
       
        st.metric(label="Active Models", value="3 Online", delta="All Systems Go")

    with col2:
        prompt = st.text_area(
            "Input Prompt",
            height=140,
            placeholder="E.g., Write a secure Python function to connect to AWS S3...",
            label_visibility="visible"
        )

   
    col_submit, col_spacer = st.columns([1, 4])
    with col_submit:
        run_btn = st.button("⚡ Execute Query")

    if run_btn:
        if not check_limit(st.session_state.user):
            st.error("🚫 Rate limit reached. Please upgrade your plan or wait.")
            st.stop()
            
        if not prompt.strip():
            st.warning("⚠️ Please provide a prompt to analyze.")
            st.stop()

     
        with st.status("🔄 Orchestrating Model Requests...", expanded=True) as status:
            st.write("🔍 Analyzing intent...")
            models = choose_models(task)
            st.write(f"✅ Selected optimized models: **{', '.join(models)}**")
            
            st.write("🚀 Dispatching parallel requests...")
            start_time = time.time()
            
            responses = run_parallel(prompt, models)
            
            elapsed = round(time.time() - start_time, 2)
            status.update(label=f"✅ Complete! Processed in {elapsed}s", state="complete", expanded=False)

     
        st.markdown("### 📊 Analysis Results")
        
       
        tab1, tab2, tab3, tab4 = st.tabs([
            "👁️ Visual Comparison",
            "📝 Raw Data",
            "📉 Cost Report",
            "📊 Performance Dashboard"
        ])



        with tab1:
           
            cols = st.columns(len(responses))
            
         
            for idx, (model_name, response_text) in enumerate(responses.items()):
                with cols[idx]:
                    st.markdown(f"""
                    <div class="model-card">
                        <div class="model-name">{model_name}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.markdown("---")
                    st.markdown(response_text) 

        with tab2:
            st.json(responses)

        with tab3:
           
            report_status = generate_report(prompt, responses)
            st.success("Report generated and saved to database.")
            
           
            metrics_col1, metrics_col2 = st.columns(2)
            metrics_col1.metric("Estimated Cost", "$0.0042", "-12%")
            metrics_col2.metric("Latency Average", f"{elapsed}s", "Fast")
        with tab4:
            st.markdown("### 📊 Model Performance Dashboard")

            metrics_file = "data/metrics/metrics.csv"

            if not os.path.exists(metrics_file):
                st.warning("No metrics data available yet. Run some prompts first.")
            else:
                df = pd.read_csv(metrics_file)

                df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")

                st.subheader("⏱️ Average Latency per Model")
                latency_df = df.groupby("model")["latency"].mean().reset_index()
                st.bar_chart(latency_df.set_index("model"))

                st.subheader("📏 Average Response Length")
                length_df = df.groupby("model")["response_length"].mean().reset_index()
                st.bar_chart(length_df.set_index("model"))

                st.subheader("📈 Requests Over Time")
                time_df = df.set_index("timestamp").resample("1min").count()["model"]
                st.line_chart(time_df)


if __name__ == "__main__":
    main()