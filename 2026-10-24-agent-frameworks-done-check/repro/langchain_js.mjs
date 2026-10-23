// Does a LangChain.js v1 agent stop, or tell the model, when a tool throws?
import { createAgent, tool } from "langchain";
import { BaseChatModel } from "@langchain/core/language_models/chat_models";
import { AIMessage } from "@langchain/core/messages";
import { z } from "zod";

class FakeToolModel extends BaseChatModel {
  constructor(script) { super({}); this.script = script; this.i = 0; this.seen = []; }
  _llmType() { return "fake-tool-model"; }
  bindTools() { return this; }
  async _generate(messages) {
    this.seen.push(messages.map((m) => `${m.getType()}: ${typeof m.content === "string" ? m.content : JSON.stringify(m.content)}`));
    const message = this.script[this.i++];
    return { generations: [{ text: message.content ?? "", message }] };
  }
}

const cancelOrder = tool(async () => { throw new Error("payment provider timeout"); },
  { name: "cancel_order", description: "Cancel an order.", schema: z.object({ order_id: z.string() }) });

const model = new FakeToolModel([
  new AIMessage({ content: "", tool_calls: [{ name: "cancel_order", args: { order_id: "1042" }, id: "call_1" }] }),
  new AIMessage({ content: "Done! Your order #1042 has been cancelled." }),
]);
const agent = createAgent({ model, tools: [cancelOrder] });
try {
  const out = await agent.invoke({ messages: [{ role: "user", content: "Cancel order 1042" }] });
  for (const m of out.messages) console.log(m.getType(), "|", m.status ?? "", "|", JSON.stringify(m.content));
  console.log("--- what the model saw on its 2nd call:"); console.log(model.seen[1]?.join("\n"));
} catch (e) { console.log("RUN STOPPED WITH EXCEPTION:", e.name, e.message); }
