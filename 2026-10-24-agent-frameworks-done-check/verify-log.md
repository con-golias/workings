# Verify log (hand re-checks of the first-pass keyword sweeps)

23 Oct 2026 ~20:55 UTC, group A, re-read in the source:
- LangChain middleware export list (`middleware/__init__.py:54-87`) ✔
- `PIIMiddleware` defaults `apply_to_output=False`, `apply_to_tool_results=False` (`pii.py:583-587`) ✔
- LangGraph `_default_handle_tool_errors` re-raises non-argument errors (`tool_node.py:391-399`) ✔
- `create_agent` ToolNode without `handle_tool_errors` (`factory.py:1141-1145`) ✔
- LangChain.js `defaultHandleToolErrors` catches all, "Please fix your mistakes." (`ToolNode.ts:118-139`) ✔
- LlamaIndex tool exception → `ToolOutput(content=str(e), is_error=True)` (`base_agent.py:375-389`) ✔
- Haystack `hooks = hooks or {}` (`agent.py:528`), `raise_on_tool_invocation_failure=False` (`agent.py:432`),
  shipped hook folders: budget, compaction, human_in_the_loop, structured_output, tool_result_offloading ✔

Read directly in the source (no first pass):
- CrewAI `HallucinationGuardrail` open-source = no-op, returns `True, task_output.raw`
  (`lib/crewai/src/crewai/tasks/hallucination_guardrail.py:1-3, 73-77, 95-103`) ✔
- Mastra scorers fire via `executeHook` → `setImmediate` "do not block the main thread"
  (`packages/core/src/hooks/index.ts:25-30`); `runScorer` not awaited in `agent.ts:7564` ✔
- OpenAI Agents (py) output guardrail signature `(context, agent, agent_output)` (`guardrail.py:145-152`);
  docs: "Output guardrails always run after the agent completes" (`docs/guardrails.md:54`) ✔

23 Oct ~21:20 UTC, groups B and C, re-read in the source:
- OpenAI py `default_tool_error_function` fixed string (`tool.py:1997-2002`) ✔ · OpenAI js same (`tool.ts:1736-1738`) ✔
- OpenAI js guardrail `details.output` "Model output items generated during the run" (`guardrail.ts:161-177`) ✔
- Pydantic AI docs "Any other exception propagates…" (`docs/tools-advanced.md:592`); `on_tool_execute_error` → `raise error` ✔
- Mastra faithfulness `options?.context ?? getToolInvocationContext(run.output)` (`faithfulness/index.ts:65`) ✔;
  docs "Live evaluations run in the background without blocking your agent responses" (`overview.mdx:106`) ✔
- Dify `sensitive_word_avoidance` default `{"enabled": False}` (`manager.py:97`) ✔
- Claude Agent SDK `_tool_error_result` → `"isError": True` (`__init__.py:472-475`) ✔
- ADK `HallucinationsV1Evaluator` docstring (`hallucinations_v1.py:262-272`) ✔; tool exception re-raised (`_caller.py:582-595`) ✔;
  `after_model_callback` docstring (`llm_agent.py:509-523`) ✔
- smolagents `check_function(final_answer, self.memory, agent=self)` → `AgentError` ✔
- Agno `OutputCheckError` handler keeps non-None content (`_run.py:692-711`) ✔
- CrewAI WARN default (`tool_failure.py:66-67`) ✔; `LLMGuardrail` prompt has only result + guardrail (`llm_guardrail.py:77-91`) ✔
Not re-verified by hand (kept out of the article or labelled): AutoGen transform details, Semantic Kernel
.NET strings, Vercel `error-json` serialization of Error objects, Mastra/Dify streaming order details,
Claude Agent SDK hook timing.
