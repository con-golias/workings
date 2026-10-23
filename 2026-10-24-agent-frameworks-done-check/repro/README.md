# Reproductions (run 23 Oct 2026, Linux, Python 3.13 / Node 22)

Same scenario in both: the user asks to cancel order 1042; a scripted fake model calls `cancel_order`;
the tool throws `payment provider timeout`; the model's next scripted reply is
"Done! Your order #1042 has been cancelled."

The fake model is scripted on purpose: this tests what the **framework** does, not what a real model
would say. A real model may or may not claim success; the framework's behaviour is the same either way.

- `langchain_python.py` → `langchain_python.out`: the run **stops with the exception** (default `create_agent`).
- `langchain_js.mjs` → `langchain_js.out`: the run **continues**; the model receives
  `Error: payment provider timeout\n Please fix your mistakes.` as a tool message with `status: error`,
  and the scripted "Done! … cancelled." reaches the caller unchanged.

Versions: `*.versions`. Install exactly these, or newer releases may behave differently:

```
# Python
python -m venv .venv
pip install langchain==1.4.7 langchain-core==1.7.0 langgraph==1.2.16
python langchain_python.py

# JavaScript (Node 22+)
npm i langchain@1.5.19 @langchain/core@1.3.0 @langchain/langgraph@1.5.2 zod
node langchain_js.mjs
```

Re-run 24 Oct 2026 on Windows 11 (Python 3.11.9, Node 24.19.0, zod 4.6.7) with the same pins:
identical output to `*.out`.
