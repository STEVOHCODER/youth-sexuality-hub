import { useState, useEffect, useRef } from 'react';
import { Send, Bot, PlusCircle, PanelLeftOpen, PanelRightOpen, Copy, Check, X, Layout, MessageSquare, Trash2, Library, MoreVertical, Calendar as CalendarIcon, Heart, LogOut } from 'lucide-react';

import ReactMarkdown from 'react-markdown';
import rehypeHighlight from 'rehype-highlight';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import 'highlight.js/styles/tokyo-night-dark.css';
import 'katex/dist/katex.min.css';
import { useAuth } from './context/AuthContext';
import { Login } from './components/Login';
import { Register } from './components/Register';

const ProjectMenu = ({ onRename, onDelete }: any) => {
  const [isOpen, setIsOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (e: any) => {
      if (menuRef.current && !menuRef.current.contains(e.target)) setIsOpen(false);
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <div className="relative" ref={menuRef}>
      <button
        onClick={(e) => {
          e.stopPropagation();
          setIsOpen(!isOpen);
        }}
        className="p-1.5 text-[#6b7fa8] hover:text-white rounded-lg"
      >
        <MoreVertical size={14} />
      </button>

      {isOpen && (
        <div className="absolute right-0 top-8 w-40 bg-[#161b22] border border-[#30363d] rounded-xl shadow-2xl z-[60] overflow-hidden animate-in fade-in slide-in-from-top-2">
          <button
            onClick={(e) => {
              e.stopPropagation();
              onRename();
              setIsOpen(false);
            }}
            className="flex items-center gap-2 w-full px-4 py-2.5 text-[11px] font-bold text-[#c9d1d9] hover:bg-[#29d8a8]/10 border-b border-[#30363d]/50"
          >
            RENAME
          </button>
          <button
            onClick={(e) => {
              e.stopPropagation();
              onDelete();
              setIsOpen(false);
            }}
            className="flex items-center gap-2 w-full px-4 py-2.5 text-[11px] font-bold text-red-400 hover:bg-red-400/10"
          >
            DELETE
          </button>
        </div>
      )}
    </div>
  );
};

const CalendarView = ({ events, onAdd }: any) => {
  return (
    <div className="flex-1 bg-[#0d1117] p-8 overflow-y-auto custom-scroll">
      <div className="max-w-4xl mx-auto">
        <div className="flex justify-between items-center mb-10">
          <h2 className="text-2xl font-black text-white tracking-tight flex items-center gap-3">
            <CalendarIcon className="text-[#29d8a8]" /> Schedule
          </h2>

          <button
            onClick={onAdd}
            className="flex items-center gap-2 px-6 py-2.5 bg-[#29d8a8] text-[#0a0c10] font-black text-xs uppercase tracking-widest rounded-full hover:scale-105 transition-all shadow-glow"
          >
            <PlusCircle size={16} /> New Entry
          </button>
        </div>

        <div className="grid gap-4">
          {events.length === 0 ? (
            <div className="text-center py-20 bg-[#161b22] border border-[#30363d] rounded-[2.5rem] opacity-50">
              <CalendarIcon size={40} className="mx-auto mb-4 text-[#6b7fa8]" />
              <p className="text-xs font-bold uppercase tracking-[0.2em] text-[#6b7fa8]">
                Your calendar is clear.
              </p>
            </div>
          ) : (
            events
              .sort((a: any, b: any) => new Date(a.event_date).getTime() - new Date(b.event_date).getTime())
              .map((e: any) => (
                <div
                  key={e.id}
                  className="bg-[#161b22] border border-[#30363d] rounded-[1.5rem] p-6 flex items-center justify-between group hover:border-[#29d8a8]/30 transition-all shadow-xl"
                >
                  <div className="flex items-center gap-6">
                    <div className="w-14 h-14 bg-gradient-to-br from-[#161b22] to-[#0d1117] border border-[#30363d] rounded-2xl flex flex-col items-center justify-center shadow-inner">
                      <span className="text-[10px] font-black text-[#6b7fa8] uppercase">
                        {new Date(e.event_date).toLocaleString('default', { month: 'short' })}
                      </span>
                      <span className="text-lg font-black text-white">
                        {new Date(e.event_date).getDate()}
                      </span>
                    </div>

                    <div>
                      <h4 className="text-sm font-black text-white uppercase tracking-tight">{e.title}</h4>
                      <span className="text-[9px] font-bold text-[#29d8a8] uppercase tracking-[0.2em] mt-1 block">
                        {e.category}
                      </span>
                    </div>
                  </div>

                  <button className="p-2 text-[#6b7fa8] hover:text-red-400 opacity-0 group-hover:opacity-100 transition-all">
                    <Trash2 size={16} />
                  </button>
                </div>
              ))
          )}
        </div>
      </div>
    </div>
  );
};

const PeriodView = ({ entries, onAdd }: any) => {
  return (
    <div className="flex-1 bg-[#0d1117] p-8 overflow-y-auto custom-scroll">
      <div className="max-w-4xl mx-auto">
        <div className="flex justify-between items-center mb-10">
          <h2 className="text-2xl font-black text-white tracking-tight flex items-center gap-3">
            <Heart size={24} className="text-[#ff7eb3]" /> My Cycles
          </h2>

          <button
            onClick={onAdd}
            className="flex items-center gap-2 px-6 py-2.5 bg-[#ff7eb3] text-[#0a0c10] font-black text-xs uppercase tracking-widest rounded-full hover:scale-105 transition-all shadow-[0_0_20px_rgba(255,126,179,0.3)]"
          >
            <PlusCircle size={16} /> Log Period
          </button>
        </div>

        <div className="grid gap-4">
          {entries.length === 0 ? (
            <div className="text-center py-20 bg-[#161b22] border border-[#30363d] rounded-[2.5rem] opacity-50 shadow-inner">
              <Heart size={40} className="mx-auto mb-4 text-[#6b7fa8]" />
              <p className="text-xs font-bold uppercase tracking-[0.2em] text-[#6b7fa8]">
                No data logged yet.
              </p>
            </div>
          ) : (
            entries
              .sort((a: any, b: any) => new Date(b.start_date).getTime() - new Date(a.start_date).getTime())
              .map((e: any) => (
                <div
                  key={e.id}
                  className="bg-[#161b22] border border-[#30363d] rounded-[1.5rem] p-6 flex items-center justify-between group hover:border-[#ff7eb3]/30 transition-all shadow-xl"
                >
                  <div className="flex items-center gap-6">
                    <div className="w-14 h-14 bg-gradient-to-br from-[#161b22] to-[#0d1117] border border-[#ff7eb3]/20 rounded-2xl flex flex-col items-center justify-center">
                      <span className="text-[10px] font-black text-[#ff7eb3] uppercase tracking-tighter">
                        {new Date(e.start_date).toLocaleString('default', { month: 'short' })}
                      </span>
                      <span className="text-lg font-black text-white">
                        {new Date(e.start_date).getDate()}
                      </span>
                    </div>

                    <div>
                      <h4 className="text-sm font-black text-white uppercase tracking-tight italic flex items-center gap-2">
                        Intensity:{' '}
                        <span
                          className={
                            e.intensity === 'heavy'
                              ? 'text-red-400'
                              : e.intensity === 'medium'
                              ? 'text-orange-300'
                              : 'text-yellow-200'
                          }
                        >
                          {e.intensity}
                        </span>
                      </h4>
                      <p className="text-[10px] text-[#6b7fa8] mt-1 font-medium">{e.notes || 'Standard entry'}</p>
                    </div>
                  </div>

                  <div className="flex items-center gap-4">
                    <button
                      onClick={() => {
                        const input = document.getElementById('main-input') as HTMLInputElement;
                        if (input) {
                          input.value = `Hi, can you explain my period log from ${new Date(e.start_date).toLocaleDateString()}? Flow was ${e.intensity}.`;
                          input.focus();
                        }
                      }}
                      className="px-5 py-2 bg-[#0d1117] border border-[#30363d] rounded-full text-[9px] font-black text-[#6b7fa8] hover:text-[#ff7eb3] hover:border-[#ff7eb3] transition-all uppercase tracking-widest shadow-inner"
                    >
                      Consult AI
                    </button>

                    <button className="p-2 text-[#6b7fa8] hover:text-red-400 opacity-0 group-hover:opacity-100 transition-all">
                      <Trash2 size={16} />
                    </button>
                  </div>
                </div>
              ))
          )}
        </div>
      </div>
    </div>
  );
};

export default function App() {
  const { isAuthenticated, loading, logout, user } = useAuth();

  // 🔥 FIX ADDED: AUTH MODE CONTROL (THIS FIXES YOUR CLICK ISSUE)
  const [authMode, setAuthMode] = useState<'login' | 'register'>('login');

  const [sessions, setSessions] = useState<any[]>([]);
  const [currentSessionId, setCurrentSessionId] = useState<string>('');
  const [messages, setMessages] = useState<any[]>([]);
  const [status, setStatus] = useState('Ready');
  const [ws, setWs] = useState<WebSocket | null>(null);

  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [isWorkspaceOpen, setIsWorkspaceOpen] = useState(true);
  const [activeTab, setActiveTab] = useState<'calendar' | 'period'>('period');

  const [calendarEvents, setCalendarEvents] = useState<any[]>([]);
  const [periodEntries, setPeriodEntries] = useState<any[]>([]);

  const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
  const WS_URL = import.meta.env.VITE_API_URL
    ? import.meta.env.VITE_API_URL.replace('https', 'wss').replace('http', 'ws')
    : 'ws://localhost:8000';

  useEffect(() => {
    const saved = localStorage.getItem('youth_hub_v2');
    if (saved) {
      const parsed = JSON.parse(saved);
      setSessions(parsed);
      if (parsed.length > 0) loadSession(parsed[0].id, parsed);
      else createNewSession([]);
    } else createNewSession([]);
  }, []);

  const createNewSession = (list?: any[]) => {
    const id = Math.random().toString(36).substring(7);
    const newSess = { id, title: 'New Consultation', messages: [] };
    const updated = [newSess, ...(list || sessions)];
    setSessions(updated);
    loadSession(id, updated);
  };

  const loadSession = (id: string, list?: any[]) => {
    setCurrentSessionId(id);
    const sess = (list || sessions).find((s) => s.id === id);
    setMessages(sess?.messages || []);
    connectWebSocket(id);
  };

  const connectWebSocket = (id: string) => {
    if (ws) ws.close();

    const socket = new WebSocket(`${WS_URL}/ws/${id}`);

    socket.onopen = () => {
      setWs(socket);
      setStatus('Online');
    };

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.type === 'result') {
        setMessages((p) => [...p, { role: 'assistant', content: data.content }]);
        setStatus('Ready');
      }
    };

    socket.onclose = () => setStatus('Disconnected');
  };

  const sendMessage = () => {
    const input = document.getElementById('main-input') as HTMLInputElement;
    if (!ws || !input?.value) return;

    ws.send(JSON.stringify({ message: input.value }));
    setMessages((p) => [...p, { role: 'user', content: input.value }]);
    input.value = '';
  };

  if (loading) return <div className="p-10 text-white">Loading...</div>;

  // 🔥 FIXED AUTH SWITCHING LOGIC
  if (!isAuthenticated) {
    return authMode === 'login'
      ? <Login onSwitchToRegister={() => setAuthMode('register')} />
      : <Register onSwitchToLogin={() => setAuthMode('login')} />;
  }

  return (
    <div className="flex h-screen w-screen bg-[#0a0c10] text-white">
      <div className="flex-1 flex flex-col">
        <div className="flex-1 overflow-y-auto p-10">
          {messages.map((m, i) => (
            <div key={i} className="mb-4">
              <div className={m.role === 'user' ? 'text-right' : 'text-left'}>
                <div className="inline-block p-4 bg-[#161b22] rounded-xl">
                  {m.content}
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="p-4 flex gap-2">
          <input id="main-input" className="flex-1 p-3 bg-[#161b22]" />
          <button onClick={sendMessage} className="bg-green-500 px-6">
            Send
          </button>
        </div>
      </div>
    </div>
  );
}
