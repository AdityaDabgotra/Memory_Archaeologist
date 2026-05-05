import ReactMarkdown from 'react-markdown';

export default function ChatMessage({ message }) {
  const isUser = message.role === 'user';

  return (
    <div style={{
      display:       'flex',
      justifyContent: isUser ? 'flex-end' : 'flex-start',
      marginBottom:  '16px',
      gap:           '10px',
      alignItems:    'flex-start',
    }}>
      {!isUser && (
        <div style={{
          width:           '32px',
          height:          '32px',
          borderRadius:    '50%',
          background:      '#2a1f5e',
          border:          '1px solid #4a3a8e',
          display:         'flex',
          alignItems:      'center',
          justifyContent:  'center',
          fontSize:        '14px',
          flexShrink:      0,
        }}>🏺</div>
      )}

      <div style={{
        maxWidth:     '75%',
        padding:      '12px 16px',
        borderRadius: isUser ? '18px 18px 4px 18px' : '18px 18px 18px 4px',
        background:   isUser ? '#2d1f6e' : '#1a1a28',
        border:       `1px solid ${isUser ? '#4a3a9e' : '#2a2a3a'}`,
        fontSize:     '14px',
        lineHeight:   '1.6',
        color:        '#e8e6df',
      }}>
        {message.intent && (
          <div style={{
            fontSize:     '10px',
            color:        '#7c6af7',
            marginBottom: '6px',
            textTransform: 'uppercase',
            letterSpacing: '0.08em',
          }}>
            {message.intent} agent
          </div>
        )}
        <ReactMarkdown>{message.content}</ReactMarkdown>
      </div>
    </div>
  );
}