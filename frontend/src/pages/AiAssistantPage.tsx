import React, { useState, useRef, useEffect } from "react";
import { Send, Sparkles } from "lucide-react";
import { api } from "../api/client";
import { Card } from "../components/ui";

interface Msg { role: "user" | "talia"; text: string; }

const PROMPTS = [
  "Show status of Aarav Sharma",
  "Find candidates with Python and PyTorch",
  "What are our open positions?",
  "Who is the top applicant for AI/ML Engineer?",
];

export default function AiAssistantPage() {
  const [messages, setMessages] = useState<Msg[]>([
    { role: "talia", text: "Hi! I'm Talia, your recruitment assistant. Ask me about application status, candidate eligibility, open positions, or top applicants for a role." },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages]);

  async function send(text: string) {
    if (!text.trim()) return;
    setMessages((m) => [...m, { role: "user", text }]);
    setInput("");
    setLoading(true);
    try {
      const res = await api.post("/chatbot/message", { message: text });
      setMessages((m) => [...m, { role: "talia", text: res.data.reply }]);
    } catch {
      setMessages((m) => [...m, { role: "talia", text: "Sorry, I couldn't process that just now." }]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)]">
      <Card className="flex-1 flex flex-col overflow-hidden p-0">
        <div className="px-5 py-4 border-b border-slate-100 flex items-center gap-2">
          <Sparkles size={16} className="text-accent-teal" />
          <span className="font-display font-semibold">Talia</span>
          <span className="text-xs text-slate-400">Recruitment Assistant</span>
        </div>

        <div className="flex-1 overflow-y-auto px-5 py-4 space-y-3 scrollbar-thin">
          {messages.map((m, i) => (
            <div key={i} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
              <div className={`max-w-md px-4 py-2.5 rounded-2xl text-sm whitespace-pre-line ${
                m.role === "user" ? "bg-accent-blue text-white rounded-br-sm" : "bg-surface text-navy rounded-bl-sm"
              }`}>
                {m.text}
              </div>
            </div>
          ))}
          {loading && <p className="text-xs text-slate-400">Talia is thinking...</p>}
          <div ref={bottomRef} />
        </div>

        <div className="px-5 py-3 border-t border-slate-100">
          <div className="flex flex-wrap gap-2 mb-3">
            {PROMPTS.map((p) => (
              <button key={p} onClick={() => send(p)}
                className="text-xs px-3 py-1.5 rounded-full bg-surface border border-slate-200 hover:bg-slate-100">
                {p}
              </button>
            ))}
          </div>
          <form onSubmit={(e) => { e.preventDefault(); send(input); }} className="flex gap-2">
            <input value={input} onChange={(e) => setInput(e.target.value)}
              placeholder="Ask Talia anything about your pipeline..."
              className="flex-1 px-4 py-2.5 text-sm rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-accent-blue/30" />
            <button type="submit" className="bg-navy text-white px-4 rounded-lg">
              <Send size={16} />
            </button>
          </form>
        </div>
      </Card>
    </div>
  );
}
