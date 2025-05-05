# components/chain_analytics.py
import streamlit as st
import pandas as pd
import altair as alt
from typing import Dict, List, Any
from datetime import datetime

def render_analytics_dashboard(chains: List[Dict[str, Any]]):
    """Render analytics dashboard for all chains"""
    st.header("Chain Analytics")

    if not chains:
        st.info("No chain data available for analytics.")
        return

    chain_metrics = []
    for chain in chains:
        executions = chain.get("executions", [])
        metrics = {
            "chain_id": chain.get("id", "Unknown"),
            "goal": chain.get("initial_goal", ""),
            "status": chain.get("status", ""),
            "created_at": datetime.fromisoformat(chain.get("created_at", datetime.now().isoformat())),
            "agents_count": len(executions),
            "total_duration": sum([
                execution.get("metrics", {}).get("total_duration", 0)
                for execution in executions
            ]),
            "total_tokens": sum([
                execution.get("metrics", {}).get("prompt_tokens", 0) +
                execution.get("metrics", {}).get("completion_tokens", 0)
                for execution in executions
            ]),
            "errors_count": sum([
                1 if execution.get("status") == "ERROR" or execution.get("execution_result", {}).get("errors")
                else 0
                for execution in executions
            ])
        }
        chain_metrics.append(metrics)

    df = pd.DataFrame(chain_metrics)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Chains", len(df))
    col2.metric("Avg. Agents", f"{df['agents_count'].mean():.1f}" if not df.empty else "0")
    col3.metric("Avg. Duration", f"{df['total_duration'].mean():.2f}s" if not df.empty else "0s")
    success_rate = 0
    if not df.empty and df['agents_count'].sum() > 0:
        success_rate = 100 * (1 - df['errors_count'].sum() / df['agents_count'].sum())
    col4.metric("Success Rate", f"{success_rate:.1f}%")

    if not df.empty:
        st.subheader("Duration Distribution")
        chart = alt.Chart(df).mark_bar().encode(
            x=alt.X('total_duration:Q', bin=True, title='Duration (s)'),
            y=alt.Y('count()', title='Chains')
        ).properties(width=600)
        st.altair_chart(chart)

        st.subheader("Chains by Status")
        status_counts = df['status'].value_counts().reset_index()
        status_counts.columns = ['status', 'count']
        pie = alt.Chart(status_counts).mark_arc().encode(
            theta=alt.Theta(field="count", type="quantitative"),
            color=alt.Color(field="status", type="nominal"),
        ).properties(width=400, height=400)
        st.altair_chart(pie)

        st.subheader("Recent Chains")
        recent = df[['chain_id','goal','status','created_at','agents_count','total_duration']].sort_values('created_at', ascending=False).head(10)
        st.dataframe(recent)
