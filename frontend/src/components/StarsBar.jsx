export default function StatsBar({ stats, concepts }) {
    return (
      <div style={{
        display:        'flex',
        gap:            '16px',
        padding:        '10px 20px',
        background:     '#0d0d18',
        borderBottom:   '1px solid #1e1e2e',
        fontSize:       '12px',
        color:          '#6a6a8a',
        alignItems:     'center',
      }}>
        <span> Memory Archaeologist</span>
        <span style={{ marginLeft: 'auto' }}>
          {stats?.total_vectors ?? 0} documents
        </span>
        <span>•</span>
        <span>{stats?.total_concepts ?? 0} concepts</span>
        <span>•</span>
        <span>{concepts?.length ?? 0} nodes in graph</span>
      </div>
    );
  }