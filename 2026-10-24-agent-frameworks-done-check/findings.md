# Findings, per framework (audited commits in `frameworks.csv`)

> Paths relative to each repo root. "Verified" = re-read by hand after the first-pass sweep
> (see `verify-log.md`). Q1 output hook · Q2 shipped claim-vs-tool check · Q3 default semantic
> check · Q4 what the model gets when a tool raises.

## Group A

### LangChain (Python, `libs/langchain_v1`, `create_agent`)
- **Q1** Yes: middleware `after_model` / `after_agent` (`agents/middleware/types.py:479`, `:650`);
  receives full `AgentState` incl. `messages` (tool calls + ToolMessages); can jump to
  `model`/`tools`/`end`.
- **Q2** None. Shipped middleware (`middleware/__init__.py`): ContextEditing, FilesystemFileSearch,
  HumanInTheLoop, LLMToolSelector, ModelCallLimit, ModelFallback, ModelRetry, PII,
  ProviderToolSearch, ShellTool, Summarization, TodoList, ToolCallLimit, ToolError, ToolRetry.
  Closest: `PIIMiddleware` (regex PII; `apply_to_output=False` by default, `pii.py:586`).
  Offline only: legacy `TrajectoryEvalChain` (LLM judge of tool use quality, not a gate).
- **Q3** None by default (structured `response_format` = schema only).
- **Q4** `create_agent` builds LangGraph `ToolNode` without `handle_tool_errors`
  (`factory.py:1141-1145`); LangGraph default returns the message only for argument errors and
  **re-raises everything else** (`langgraph/libs/prebuilt/langgraph/prebuilt/tool_node.py:391-399`).
  Opt-in `ToolErrorMiddleware` turns exceptions into `ToolMessage(status="error")`. ✔ verified

### LangChain.js (`libs/langchain/src/agents`)
- **Q1** Yes: `afterModel` / `afterAgent` middleware (`middleware/types.ts:594`, `:604`), state incl. messages.
- **Q2** None (middleware: contextEditing, dynamicSystemPrompt, hitl, llmToolSelector, modelCallLimit,
  modelFallback, modelRetry, pii, piiRedaction, providerToolSearch, summarization, todoList,
  toolCallLimit, toolEmulator, toolError, toolRetry). PII `applyToOutput` defaults false.
- **Q3** None.
- **Q4** Catches all tool errors: `ToolMessage({content: \`${error}\n Please fix your mistakes.\`, status: "error"})`
  (`nodes/ToolNode.ts:118-139`). ✔ verified

### LangGraph
- **Q1** No dedicated hook (graph runtime: add your own node). Prebuilt `create_react_agent` has
  `post_model_hook` ("guardrails, validation…", `chat_agent_executor.py:425-427`), but is
  deprecated in favour of `langchain.agents.create_agent`.
- **Q2** None. **Q3** None. **Q4** as LangChain Python (re-raise except argument errors).

### LlamaIndex (`llama-index-core`, agent workflow)
- **Q1** No documented output hook; closest is overriding `finalize()` in a subclass
  (`agent/workflow/base_agent.py:272-275`).
- **Q2** None at runtime. `FaithfulnessEvaluator` (`evaluation/faithfulness.py`) = offline LLM judge
  of response vs **retrieved contexts**, not tool calls; not wired into the agent.
- **Q3** None (`output_cls` = schema only; failures only warn).
- **Q4** Caught; model gets `str(e)`; `is_error=True` stays on the Python object, not in the chat
  message (`base_agent.py:375-389`; `function_agent.py:155-161`). ✔ verified (first part)

### Haystack (`components/agents/agent.py`)
- **Q1** Yes: hooks `on_exit` / `after_run` (`hooks/protocol.py:10`), receive live `State` incl. messages.
  The docs example `require_save` forces a tool call before finishing: a pattern the developer writes.
- **Q2** None. Shipped hooks: budget, compaction, human_in_the_loop, structured_output,
  tool_result_offloading. `FaithfulnessEvaluator` = offline LLM judge vs contexts.
- **Q3** None (`hooks = hooks or {}`, `agent.py:528`).
- **Q4** Caught by default (`raise_on_tool_invocation_failure=False`, `agent.py:432`); model gets the
  error string with `error=True` on the tool message (`tool_calling.py:507-510`). ✔ verified (defaults)

## Group B

### CrewAI (`lib/crewai/src/crewai`)
- **Q1** Yes: `Task.guardrail(s)` (`task.py:252-272`), callable gets `TaskOutput` incl. `messages` and
  `tool_failures`; can rewrite (`task.py:1365-1377`); blocks by retry (default 3) then raises.
  A **string** guardrail becomes `LLMGuardrail`, whose judge prompt contains only the task result and
  the guardrail text, no tool calls (`tasks/llm_guardrail.py:77-91`). ✔ verified
- **Q2** `HallucinationGuardrail` exists and accepts `tool_response`, but the open-source version is a
  **no-op that always passes** ("Hallucination detection is a no-op in open source, use it for free at
  https://app.crewai.com"; `return True, task_output.raw`, `tasks/hallucination_guardrail.py:73-77, 95-103`).
  The working version is in CrewAI's hosted product, not in the repo. ✔ verified
- **Q3** None by default. `tool_failure_policy` default **WARN**: "Record the failure, emit an event,
  and keep going. The default." (`tools/tool_failure.py:66-67`). ✔ verified
- **Q4** Model gets text: `f"Error executing tool: {e}"` (`utilities/agent_utils.py:1609-1611`), plus
  a structured failure record kept by the framework.

### AutoGen (`python/packages/autogen-agentchat`)
- **Q1** No final-output hook on `AssistantAgent`; autogen-core `InterventionHandler` (runtime level,
  one message at a time, SingleThreadedAgentRuntime only).
- **Q2** None. Note: default `reflect_on_tool_use=False` returns a `ToolCallSummaryMessage` built from
  the tool results themselves (`"{result}"`), so after a tool call the reply is not an LLM claim.
- **Q3** None. **Q4** error string to the model; `is_error` kept internally, not sent in the OpenAI
  tool message (`autogen-ext/.../openai/_message_transform.py:444`).

### Semantic Kernel (Python and .NET)
- **Q1** Filters (function invocation, prompt rendering, auto function invocation). `ChatCompletionAgent`
  calls the chat service directly, so no function-invocation filter wraps the agent's final reply;
  the auto-function filter runs per tool call with `chat_history`.
- **Q2** None in the package. Grounding checks exist only as **samples** (GroundingPlugin prompts,
  `08-groundedness-checking.ipynb`, `GroundednessChecks.cs`), LLM judge vs a grounding context.
- **Q3** None. **Q4** error string: Python `"An error occurred while invoking the function …: {exc}"`
  (`kernel.py:477-487`); .NET `"Error: Exception while invoking function. {e.Message}"`.

### Google ADK (`src/google/adk`)
- **Q1** Yes: `after_model_callback` — "A truthy response replaces the model response"
  (`agents/llm_agent.py:509-523`); session events (incl. function calls/responses) reachable. ✔ verified
- **Q2** Offline only: `HallucinationsV1Evaluator` — LLM judge, per-sentence supported / unsupported /
  contradictory, with **tool calls and tool outputs in its context** (`evaluation/hallucinations_v1.py:262-272`,
  `:314-327`, `:472-505`). An eval metric, not wired into the runtime. ✔ verified (docstring)
- **Q3** None. **Q4** **exception propagates** unless an `on_tool_error_callback` returns a response
  (`flows/llm_flows/tools/_caller.py:582-595`). ✔ verified

### smolagents
- **Q1** Yes: `final_answer_checks`, called as `check_function(final_answer, self.memory, agent=self)`;
  failure → `AgentError`, the run continues (retry), no rewrite (`agents.py:589-618`). ✔ verified
  Docs describe the signature without memory (`guided_tour.md:394-397`).
- **Q2** None. **Q3** None (`[]` by default). **Q4** error text to the model:
  "Error executing tool '…' … Please try again or use another tool" (`agents.py:1490-1502`).

### Agno (`libs/agno/agno`)
- **Q1** Yes: `post_hooks` with `run_output` (incl. `tools: List[ToolExecution]`). Blocking = raise
  `OutputCheckError`; the handler sets `status = error` but only replaces `content` **if it is None**
  (`agent/_run.py:692-711`), so the original text stays in the returned object unless the caller checks
  `status`. In streaming, post-hooks run after the content was streamed. ✔ verified (handler)
- **Q2** None. Shipped guardrails (PII, prompt injection, OpenAI moderation) check **input**.
  `AgentAsJudgeEval` judges input/output text only; `ReliabilityEval` compares tool calls with expected
  ones (offline).
- **Q3** None. **Q4** error string to the model; `FunctionExecutionResult(status="failure")` internal.

## Group C

### OpenAI Agents SDK (Python)
- **Q1** Output guardrails; function gets `(context, agent, agent_output)` only — **no tool items**
  (`guardrail.py:145-152`); block by tripwire exception, cannot rewrite; "always run after the agent
  completes" (`docs/guardrails.md:54`). Streaming: raw token events are queued as they arrive, so a
  streaming client sees text before the guardrail decides. ✔ verified (signature, docs)
- **Q2** None shipped. **Q3** None (output_type = schema only).
- **Q4** Fixed string: `"An error occurred while running the tool. Please try again."`
  (`tool.py:1997-2002`). ✔ verified

### OpenAI Agents SDK (JS)
- **Q1** Output guardrails **do** receive `details.output` = generated items incl. tool calls/results
  (`agents-core/src/guardrail.ts:161-177`). Block only. ✔ verified
- **Q2** None. **Q3** None. **Q4** same fixed string (`tool.ts:1736-1738`). ✔ verified

### Pydantic AI
- **Q1** `@agent.output_validator` with `RunContext.messages` (full history); can `raise ModelRetry`
  or return a modified value. Docs: delta text streaming "skips validators" (`docs/output.md:962`).
- **Q2** None at runtime. `pydantic_evals` has deterministic tool-trajectory evaluators vs an
  **expected** trajectory (offline).
- **Q3** None (schema only).
- **Q4** **Propagates**: "Any other exception propagates out of the agent run and is not sent back to
  the model." (`docs/tools-advanced.md:592`; default `on_tool_execute_error` → `raise error`). ✔ verified

### Mastra
- **Q1** Output processors (`processOutputStream`, `processOutputResult` with `result.steps` incl.
  toolCalls/toolResults, `processOutputStep`); `abort({retry})`. `processOutputResult` runs after the
  stream finished. Opt-in `isTaskComplete` scorers can loop the agent.
- **Q2** Closest shipped artifact anywhere: the **faithfulness scorer** uses tool results as context
  by default (`context ?? getToolInvocationContext(run.output)`, `evals/src/scorers/llm/faithfulness/index.ts:19-26, 65`),
  LLM judge. But agent scorers **only observe**: "Live evaluations run in the background without
  blocking your agent responses" (`docs/.../evals/overview.mdx:106`; `setImmediate` in `hooks/index.ts`). ✔ verified
  Hallucination scorer: context only if the developer supplies it.
- **Q3** None semantic. **Q4** error text as a tool result with `outcome.kind = 'error'`.

### Vercel AI SDK (`packages/ai`)
- **Q1** No agent-level final-output hook; language-model middleware `wrapGenerate`/`wrapStream` per
  model call (docs show a redaction "guardrail" example). `onStepFinish`/`onFinish` callbacks.
- **Q2** None (shipped middleware: default-settings, extract-json, extract-reasoning, simulate-streaming,
  add-tool-input-examples, default-instructions). **Q3** None.
- **Q4** caught → `tool-error` part, serialized as `error-json` to the model. (Unverified: whether a plain
  `Error` serializes to `{}`; not claimed.)

### Claude Agent SDK (Python)
- **Q1** Hooks `Stop`/`SubagentStop` (gets `last_assistant_message`, `transcript_path`), `PostToolUse`
  (`tool_input`, `tool_response`), `PostToolUseFailure`. A Stop block makes the agent continue with
  feedback; no field rewrites an already-produced message. Hooks are executed by the bundled CLI.
- **Q2** None. **Q3** None.
- **Q4** in-process SDK MCP tools: `str(e)` with `"isError": True` (`__init__.py:472-475, 620-641`). ✔ verified

### Dify (`api/`)
- **Q1** Output moderation ("sensitive_word_avoidance"): sees **text only**
  (`core/moderation/base.py:67-75`), can replace; runs on buffered chunks while streaming continues.
- **Q2** None (only "hallucinated tool names" in the workflow *generator*).
- **Q3** Off: `config.get("sensitive_word_avoidance") or {"enabled": False}` (`manager.py:97`). ✔ verified
- **Q4** string to the LLM: `"tool invoke error: {e}"` / `"unknown error: {e}"` (`core/tools/tool_engine.py:130-157`).
