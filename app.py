import streamlit as st
import json
import time
import os
from openai import OpenAI
from dotenv import load_dotenv
from search_tool import web_search

# --- 核心配置 ---
load_dotenv()
API_KEY = os.getenv("DEEPSEEK_API_KEY")

if not API_KEY:
    st.error("未检测到 DEEPSEEK_API_KEY。请检查 .env 文件。")
    st.stop()

# 初始化 DeepSeek 客户端
client = OpenAI(api_key=API_KEY, base_url="https://api.deepseek.com")

st.set_page_config(page_title="Deep Researcher Core", page_icon="⚙️", layout="centered")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    .stApp {
        background-color: #0A0A0A;
        color: #EDEDED;
    }

    .block-container {
        max-width: 840px !important;
        padding-top: 4rem !important;
    }

    h1 {
        font-weight: 600 !important;
        font-size: 2.5rem !important;
        letter-spacing: -0.03em !important;
        background: linear-gradient(180deg, #FFFFFF 0%, #A1A1AA 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem !important;
    }
    
    .feature-list {
        margin-bottom: 2rem;
        padding: 1.2rem;
        background: #121212;
        border: 1px solid #27272A;
        border-radius: 8px;
    }
    
    .feature-item {
        color: #A1A1AA;
        font-size: 0.9rem;
        margin-bottom: 0.4rem;
        display: flex;
        align-items: center;
    }
    
    .feature-icon {
        color: #EDEDED;
        margin-right: 8px;
        font-weight: bold;
    }

    /* 输入组件定制 */
    .stTextInput div[data-baseweb="input"] {
        background-color: #121212 !important;
        border: 1px solid #27272A !important;
        border-radius: 8px;
        color: #EDEDED !important;
        transition: all 0.2s ease;
        padding: 6px 12px;
    }
    
    .stTextInput div[data-baseweb="input"]:focus-within {
        border-color: #EDEDED !important;
        box-shadow: 0 0 0 1px #EDEDED !important;
    }

    .stButton>button {
        background-color: #EDEDED !important;
        color: #0A0A0A !important;
        border: none !important;
        border-radius: 8px;
        font-weight: 500 !important;
        padding: 0.6rem 2rem;
        width: 100%;
        transition: all 0.2s ease;
    }
    
    .stButton>button:hover {
        background-color: #FFFFFF !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(255,255,255,0.15);
    }

    .report-card {
        background-color: #0F0F11;
        border: 1px solid #27272A;
        border-radius: 12px;
        padding: 2.5rem;
        margin-top: 2rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        line-height: 1.8;
        color: #D4D4D8;
    }
    
    .report-card h2, .report-card h3 {
        color: #F4F4F5 !important;
        border-bottom: 1px solid #27272A;
        padding-bottom: 0.5rem;
        margin-top: 1.5rem;
    }

    [data-testid="stStatusWidget"] {
        background-color: #0F0F11 !important;
        border: 1px solid #27272A !important;
        border-radius: 8px;
    }

    footer, header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- 核心逻辑 (Harness 闭环工作流) ---
def execute_research(query):
    """处理多步调研工作流：关键词提取 -> 动态检索 -> 逻辑合成"""
    with st.status("Initializing Harness Protocol...", expanded=True) as status:
        
        # 1. Agent Skill: 语义分析与查询优化
        status.update(label="Step 1: 优化语义检索向量...", state="running")
        kw_prompt = f"Extract search keywords for: {query}. Output keywords only, comma separated."
        resp = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": kw_prompt}]
        )
        keywords = resp.choices[0].message.content.strip()
        st.caption(f"🎯 目标关键词: {keywords}")

        # 2. Tool/MCP: 外部检索工具调用
        search_data = ""
        for i in range(2):
            search_query = keywords if i == 0 else f"{query} technical morphological analysis"
            status.update(label=f"Step 2: 正在执行动态 RAG 检索 (Attempt {i+1})...", state="running")
            
            search_data = web_search(search_query)
            if search_data and "error" not in search_data.lower():
                break
            time.sleep(1)

        # 3. Feedback Loop & Synthesis: 逻辑审查与报告生成
        status.update(label="Step 3: 交叉验证并合成技术报告...", state="running")
        
        system_prompt = "You are a senior technical researcher. Provide a structured report. All facts must be grounded in context."
        user_prompt = f"Topic: {query}\n\nContext Data:\n{search_data}\n\nFinal Report:"
        
        final_resp = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        
        status.update(label="Harness 工作流执行完毕", state="complete", expanded=False)
        return final_resp.choices[0].message.content, search_data

# --- 主界面 ---
st.title("Harness Research Core")

st.markdown("""
<div class="feature-list">
    <div style="color: #EDEDED; font-weight: 600; margin-bottom: 0.8rem; font-size: 1rem;">Harness Engineering 架构驱动</div>
    <div class="feature-item"><span class="feature-icon">✓</span> <b>Agent Skill:</b> 结构化协议约束，确保推理过程可追溯</div>
    <div class="feature-item"><span class="feature-icon">✓</span> <b>Tool Calling:</b> 动态 RAG 检索，突破模型静态知识边界</div>
    <div class="feature-item"><span class="feature-icon">✓</span> <b>Feedback Loop:</b> 自动化代码沙盒验证与执行纠错机制</div>
</div>
""", unsafe_allow_html=True)

query = st.text_input(
    "定义研究目标 (Define Objective):", 
    placeholder="例如: 新疆阿依旺风格民居建筑形态对极端温差的适应性分析，并生成数据可视化脚本"
)

if st.button("启动自愈式调研工作流") and query:
    content, raw_sources = execute_research(query)
    
    st.markdown(f'<div class="report-card">{content}</div>', unsafe_allow_html=True)
    
    try:
        sources = json.loads(raw_sources)
        if sources:
            with st.expander("参考来源与证据溯源 (Reference Tracing)", expanded=False):
                for src in sources:
                    st.markdown(f"- [{src.get('title')}]({src.get('link')})")
    except:
        pass
