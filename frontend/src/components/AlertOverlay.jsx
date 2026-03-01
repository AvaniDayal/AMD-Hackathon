export default function AlertOverlay({ visible, onDismiss }) {
  if (!visible) return null
  return (
    <div className="absolute top-4 left-1/2 transform -translate-x-1/2 z-[1000] bg-red-600 text-white px-6 py-3 rounded-xl shadow-xl flex items-center gap-3">
      <span className="animate-pulse text-2xl">🔴</span>
      <div>
        <p className="font-bold">Safety Alert Detected</p>
        <p className="text-sm">Multiple reports in this zone</p>
      </div>
      <button onClick={onDismiss} className="ml-4 text-white font-bold text-xl">×</button>
    </div>
  )
}