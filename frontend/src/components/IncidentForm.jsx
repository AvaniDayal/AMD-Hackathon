import { useState } from 'react'
import { reportIncident } from '../services/api'

export default function IncidentForm({
  incidentLocation,
  onRequestLocationPick,
  onAlert,
  onReroute,
  onSubmitted,
  origin,
  dest,
}) {
  const [text, setText] = useState('')
  const [status, setStatus] = useState('')
  const [count, setCount] = useState(0)
  const [submitting, setSubmitting] = useState(false)

  const handleSubmit = async () => {
    if (!text.trim()) {
      setStatus('Please describe the incident first.')
      return
    }
    if (!incidentLocation) {
      setStatus('Please pin the incident location on the map first.')
      return
    }

    setSubmitting(true)
    setStatus('Submitting...')

    try {
      const res = await reportIncident({
        lat: incidentLocation.lat,
        lon: incidentLocation.lon,
        text,
        // Always send current origin/dest so backend can reroute
        origin_lat: origin?.lat ?? null,
        origin_lon: origin?.lon ?? null,
        dest_lat: dest?.lat ?? null,
        dest_lon: dest?.lon ?? null,
      })

      const newCount = count + 1
      setCount(newCount)
      setText('')

      // Notify parent — adds circle + icon on map
      onSubmitted(incidentLocation.lat, incidentLocation.lon)

      if (res.data.alert === true && res.data.alert_lat != null) {
        // Trigger alert banner
        onAlert(res.data.alert_lat, res.data.alert_lon)
        // Update safe route if backend returned a new one
        if (res.data.new_safe_route && res.data.new_safe_route.length > 0) {
          onReroute(res.data.new_safe_route)
          setStatus('🚨 Alert! Safe route updated to avoid this zone.')
        } else {
          setStatus('🚨 Alert triggered — route already avoids this zone.')
        }
      } else {
        setStatus(`✓ Report submitted — safety scores updated`)
      }

      setTimeout(() => setStatus(''), 5000)
    } catch (err) {
      console.error('Incident submission error:', err)
      setStatus('Submission failed. Is the backend running?')
    }

    setSubmitting(false)
  }

  return (
    <div className="absolute bottom-4 left-4 bg-white rounded-xl shadow-xl p-4 w-80 z-[1000] border border-gray-200">
      <p className="font-bold text-gray-800 mb-3 text-sm">⚠️ Report an Incident</p>

      {/* Location pin button */}
      <button
        onClick={onRequestLocationPick}
        className={`w-full mb-2 py-2 px-3 rounded-lg text-sm font-semibold border-2 transition-all ${
          incidentLocation
            ? 'bg-green-50 border-green-500 text-green-700'
            : 'bg-gray-50 border-dashed border-gray-400 text-gray-500 hover:border-red-400 hover:text-red-500'
        }`}
      >
        {incidentLocation
          ? `📍 ${incidentLocation.lat.toFixed(4)}, ${incidentLocation.lon.toFixed(4)}`
          : '📍 Click to pin incident location on map'}
      </button>

      {/* Text input */}
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Describe what you observed... (e.g. dark path, suspicious person)"
        className="w-full border border-gray-300 rounded-lg p-2 text-sm h-16 resize-none focus:outline-none focus:border-red-400"
      />

      {/* Submit button */}
      <button
        onClick={handleSubmit}
        disabled={submitting}
        className="mt-2 w-full bg-red-500 text-white py-2 rounded-lg font-semibold hover:bg-red-600 transition-colors text-sm disabled:opacity-60"
      >
        {submitting ? 'Submitting...' : 'Submit Report'}
      </button>

      {/* Status message */}
      {status && (
        <p className="text-xs mt-2 text-center text-gray-600 font-medium">{status}</p>
      )}

      {/* Counter */}
      <div className="flex justify-between mt-2">
        <p className="text-xs text-gray-400">Reports this session: {count}</p>
        <p className="text-xs text-gray-400">Each report updates safety scores</p>
      </div>
    </div>
  )
}