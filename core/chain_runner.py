# core/chain_runner.py
from typing import Dict, List, Any
from core.agent import AgentSpec, AgentResult
from infrastructure.llm_service import LLMService, LLMProvider, AgentMetrics
from infrastructure.supabase_store import SupabaseStore
import logging, time

logger = logging.getLogger(__name__)

class ChainRunner:
    def __init__(self, llm_service: LLMService, store: SupabaseStore, available_tools: Dict[str, Any]):
        self.llm_service = llm_service
        self.store = store
        self.available_tools = available_tools

    def start_chain(self, goal: str, selected_tools: List[str]) -> str:
        spec = AgentSpec(goal=goal, tools=selected_tools, continue_chain=True)
        chain_id = self.store.create_chain(goal)
        logger.info(f"Chain {chain_id} started with goal: {goal}")
        return chain_id

    def execute_next_agent(self, chain_id: str, spec: AgentSpec) -> AgentResult:
        start = time.time()
        tools = {n: t for n,t in self.available_tools.items() if n in spec.tools}
        try:
            result, metrics = self.llm_service.generate_agent_execution(spec, tools)
            self.store.store_agent_execution(chain_id, spec, result, metrics)
            logger.info(f"Agent run in {time.time()-start:.2f}s")
            return result
        except Exception as e:
            err = str(e)
            logger.error(err)
            failed = AgentResult(execution_result={}, errors=[err])
            self.store.store_agent_execution(chain_id, spec, failed)
            return failed
