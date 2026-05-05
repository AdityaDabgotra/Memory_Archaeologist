import ReactMarkdown from 'react-markdown';

const INTENT_LABELS = {
  archaeologist: 'Memory retrieval',
  timeline:      'Timeline analysis',
  contrast:      'Contrast analysis',
  regret_miner:  'Idea excavation',
};

export default function ChatMessage({ message }) {
  const isUser = message.role === 'user';

  return (
    <div style={{
      display:        'flex',
      justifyContent: isUser ? 'flex-end' : 'flex-start',
      marginBottom:   '20px',
      gap:            '12px',
      alignItems:     'flex-start',
    }}>
      {!isUser && (
        <div style={{
          width:          '32px', height: '32px',
          borderRadius:   '8px',
          background:     'var(--accent)',
          display:        'flex',
          alignItems:     'center',
          justifyContent: 'center',
          fontSize:       '14px',
          flexShrink:     0,
          marginTop:      '2px',
        }}>🏺</div>
      )}

      <div style={{ maxWidth: '72%' }}>
        {!isUser && message.intent && (
          <div style={{
            fontSize:      '10px',
            color:         'var(--accent)',
            fontWeight:    500,
            letterSpacing: '0.08em',
            textTransform: 'uppercase',
            marginBottom:  '5px',
          }}>
            {INTENT_LABELS[message.intent] ?? message.intent}
          </div>
        )}
        <div style={{
          padding:      isUser ? '11px 16px' : '14px 18px',
          borderRadius: isUser ? '18px 18px 4px 18px' : '4px 18px 18px 18px',
          background:   isUser ? 'var(--user-bg)' : 'var(--surface)',
          border:       isUser ? 'none' : '1px solid var(--border)',
          fontSize:     '14px',
          lineHeight:   '1.7',
          color:        isUser ? 'var(--user-text)' : 'var(--text)',
        }}>
          <ReactMarkdown
            components={{
              p: ({children}) => <p style={{ marginBottom: '10px', lastChild: { marginBottom: 0 } }}>{children}</p>,
              h3: ({children}) => <h3 style={{ fontSize: '14px', fontWeight: 500, margin: '12px 0 4px' }}>{children}</h3>,
              strong: ({children}) => <strong style={{ fontWeight: 500 }}>{children}</strong>,
              ul: ({children}) => <ul style={{ paddingLeft: '18px', marginBottom: '10px' }}>{children}</ul>,
              li: ({children}) => <li style={{ marginBottom: '4px' }}>{children}</li>,
            }}
          >
            {message.content}
          </ReactMarkdown>
        </div>
      </div>
    </div>
  );
}