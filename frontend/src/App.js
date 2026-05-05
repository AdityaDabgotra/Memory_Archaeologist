import { useState, useEffect, useRef } from 'react';
import { queryMemories, getConcepts, getStats } from './api';
import KnowledgeGraph from './components/KnowledgeGraph.jsx';
import ChatMessage    from './components/ChatMessage.jsx';
import StatsBar       from './components/StatsBar.jsx';

const SUGGESTIONS = [
  'What was I thinking about starting a business?',
  'How did my startup idea evolve over time?',
  'Have I ever contradicted myself about my career?',
  'What ideas did I mention but never follow up on?',
];

export default function App() {
  const [messages,    setMessages]    = useState([]);
  const [input,       setInput]       = useState('');
  const [loading,     setLoading]     = useState(false);
  const [concepts,    setConcepts]    = useState([]);
  const [stats,       setStats]       = useState(null);
  const [highlighted, setHighlighted] = useState(null);
  const [tab,         setTab]         = useState('chat');
  const bottomRef = useRef(null);

  useEffect(() => {
    getConcepts().then(d => setConcepts(d.concepts)).catch(() => {});
    getStats().then(setStats).catch(() => {});
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const send = async () => {
    if (!input.trim() || loading) return;
    const q = input.trim();
    setMessages(p => [...p, { role: 'user', content: q }]);
    setInput('');
    setLoading(true);
    try {
      const res = await queryMemories(q);
      const hit = concepts.find(c => res.answer.toLowerCase().includes(c.concept));
      if (hit) setHighlighted(hit.concept);
      setMessages(p => [...p, { role: 'assistant', content: res.answer, intent: res.intent }]);
      getConcepts().then(d => setConcepts(d.concepts));
    } catch {
      setMessages(p => [...p, { role: 'assistant', content: 'Could not reach the API. Make sure the backend is running on port 8000.' }]);
    } finally {
      setLoading(false);
    }
  };

  const onKey = e => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(); }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', background: 'var(--bg)' }}>

      <StatsBar stats={stats} />

      {/* Tabs */}
      <div style={{
        display: 'flex', gap: '2px',
        padding: '0 28px',
        background: 'var(--surface)',
        borderBottom: '1px solid var(--border)',
      }}>
        {[['chat', '💬 Chat'], ['graph', '🕸 Knowledge Graph']].map(([key, label]) => (
          <button key={key} onClick={() => setTab(key)} style={{
            padding:      '12px 16px',
            background:   'none',
            border:       'none',
            borderBottom: tab === key ? '2px solid var(--accent)' : '2px solid transparent',
            color:        tab === key ? 'var(--accent)' : 'var(--muted)',
            cursor:       'pointer',
            fontSize:     '13px',
            fontWeight:   tab === key ? 500 : 400,
            fontFamily:   'inherit',
            transition:   'color 0.15s',
          }}>{label}</button>
        ))}
      </div>

      {/* Content */}
      <div style={{ flex: 1, overflow: 'hidden' }}>

        {/* ── Chat ── */}
        {tab === 'chat' && (
          <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>

            <div style={{ flex: 1, overflowY: 'auto', padding: '28px 10vw' }}>
              {messages.length === 0 && (
                <div style={{ textAlign: 'center', paddingTop: '80px' }}>
                  <p style={{
                    fontFamily: 'Instrument Serif, serif',
                    fontSize:   '28px',
                    color:      'var(--text)',
                    marginBottom: '8px',
                  }}>
                    What do you want to rediscover?
                  </p>
                  <p style={{ fontSize: '14px', color: 'var(--muted)', marginBottom: '36px' }}>
                    Ask anything about your past thoughts, ideas, and decisions.
                  </p>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', justifyContent: 'center' }}>
                    {SUGGESTIONS.map((s, i) => (
                      <button key={i} onClick={() => setInput(s)} style={{
                        padding:      '8px 14px',
                        background:   'var(--surface)',
                        border:       '1px solid var(--border)',
                        borderRadius: '20px',
                        color:        'var(--muted)',
                        cursor:       'pointer',
                        fontSize:     '12.5px',
                        fontFamily:   'inherit',
                        transition:   'border-color 0.15s, color 0.15s',
                      }}
                      onMouseEnter={e => { e.target.style.borderColor = 'var(--accent)'; e.target.style.color = 'var(--accent)'; }}
                      onMouseLeave={e => { e.target.style.borderColor = 'var(--border)'; e.target.style.color = 'var(--muted)'; }}
                      >{s}</button>
                    ))}
                  </div>
                </div>
              )}

              {messages.map((m, i) => <ChatMessage key={i} message={m} />)}

              {loading && (
                <div style={{ display: 'flex', gap: '12px', alignItems: 'center', marginBottom: '20px' }}>
                  <div style={{
                    width: '32px', height: '32px', borderRadius: '8px',
                    background: 'var(--accent)',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    fontSize: '14px',
                  }}>🏺</div>
                  <div style={{ display: 'flex', gap: '4px', alignItems: 'center' }}>
                    {[0, 1, 2].map(i => (
                      <div key={i} style={{
                        width: '5px', height: '5px',
                        borderRadius: '50%',
                        background: 'var(--muted)',
                        animation: `pulse 1.2s ease-in-out ${i * 0.2}s infinite`,
                      }} />
                    ))}
                  </div>
                </div>
              )}
              <div ref={bottomRef} />
            </div>

            {/* Input */}
            <div style={{
              padding:    '16px 10vw',
              background: 'var(--surface)',
              borderTop:  '1px solid var(--border)',
              display:    'flex',
              gap:        '10px',
            }}>
              <textarea
                value={input}
                onChange={e => setInput(e.target.value)}
                onKeyDown={onKey}
                placeholder="Ask about your past thoughts…"
                rows={2}
                style={{
                  flex:         1,
                  padding:      '12px 16px',
                  background:   'var(--bg)',
                  border:       '1px solid var(--border)',
                  borderRadius: 'var(--radius)',
                  color:        'var(--text)',
                  fontSize:     '14px',
                  fontFamily:   'inherit',
                  resize:       'none',
                  outline:      'none',
                  lineHeight:   '1.6',
                  transition:   'border-color 0.15s',
                }}
                onFocus={e  => e.target.style.borderColor = 'var(--accent)'}
                onBlur={e   => e.target.style.borderColor = 'var(--border)'}
              />
              <button onClick={send} disabled={loading || !input.trim()} style={{
                padding:      '0 20px',
                background:   loading || !input.trim() ? 'var(--border)' : 'var(--accent)',
                border:       'none',
                borderRadius: 'var(--radius)',
                color:        loading || !input.trim() ? 'var(--muted)' : '#FFFFFF',
                cursor:       loading || !input.trim() ? 'not-allowed' : 'pointer',
                fontSize:     '18px',
                transition:   'background 0.15s',
              }}>↑</button>
            </div>
          </div>
        )}

        {/* ── Graph ── */}
        {tab === 'graph' && (
          <div style={{ height: '100%', padding: '24px', background: 'var(--bg)' }}>
            <div style={{
              height:       '100%',
              background:   'var(--surface)',
              borderRadius: '16px',
              border:       '1px solid var(--border)',
              overflow:     'hidden',
            }}>
              {concepts.length > 0
                ? <KnowledgeGraph concepts={concepts} highlightedConcept={highlighted} />
                : (
                  <div style={{
                    display: 'flex', flexDirection: 'column',
                    alignItems: 'center', justifyContent: 'center',
                    height: '100%', gap: '8px',
                  }}>
                    <span style={{ fontSize: '32px' }}>🕸</span>
                    <p style={{ color: 'var(--muted)', fontSize: '14px' }}>
                      No concepts yet — ingest some documents first.
                    </p>
                  </div>
                )
              }
            </div>
          </div>
        )}
      </div>

      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 0.3; transform: scale(0.8); }
          50%       { opacity: 1;   transform: scale(1.1); }
        }
      `}</style>
    </div>
  );
}