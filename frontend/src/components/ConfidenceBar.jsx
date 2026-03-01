export default function ConfidenceBar({ score }) {
  const label = score >= 70
    ? '✓ Well documented area'
    : score >= 30
    ? '~ Some community reports'
    : '○ New area — limited data'

  const color = score >= 70
    ? 'bg-green-400'
    : score >= 30
    ? 'bg-yellow-400'
    : 'bg-gray-300'

  return (
    <div className="mt-2">
      <div className="w-full bg-gray-200 rounded-full h-1.5">
        <div
          className={`${color} h-1.5 rounded-full transition-all`}
          style={{ width: `${Math.max(score, 5)}%` }}
        />
      </div>
      <p className="text-xs text-gray-500 mt-1">{label}</p>
    </div>
  )
}