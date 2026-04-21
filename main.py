import json
import time
import re
import sys
import io
import os
import traceback
from openai import OpenAI
from dotenv import load_dotenv
from search_tool import web_search

# --- Configuration ---
load_dotenv()
API_KEY = os.getenv("DEEPSEEK_API_KEY") 
# 建议通过环境变量读取，避免硬编码。如果必须硬编码，直接写字符串即可，不需要注释提醒。

client = OpenAI(
    api_key=API_KEY,
    base_url="https://api.deepseek.com"
)

def fetch_llm_response(prompt, system_role="You are a helpful assistant.", model="deepseek-chat"):
    """封装常用的调用逻辑"""
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_role},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3 # 降低随机性，增加技术回答的稳定性
    )
    return response.choices[0].message.content.strip()

# ==========================================
# 1. Search Logic (Query Refinement)
# ==========================================
def get_search_context(query, max_retries=2):
    print(f"[*] Analyzing query for retrieval...")
    
    # 提取搜索关键词
    kw_prompt = f"Identify optimal search keywords for: {query}. Return keywords only, separated by commas."
    keywords = fetch_llm_response(kw_prompt)
    
    for i in range(max_retries):
        current_kw = keywords if i == 0 else f"{query} technical details analysis"
        print(f"[-] Executing search with: {current_kw}")
        
        results = web_search(current_kw)
        
        if results and "error" not in results.lower() and len(results) > 100:
            print("[+] Retrieval successful.")
            return results
        
        print(f"[!] Low quality results, retrying ({i+1}/{max_retries})...")
        time.sleep(1)
            
    return results

# ==========================================
# 2. Sandbox Execution & Self-Healing
# ==========================================
def run_and_repair_code(code_snippet, max_attempts=3):
    """在隔离环境中执行 Python 代码并进行自动修复"""
    print("[*] Entering execution sandbox...")
    
    current_code = code_snippet
    for i in range(max_attempts):
        print(f"[-] Execution attempt {i+1}...")
        
        output_buffer = io.StringIO()
        sys.stdout = output_buffer
        
        try:
            # 使用独立字典作为命名空间，防止污染全局变量
            exec(current_code, {"__name__": "__main__", "import": __import__})
            sys.stdout = sys.__stdout__
            print("[+] Execution successful.")
            return current_code, output_buffer.getvalue()
            
        except Exception:
            sys.stdout = sys.__stdout__
            error_log = traceback.format_exc()
            print(f"[!] Runtime error detected:\n{error_log.splitlines()[-1]}")
            
            if i == max_attempts - 1:
                return current_code, error_log
                
            print("[-] Attempting automated repair...")
            fix_prompt = f"Fix the following Python code error.\n\nError:\n{error_log}\n\nCode:\n{current_code}\n\nReturn the corrected code block ONLY."
            repaired_resp = fetch_llm_response(fix_prompt, system_role="You are an expert Python debugger. Only output code within triple backticks.")
            
            match = re.search(r'```python\s*(.*?)\s*```', repaired_resp, re.DOTALL)
            current_code = match.group(1) if match else repaired_resp

# ==========================================
# 3. Main Workflow
# ==========================================
def run_workflow(user_query):
    # Step 1: Context Acquisition
    context = get_search_context(user_query)
    
    # Step 2: Synthesis
    print("[*] Synthesizing initial response...")
    draft_prompt = f"Context:\n{context}\n\nTask:\n{user_query}\n\nIf calculation or visualization is required, provide Python code."
    draft = fetch_llm_response(draft_prompt)
    
    # Step 3: Code Validation (if exists)
    code_match = re.search(r'```python\s*(.*?)\s*```', draft, re.DOTALL)
    if code_match:
        valid_code, exec_result = run_and_repair_code(code_match.group(1))
        # 将验证过的代码和结果合入上下文供最终审查
        draft += f"\n\n[Code Execution Result]:\n{exec_result}"

    # Step 4: Final Review & Fact-check
    print("[*] Performing final technical review...")
    review_prompt = f"Review and refine the following content for technical accuracy and professional tone.\n\nContext:\n{context}\n\nDraft:\n{draft}"
    final_output = fetch_llm_response(review_prompt, system_role="You are a senior technical reviewer. Ensure the output is rigorous, fact-based, and lacks AI-generated mannerisms.")
    
    print("\n" + "="*30 + " FINAL REPORT " + "="*30)
    print(final_output)
    print("="*74)

if __name__ == "__main__":
    print("[System] Researcher Core Initialized.")
    
    while True:
        try:
            default_query = "新疆阿依旺风格民居建筑形态对极端沙尘与温差的适应性分析，并生成模拟气温波动的可视化脚本。"
            prompt_str = f"\nInput query (Enter for default): "
            user_input = input(prompt_str).strip() or default_query
                
            if user_input.lower() in ['exit', 'quit']:
                break
                
            run_workflow(user_input)
            
        except KeyboardInterrupt:
            break
