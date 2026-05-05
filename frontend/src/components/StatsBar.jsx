export default function StatsBar({ stats }) {
  return (
    <div style={{
      display:        'flex',
      alignItems:     'center',
      justifyContent: 'space-between',
      padding:        '14px 28px',
      background:     'var(--surface)',
      borderBottom:   '1px solid var(--border)',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
        <div style={{
          width: '28px', height: '28px',
          background: 'var(--accent)',
          borderRadius: '6px',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: '14px',
        }}>🏺</div>
        <span style={{
          fontFamily:  'Instrument Serif, serif',
          fontSize:    '17px',
          color:       'var(--text)',
          letterSpacing: '0.01em',
        }}>
          Memory Archaeologist
        </span>
      </div>

      <div style={{ display: 'flex', gap: '20px', alignItems: 'center' }}>
        {[
          ['Documents', stats?.total_vectors ?? '—'],
          ['Concepts',  stats?.total_concepts ?? '—'],
        ].map(([label, val]) => (
          <div key={label} style={{ textAlign: 'right' }}>
            <div style={{ fontSize: '15px', fontWeight: 500, color: 'var(--text)' }}>{val}</div>
            <div style={{ fontSize: '11px', color: 'var(--muted)', textTransform: 'uppercase', letterSpacing: '0.06em' }}>{label}</div>
          </div>
        ))}
      </div>
    </div>
  );
}