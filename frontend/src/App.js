import { useState, useEffect, useRef } from 'react';
import { queryMemories, getConcepts, getStats } from './api';
import KnowledgeGraph from './components/KnowledgeGraph';
import ChatMessage from './components/ChatMessage';
import StatsBar from './components/StatsBar';

export default function App() {
  const [messages,           setMessages]           = useState([]);
  const [input,              setInput]              = useState('');
  const [loading,            setLoading]            = useState(false);
  const [concepts,           setConcepts]           = useState([]);
  const [stats,              setStats]              = useState(null);
  const [highlightedConcept, setHighlightedConcept] = useState(null);
  const [activeTab,          setActiveTab]          = useState('chat');
  const messagesEndRef = useRef(null);

  // Load initial data
  useEffect(() => {
    getConcepts().then(d => setConcepts(d.concepts)).catch(console.error);
    getStats().then(setStats).catch(console.error);
  }, []);

  // Scroll to bottom on new message
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    const userMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const result = await queryMemories(input);

      // Highlight concept mentioned in answer
      const mentioned = concepts.find(c =>
        result.answer.toLowerCase().includes(c.concept)
      );
      if (mentioned) setHighlightedConcept(mentioned.concept);

      setMessages(prev => [...prev, {
        role:    'assistant',
        content: result.answer,
        intent:  result.intent,
      }]);

      // Refresh concepts after query
      getConcepts().then(d => setConcepts(d.concepts));

    } catch (err) {
      setMessages(prev => [...prev, {
        role:    'assistant',
        content: '❌ Error connecting to the API. Is the server running?',
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const suggestions = [
    'What was I thinking about starting a business?',
    'How did my startup idea evolve over time?',
    'Have I contradicted myself about my career?',
    'What ideas did I abandon and never follow up on?',
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>

      {/* Top bar */}
      <StatsBar stats={stats} concepts={concepts} />

      {/* Tab switcher */}
      <div style={{
        display:      'flex',
        background:   '#0d0d18',
        borderBottom: '1px solid #1e1e2e',
        padding:      '0 20px',
      }}>
        {['chat', 'graph'].map(tab => (
          <button key={tab} onClick={() => setActiveTab(tab)} style={{
            padding:      '10px 20px',
            background:   'none',
            border:       'none',
            borderBottom: activeTab === tab ? '2px solid #7c6af7' : '2px solid transparent',
            color:        activeTab === tab ? '#a89cf7' : '#5a5a7a',
            cursor:       'pointer',
            fontSize:     '13px',
            textTransform: 'capitalize',
          }}>
            {tab === 'chat' ? '💬 Chat' : '🕸️ Knowledge Graph'}
          </button>
        ))}
      </div>

      {/* Main content */}
      <div style={{ flex: 1, overflow: 'hidden', position: 'relative' }}>

        {/* Chat tab */}
        {activeTab === 'chat' && (
          <div style={{
            display:       'flex',
            flexDirection: 'column',
            height:        '100%',
          }}>
            {/* Messages */}
            <div style={{
              flex:       1,
              overflowY:  'auto',
              padding:    '20px',
            }}>
              {messages.length === 0 && (
                <div style={{ textAlign: 'center', marginTop: '60px' }}>
                  <div style={{ fontSize: '48px', marginBottom: '16px' }}>🏺</div>
                  <h2 style={{
                    color:        '#7c6af7',
                    marginBottom: '8px',
                    fontWeight:   500,
                  }}>
                    Memory Archaeologist
                  </h2>
                  <p style={{ color: '#5a5a7a', marginBottom: '32px' }}>
                    Ask anything about your past thoughts and ideas
                  </p>
                  <div style={{
                    display:   'flex',
                    flexWrap:  'wrap',
                    gap:       '10px',
                    justifyContent: 'center',
                    maxWidth:  '600px',
                    margin:    '0 auto',
                  }}>
                    {suggestions.map((s, i) => (
                      <button key={i} onClick={() => setInput(s)} style={{
                        padding:      '8px 14px',
                        background:   '#1a1a28',
                        border:       '1px solid #2a2a3a',
                        borderRadius: '20px',
                        color:        '#8a8aaa',
                        cursor:       'pointer',
                        fontSize:     '12px',
                      }}>
                        {s}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {messages.map((msg, i) => (
                <ChatMessage key={i} message={msg} />
              ))}

              {loading && (
                <div style={{
                  display:    'flex',
                  gap:        '10px',
                  alignItems: 'center',
                  color:      '#5a5a7a',
                  fontSize:   '13px',
                  padding:    '8px 0',
                }}>
                  <div style={{
                    width:        '32px',
                    height:       '32px',
                    borderRadius: '50%',
                    background:   '#2a1f5e',
                    border:       '1px solid #4a3a8e',
                    display:      'flex',
                    alignItems:   'center',
                    justifyContent: 'center',
                  }}>🏺</div>
                  Excavating memories...
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Input area */}
            <div style={{
              padding:    '16px 20px',
              borderTop:  '1px solid #1e1e2e',
              background: '#0d0d18',
              display:    'flex',
              gap:        '10px',
            }}>
              <textarea
                value={input}
                onChange={e => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Ask about your past thoughts... (Enter to send)"
                rows={2}
                style={{
                  flex:        1,
                  padding:     '12px 16px',
                  background:  '#1a1a28',
                  border:      '1px solid #2a2a3a',
                  borderRadius: '12px',
                  color:       '#e8e6df',
                  fontSize:    '14px',
                  resize:      'none',
                  outline:     'none',
                  fontFamily:  'inherit',
                }}
              />
              <button
                onClick={sendMessage}
                disabled={loading || !input.trim()}
                style={{
                  padding:      '12px 20px',
                  background:   loading || !input.trim() ? '#1a1a28' : '#2d1f6e',
                  border:       '1px solid #4a3a8e',
                  borderRadius: '12px',
                  color:        loading || !input.trim() ? '#4a4a6a' : '#a89cf7',
                  cursor:       loading || !input.trim() ? 'not-allowed' : 'pointer',
                  fontSize:     '20px',
                  transition:   'all 0.2s',
                }}
              >
                ↑
              </button>
            </div>
          </div>
        )}

        {/* Graph tab */}
        {activeTab === 'graph' && (
          <div style={{ height: '100%', padding: '20px' }}>
            <div style={{
              height:       '100%',
              background:   '#0d0d18',
              borderRadius: '12px',
              border:       '1px solid #1e1e2e',
              overflow:     'hidden',
            }}>
              {concepts.length > 0
                ? <KnowledgeGraph
                    concepts={concepts}
                    highlightedConcept={highlightedConcept}
                  />
                : (
                  <div style={{
                    display:        'flex',
                    alignItems:     'center',
                    justifyContent: 'center',
                    height:         '100%',
                    color:          '#3a3a5a',
                  }}>
                    No concepts in graph yet. Ingest some documents first.
                  </div>
                )
              }
            </div>
          </div>
        )}
      </div>
    </div>
  );
}