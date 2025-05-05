# app.py
import streamlit as st
from infrastructure.auth import setup_auth
from infrastructure.supabase_store import SupabaseStore
from infrastructure.llm_service import LLMService, LLMProvider
from core.chain_runner import ChainRunner
from core.agent import AgentSpec
from tools import tools  # <-- import the actual dict
from components.agent_dashboard import render_chain_dashboard
from components.chain_analytics import render_analytics_dashboard

st.set_page_config(page_title="DANI", layout="wide")
if not setup_auth(): st.stop()

@st.cache_resource
def init():
    store = SupabaseStore()
    tools_dict = {
        "browsing": tools.BrowsingTool(),
        "scraping": tools.ScrapingTool(),
        "calculation": tools.CalculationTool(),
        "rest_api": tools.RestApiTool(),
        "autopilot": tools.AutopilotTool()
    }
    llm = LLMService(provider=LLMProvider.CLAUDE)
    runner = ChainRunner(llm_service=llm, store=store, available_tools=tools)
    return store, tools, llm, runner

store, tools, llm_service, runner = init()
tabs=["New Chain","Monitor","Analytics"]
if "tab" not in st.session_state: st.session_state.tab="New Chain"
sel = st.radio("", tabs, horizontal=True, index=tabs.index(st.session_state.tab))
st.session_state.tab = sel

if sel=="New Chain":
    with st.form("f"):
        goal = st.text_area("Goal","")
        selected = st.multiselect("Tools", list(tools.keys()), default=list(tools.keys()))
        launch = st.form_submit_button("Launch")  # <- assign to a variable
        if launch:
            cid = runner.start_chain(goal, selected)
            res = runner.execute_next_agent(cid, AgentSpec(goal=goal, tools=selected))
            if res.errors:
                st.error(res.errors)
            else:
                st.success(f"Launched {cid[:8]}")
                st.session_state.selected = cid

elif sel=="Monitor":
    cid = st.session_state.get("selected")
    if cid:
        data = store.get_chain_details(cid)
        execs = store.get_chain_executions(cid)
        render_chain_dashboard(cid, data, execs)
        if data["status"] not in ["COMPLETED","FAILED"]: st.experimental_rerun()
    else: st.info("Launch a chain first")

else:
    chains = store.get_all_chains_with_metrics()
    render_analytics_dashboard(chains)
