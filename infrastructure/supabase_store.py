# infrastructure/supabase_store.py
from typing import Dict, List, Any, Optional
from uuid import uuid4
from datetime import datetime
import json
import streamlit as st
from supabase import create_client, Client
from core.agent import AgentSpec, AgentResult

class SupabaseStore:
    def __init__(self):
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_ANON_KEY"]
        self.client: Client = create_client(url, key)

    def create_chain(self, initial_goal: str) -> str:
        cid = str(uuid4())
        now = datetime.now().isoformat()
        self.client.table("chains").insert({
            "id": cid, "initial_goal": initial_goal,
            "status":"CREATED", "created_at":now, "updated_at":now
        }).execute()
        return cid

    def update_chain_status(self, chain_id: str, status: str):
        now = datetime.now().isoformat()
        self.client.table("chains").update({
            "status": status, "updated_at": now
        }).eq("id", chain_id).execute()

    def store_agent_execution(self, chain_id: str, spec: AgentSpec, res: AgentResult, metrics: Any=None) -> str:
        eid = str(uuid4())
        spec_json = spec.json()
        res_json = res.json()
        metrics_json = metrics.json() if metrics else None
        status = "ERROR" if res.errors else "COMPLETED"
        self.client.table("agent_executions").insert({
            "id": eid, "chain_id":chain_id,
            "agent_spec": spec_json, "execution_result": res_json,
            "metrics": metrics_json, "status": status,
            "created_at": datetime.now().isoformat()
        }).execute()
        self.update_chain_status(chain_id, "RUNNING")
        return eid

    def get_chain_details(self, chain_id: str) -> Dict[str, Any]:
        resp = self.client.table("chains").select("*").eq("id", chain_id).execute()
        if not resp.data:
            raise ValueError("Chain not found")
        return resp.data[0]

    def get_chain_executions(self, chain_id: str) -> List[Dict[str, Any]]:
        resp = self.client.table("agent_executions").select("*").eq("chain_id", chain_id).order("created_at").execute()
        rows = []
        for r in resp.data:
            r["agent_spec"] = json.loads(r["agent_spec"])
            r["execution_result"] = json.loads(r["execution_result"])
            if r.get("metrics"): r["metrics"] = json.loads(r["metrics"])
            rows.append(r)
        return rows

    def get_active_chains(self, limit: int=5) -> List[Dict[str, Any]]:
        resp = self.client.table("chains").select("*").not_("status","eq","COMPLETED").order("updated_at",desc=True).limit(limit).execute()
        return resp.data

    def get_all_chains_with_metrics(self) -> List[Dict[str, Any]]:
        chains = self.client.table("chains").select("*").execute().data
        for c in chains:
            c["executions"] = self.get_chain_executions(c["id"])
        return chains
