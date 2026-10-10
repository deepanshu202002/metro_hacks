import { useState, useRef, useEffect } from "react";
import { Send, Bot, User, Mic, MicOff, Volume2, VolumeX } from "lucide-react";

export default function ChatPanel({ onRouteFound }) {
  const [messages, setMessages] = useState([
    { role: "assistant", content: "Hi! I'm your One Journey assistant. Where would you like to go in Ahmedabad or Gandhinagar?" }
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [speakAnswers, setSpeakAnswers] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim()) return;
    
    const userMsg = input;
    setMessages(prev => [...prev, { role: "user", content: userMsg }]);
    setInput("");
    setIsLoading(true);

    try {
      // Mock call to /api/explain or /api/parse
      // In a real app this would go to the FastAPI backend agent
      setTimeout(() => {
        setMessages(prev => [...prev, { 
          role: "assistant", 
          content: "I've planned a route for you. You can take the Red Line towards Mahatma Mandir." 
        }]);
        
        // Mock route found trigger
        onRouteFound({
          metro_only: { time: 40, fare: 30, transfers: 0 }
        });
        
        setIsLoading(false);
      }, 1500);
    } catch (e) {
      console.error(e);
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-surface-hover/30 backdrop-blur-md">
      <div className="p-4 border-b border-border bg-surface/90 backdrop-blur flex justify-between items-center z-10 shadow-sm">
        <div className="flex items-center gap-3">
          <div className="bg-gradient-to-br from-primary to-transit-blue p-2 rounded-xl shadow-sm">
            <Bot size={20} className="text-white" />
          </div>
          <div>
            <h2 className="font-bold text-foreground leading-tight">Journey Agent</h2>
            <p className="text-[10px] text-primary font-medium tracking-wide uppercase">AI Assistant</p>
          </div>
        </div>
        <button 
          onClick={() => setSpeakAnswers(!speakAnswers)}
          className={`p-2.5 rounded-full transition-colors active:scale-95 ${speakAnswers ? 'text-primary bg-primary/10' : 'text-foreground-muted hover:text-foreground hover:bg-surface'}`}
          title="Toggle Voice Output"
        >
          {speakAnswers ? <Volume2 size={18} /> : <VolumeX size={18} />}
        </button>
      </div>
      
      <div className="flex-1 overflow-y-auto p-5 space-y-5 scrollbar-thin scrollbar-thumb-border">
        {messages.map((msg, idx) => (
          <div key={idx} className={`flex gap-3 max-w-[92%] animate-in fade-in slide-in-from-bottom-2 ${msg.role === "user" ? "ml-auto flex-row-reverse" : ""}`}>
            <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 shadow-sm ${
              msg.role === "user" ? "bg-surface border border-border" : "bg-surface border border-border"
            }`}>
              {msg.role === "user" ? <User size={15} className="text-foreground-muted" /> : <Bot size={15} className="text-primary" />}
            </div>
            <div className={`p-3.5 rounded-2xl text-[13px] md:text-sm leading-relaxed shadow-sm ${
              msg.role === "user" 
                ? "bg-primary text-primary-foreground rounded-tr-sm" 
                : "bg-surface border border-border text-foreground rounded-tl-sm"
            }`}>
              {msg.content}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex gap-3 max-w-[92%] animate-in fade-in slide-in-from-bottom-2">
             <div className="w-8 h-8 rounded-full bg-surface border border-border flex items-center justify-center shadow-sm">
              <Bot size={15} className="text-primary" />
            </div>
            <div className="px-4 py-3 bg-surface border border-border rounded-2xl rounded-tl-sm text-foreground-muted flex items-center gap-1.5 shadow-sm">
              <span className="w-1.5 h-1.5 bg-foreground-muted/60 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
              <span className="w-1.5 h-1.5 bg-foreground-muted/60 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
              <span className="w-1.5 h-1.5 bg-foreground-muted/60 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="p-4 bg-surface/90 backdrop-blur border-t border-border z-10">
        <div className="relative flex items-center shadow-sm rounded-full bg-surface border border-border">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSend()}
            placeholder="Ask anything..."
            className="w-full bg-transparent py-3.5 pl-5 pr-24 text-[14px] text-foreground placeholder-foreground-muted focus:outline-none rounded-full"
            aria-label="Message Input"
          />
          <div className="absolute right-1.5 flex items-center gap-1">
            <button 
              onClick={() => setIsRecording(!isRecording)}
              className={`p-2.5 rounded-full transition-colors active:scale-95 ${isRecording ? 'bg-transit-red/10 text-transit-red animate-pulse' : 'text-foreground-muted hover:text-foreground hover:bg-surface-hover'}`}
              aria-label="Voice Input"
            >
              {isRecording ? <MicOff size={18} /> : <Mic size={18} />}
            </button>
            <button 
              onClick={handleSend}
              disabled={!input.trim() || isLoading}
              className="p-2.5 bg-primary hover:bg-primary/90 disabled:opacity-50 disabled:hover:bg-primary text-primary-foreground rounded-full transition-all active:scale-95 shadow-md mr-0.5"
              aria-label="Send Message"
            >
              <Send size={16} className="ml-0.5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
