const TYPE_LABELS = {
  A: 'Ability & Aptitude',
  B: 'Biodata & SJT',
  C: 'Competencies',
  D: 'Development & 360',
  E: 'Assessment Exercises',
  K: 'Knowledge & Skills',
  P: 'Personality & Behavior',
  S: 'Simulations',
}

function TypeBadges({ typeStr }) {
  const codes = typeStr.split(',').map(c => c.trim()).filter(Boolean)
  return (
    <div style={{ display: 'flex', gap: 4, flexWrap: 'wrap' }}>
      {codes.map(code => (
        <span
          key={code}
          className={`type-badge badge-${code} ${!TYPE_LABELS[code] ? 'badge-default' : ''}`}
          title={TYPE_LABELS[code] || code}
        >
          {code}
        </span>
      ))}
    </div>
  )
}

export default function RecommendationCard({ rec }) {
  return (
    <div className="rec-card">
      <div className="rec-card-header">
        <div className="rec-name">{rec.name}</div>
        <TypeBadges typeStr={rec.test_type} />
      </div>
      <a
        href={rec.url}
        target="_blank"
        rel="noopener noreferrer"
        className="rec-link"
      >
        View in catalog
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
          <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>
          <polyline points="15 3 21 3 21 9"/>
          <line x1="10" y1="14" x2="21" y2="3"/>
        </svg>
      </a>
    </div>
  )
}
