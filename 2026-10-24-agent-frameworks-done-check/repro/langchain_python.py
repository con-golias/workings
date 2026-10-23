# Does a LangChain v1 agent stop, or tell the model, when a tool raises?
from typing import Any
from langchain.agents import create_agent
from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage
from langchain_core.tools import tool

class FakeToolModel(GenericFakeChatModel):
    def bind_tools(self, tools: Any, **kwargs: Any):
        return self

@tool
def cancel_order(order_id: str) -> str:
    """Cancel an order."""
    raise RuntimeError("payment provider timeout")

model = FakeToolModel(messages=iter([
    AIMessage(content="", tool_calls=[{"name": "cancel_order", "args": {"order_id": "1042"}, "id": "call_1"}]),
    AIMessage(content="Done! Your order #1042 has been cancelled."),
]))
agent = create_agent(model, tools=[cancel_order])
try:
    out = agent.invoke({"messages": [{"role": "user", "content": "Cancel order 1042"}]})
    for m in out["messages"]:
        print(type(m).__name__, "|", getattr(m, "status", ""), "|", m.content)
except Exception as e:
    print("RUN STOPPED WITH EXCEPTION:", type(e).__name__, e)
