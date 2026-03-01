// IIT Bombay Library to Hostel 10 — real coordinates
const DEMO_SCENARIO = {
  origin_lat: 19.1334,
  origin_lon: 72.9133,
  dest_lat: 19.1367,
  dest_lon: 72.9156,
  hour: 22,
  day: 4
}

export default function DemoButton({ onLoad }) {
  return (
    <button
      onClick={() => onLoad(DEMO_SCENARIO)}
      className="bg-orange-500 text-white px-4 py-2 rounded font-bold hover:bg-orange-600"
    >
      Load Demo: Library → Hostel (10PM Friday)
    </button>
  )
}