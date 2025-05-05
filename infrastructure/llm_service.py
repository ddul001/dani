# infrastructure/llm_service.py
from typing import Dict, Any, Tuple
from pydantic import BaseModel, Field
import anthropic, openai, time, logging, streamlit as st, re, json
from enum import Enum
from core.agent import AgentSpec, AgentResult

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMProvider(str, Enum):
    CLAUDE = "claude"
    GPT = "gpt"

class ToolExecution(BaseModel):
    tool_name: str
    input_params: Dict[str, Any]
    output: Any = None
    start_time: float = Field(default_factory=time.time)
    end_time: float = None
    error: str = None
    def complete(self, out): self.output=out; self.end_time=time.time()
    def fail(self,e): self.error=e; self.end_time=time.time()
    @property
    def duration(self): return None if not self.end_time else self.end_time-self.start_time

class AgentMetrics(BaseModel):
    llm_provider: LLMProvider
    tool_executions: list[ToolExecution] = Field(default_factory=list)
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_duration: float = 0
    start_time: float = Field(default_factory=time.time)
    end_time: float = None
    def complete(self): self.end_time=time.time(); self.total_duration=self.end_time-self.start_time

class LLMService:
    def __init__(self, provider=LLMProvider.CLAUDE):
        self.provider=provider; self._setup_client()
    def _setup_client(self):
        if self.provider==LLMProvider.CLAUDE:
            self.client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
        else:
            self.client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    def generate_agent_execution(self, spec:AgentSpec, tools:Dict[str,Any]) -> Tuple[AgentResult,AgentMetrics]:
        metrics=AgentMetrics(llm_provider=self.provider)
        tool_results={}
        for name,tool in tools.items():
            te=ToolExecution(tool_name=name,input_params={"goal":spec.goal})
            try:
                out=tool.execute({"goal":spec.goal})
                te.complete(out)
            except Exception as e:
                te.fail(str(e)); logger.error(te.error)
            metrics.tool_executions.append(te)
            tool_results[name]=te.output
        prompt=self._generate_prompt(spec,tool_results)
        if self.provider==LLMProvider.CLAUDE:
            resp=self.client.messages.create(model="claude-3-sonnet-20240229",max_tokens=2000,messages=[{"role":"user","content":prompt}])
            txt=resp.content[0].text; metrics.prompt_tokens=resp.usage.input_tokens; metrics.completion_tokens=resp.usage.output_tokens
        else:
            resp=self.client.chat.completions.create(model="gpt-4",messages=[{"role":"user","content":prompt}],max_tokens=2000)
            txt=resp.choices[0].message.content; metrics.prompt_tokens=resp.usage.prompt_tokens; metrics.completion_tokens=resp.usage.completion_tokens
        result=self._parse_llm_response(txt)
        metrics.complete()
        return result, metrics
		
		def _generate_prompt(self, spec, results):
			# Build a clean, valid prompt string
			tools_list = ", ".join(spec.tools)
			txt = (
				f"You are DANI, a dynamic auto-adaptive neural intelligence agent.\n"
			   f"Your goal: {spec.goal}\n"
				f"Available tools: {tools_list}\n"
				f"Tool results: {results}\n"
			   "Respond strictly in JSON with keys \"execution_result\" and \"next_agent_spec\"."
			)
			return txt
			
    def _parse_llm_response(self, text):
        try:
            m=re.search(r'```(?:json)?\s*(.*?)\s*```', text, re.DOTALL)
            js=m.group(1) if m else text
            data=json.loads(js)
            res=AgentResult(execution_result=data.get("execution_result",{}))
            nas=data.get("next_agent_spec")
            if nas: res.next_agent_spec=AgentSpec(**nas)
            return res
        except Exception as e:
            logger.error(f"parse error: {e}")
            return AgentResult(execution_result={}, errors=[str(e)])
