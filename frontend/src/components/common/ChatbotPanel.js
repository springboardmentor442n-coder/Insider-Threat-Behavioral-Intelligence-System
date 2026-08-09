import React, { useState, useRef, useEffect } from 'react';
import { MessageSquare, Send, X, ShieldAlert, Sparkles, HelpCircle } from 'lucide-react';
import axios from 'axios';

// Simple helper to parse basic markdown elements returned by the security NLP engine
function parseMarkdown(text) {
  if (!text) return '';
  let html = text;

  // Replace headers
  html = html.replace(/### (.*)/g, '<h4 class="text-xs font-bold text-cyber-primary uppercase tracking-wider mb-2 mt-4 flex items-center gap-1">$1</h4>');
  html = html.replace(/#### (.*)/g, '<h5 class="text-[11px] font-bold text-cyber-accent uppercase tracking-wider mb-1 mt-3">$1</h5>');

  // Replace Bold
  html = html.replace(/\*\*(.*?)\*\*/g, '<strong class="text-white font-semibold">$1</strong>');
  
  // Replace Code blocks
  html = html.replace(/`(.*?)`/g, '<code class="bg-[#1E2D4A] px-1 py-0.5 rounded text-[10px] text-cyber-primary font-mono">$1</code>');

  // Replace Blockquotes
  html = html.replace(/^> (.*)/gm, '<div class="border-l-2 border-cyber-secondary pl-3 py-1 italic my-2 bg-cyber-secondary/5 text-gray-300">$1</div>');

  // Parse tables
  const lines = html.split('\n');
  let inTable = false;
  let tableRows = [];
  let tableHeaders = [];
  
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    if (line.startsWith('|') && line.endsWith('|')) {
      const columns = line.split('|').map(c => c.trim()).filter((_, idx, arr) => idx > 0 && idx < arr.length - 1);
      
      if (line.includes('---')) {
        // Divider row
        continue;
      }
      
      if (!inTable) {
        inTable = true;
        tableHeaders = columns;
      } else {
        tableRows.push(columns);
      }
      lines[i] = ''; // clear it
    } else {
      if (inTable) {
        // Build table html
        const headerHtml = tableHeaders.map(h => `<th class="px-2 py-1 bg-cyber-border text-left font-bold text-[9px] text-gray-400 uppercase">${h}</th>`).join('');
        const rowsHtml = tableRows.map(row => `<tr>${row.map(cell => `<td class="px-2 py-1.5 border-b border-cyber-border/40 text-[10px] text-gray-300">${cell}</td>`).join('')}</tr>`).join('');
        const tableHtml = `<div class="overflow-x-auto my-3"><table class="w-full border-collapse"><thead><tr>${headerHtml}</tr></thead><tbody>${rowsHtml}</tbody></table></div>`;
        
        // Find first empty line index that was cleared to inject
        lines[i - tableRows.length - 2] = tableHtml;
        inTable = false;
        tableRows = [];
        tableHeaders = [];
      }
    }
  }
  
  html = lines.filter(l => l !== '').join('\n');

  // Parse bullet points
  html = html.replace(/^\- (.*)/gm, '<li class="ml-4 list-disc pl-1 text-gray-300 text-[11px] mb-1">$1</li>');

  // Newlines to breaks (if not inside tables or list tag boundaries)
  html = html.replace(/\n/g, '<br/>');

  return html;
}

const QUICK_PROMPTS = [
  "Show suspicious employees today",
  "Why is employee EMP001 risky?",
  "Explain today's alerts",
  "Summarize weekly threats",
  "Suggest mitigation steps"
];

export default function ChatbotPanel() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    {
      sender: 'bot',
      text: "🛡️ **Insider Threat Security Console AI Agent Online**\n\nI can retrieve real-time activity baselines, identify anomalies, and provide SHAP model explainability audits for any employee in the identity registry. What threats should we investigate?"
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const token = localStorage.getItem('access_token');
  const BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isOpen]);

  const handleSend = async (textToSend) => {
    const query = textToSend || input;
    if (!query.trim()) return;

    setMessages(prev => [...prev, { sender: 'user', text: query }]);
    if (!textToSend) setInput('');
    setLoading(true);

    try {
      const response = await axios.post(
        `${BASE_URL}/chatbot/query`,
        { query },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      setMessages(prev => [...prev, { sender: 'bot', text: response.data.response }]);
    } catch (err) {
      console.error(err);
      setMessages(prev => [...prev, {
        sender: 'bot',
        text: "❌ **Failed to contact threat intelligence backend.** Make sure you are logged in as a security analyst."
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      {/* Floating Toggle Button */}
      <button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-6 right-6 z-50 flex h-14 w-14 items-center justify-center rounded-full bg-gradient-to-tr from-cyber-secondary to-cyber-primary text-cyber-bg shadow-glow-primary hover:scale-105 active:scale-95 transition-all duration-200"
        title="Open Security Assistant"
      >
        <MessageSquare size={24} className="animate-pulse" />
      </button>

      {/* Floating Panel Panel */}
      {isOpen && (
        <div className="fixed inset-y-0 right-0 z-50 flex w-96 flex-col border-l border-cyber-border bg-[#070B17]/95 shadow-2xl backdrop-blur-xl animate-in slide-in-from-right duration-300">
          
          {/* Header */}
          <div className="flex items-center justify-between border-b border-cyber-border p-4 bg-cyber-card/80">
            <div className="flex items-center gap-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-cyber-secondary/20 text-cyber-secondary">
                <Sparkles size={16} />
              </div>
              <div>
                <div className="text-xs font-bold text-white tracking-wide">SOC INTEL ASSISTANT</div>
                <div className="text-[9px] text-cyber-accent font-bold flex items-center gap-1">
                  <span className="live-dot-critical w-1.5 h-1.5"></span> LIVE SEC-AUDIT MODE
                </div>
              </div>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="rounded-lg p-1 text-gray-400 hover:bg-cyber-border hover:text-white"
            >
              <X size={18} />
            </button>
          </div>

          {/* Messages Feed */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4 scrollbar-thin">
            {messages.map((msg, idx) => (
              <div
                key={idx}
                className={`flex flex-col max-w-[85%] ${
                  msg.sender === 'user' ? 'ml-auto items-end' : 'mr-auto items-start'
                }`}
              >
                <div
                  className={`rounded-2xl px-3 py-2 text-[11px] leading-relaxed select-text ${
                    msg.sender === 'user'
                      ? 'bg-cyber-secondary text-white rounded-tr-none'
                      : 'bg-cyber-card border border-cyber-border text-gray-300 rounded-tl-none font-sans'
                  }`}
                  dangerouslySetInnerHTML={{ __html: parseMarkdown(msg.text) }}
                />
              </div>
            ))}
            {loading && (
              <div className="flex items-center gap-2 text-cyber-primary text-[10px] bg-cyber-card/40 border border-cyber-border/40 rounded-xl px-3 py-1.5 w-max">
                <div className="animate-bounce">●</div>
                <div className="animate-bounce delay-75">●</div>
                <div className="animate-bounce delay-150">●</div>
                <span className="font-mono ml-1 font-bold">Querying ML models & baseline matrices...</span>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Quick Prompts Panel */}
          {messages.length === 1 && (
            <div className="p-3 border-t border-cyber-border/40 bg-cyber-card/20 space-y-1.5">
              <div className="text-[9px] font-bold text-cyber-muted uppercase tracking-wider mb-1 flex items-center gap-1">
                <HelpCircle size={10} /> Suggested Queries
              </div>
              <div className="flex flex-wrap gap-1.5">
                {QUICK_PROMPTS.map((p, i) => (
                  <button
                    key={i}
                    onClick={() => handleSend(p)}
                    className="text-[9px] bg-cyber-border hover:bg-cyber-border/80 border border-cyber-border/80 hover:border-cyber-primary/50 text-gray-300 hover:text-white px-2 py-1 rounded-lg transition-all"
                  >
                    {p}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Form Input */}
          <div className="border-t border-cyber-border p-3 bg-cyber-card/50">
            <div className="flex items-center gap-2">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                placeholder="Ask me: Why is employee 205 risky?"
                className="flex-1 rounded-lg bg-cyber-bg border border-cyber-border px-3 py-2 text-xs text-white placeholder-gray-500 outline-none focus:border-cyber-primary focus:ring-1 focus:ring-cyber-primary"
              />
              <button
                onClick={() => handleSend()}
                disabled={loading}
                className="flex h-8 w-8 items-center justify-center rounded-lg bg-cyber-primary text-cyber-bg hover:scale-105 active:scale-95 transition-all shadow-glow-primary"
              >
                <Send size={14} />
              </button>
            </div>
          </div>

        </div>
      )}
    </>
  );
}
