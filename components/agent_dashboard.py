# components/agent_dashboard.py
import streamlit as st
from typing import Dict, List, Any

def render_agent_execution(execution: Dict[str, Any], expanded: bool = False):
    """Render details of a single agent execution"""
    agent_spec = execution.get("agent_spec", {})
    execution_result = execution.get("execution_result", {})
    metrics = execution.get("metrics", {})

    with st.expander(f"Agent: {agent_spec.get('goal', 'Unknown')}", expanded=expanded):
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Agent Specification")
            st.json(agent_spec)

        with col2:
            st.subheader("Execution Result")
            if execution.get("status") == "ERROR" or execution_result.get("errors"):
                st.error("Execution failed")
                st.json(execution_result)
            else:
                st.success("Execution completed")
                st.json(execution_result)

        if metrics:
            st.subheader("Performance Metrics")
            m1, m2, m3 = st.columns(3)
            m1.metric("Duration", f"{metrics.get('total_duration', 0):.2f}s")
            m2.metric("Prompt Tokens", metrics.get('prompt_tokens', 0))
            m3.metric("Completion Tokens", metrics.get('completion_tokens', 0))

            for tool_exec in metrics.get("tool_executions", []):
                with st.expander(f"{tool_exec.get('tool_name', 'Unknown')} ({tool_exec.get('duration', 0):.2f}s)"):
                    if tool_exec.get("error"):
                        st.error(f"Error: {tool_exec.get('error')}")
                    else:
                        st.json(tool_exec.get("output", {}))
