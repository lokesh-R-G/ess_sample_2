import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

import { getAdminPunchesForDate, MobilePunch } from '../../services/attendanceService';
import { format } from 'date-fns';
import { Clock, Smartphone, Fingerprint } from 'lucide-react';

// Fix Vite/Leaflet default marker issue
import iconUrl from 'leaflet/dist/images/marker-icon.png';
import iconShadowUrl from 'leaflet/dist/images/marker-shadow.png';
import iconRetinaUrl from 'leaflet/dist/images/marker-icon-2x.png';

let DefaultIcon = L.icon({
  iconUrl,
  iconRetinaUrl,
  shadowUrl: iconShadowUrl,
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  tooltipAnchor: [16, -28],
  shadowSize: [41, 41]
});
L.Marker.prototype.options.icon = DefaultIcon;

interface AdminPunchDetailMapProps {
  empCode: string;
  date: string;
  companyId?: string;
}

export const AdminPunchDetailMap: React.FC<AdminPunchDetailMapProps> = ({ empCode, date, companyId }) => {
  const [punches, setPunches] = useState<MobilePunch[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    const fetchPunches = async () => {
      setLoading(true);
      try {
        const response = await getAdminPunchesForDate(empCode, date, companyId);
        if (mounted) {
          setPunches(response.punches || []);
        }
      } catch (err: any) {
        if (mounted) {
          setError(err.message || 'Failed to fetch punches');
        }
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    };
    if (empCode && date) {
      fetchPunches();
    }
    return () => { mounted = false; };
  }, [empCode, date, companyId]);

  if (loading) {
    return <div className="text-sm text-neutral-500 py-4">Loading punches...</div>;
  }

  if (error) {
    return <div className="text-sm text-red-500 py-4">{error}</div>;
  }

  if (punches.length === 0) {
    return <div className="text-sm text-neutral-500 py-4">No raw punches found for this date.</div>;
  }

  const mapPunches = punches.filter(p => 
    p.source === 'MOBILE' && 
    p.location?.lat != null && 
    p.location?.lng != null &&
    p.location.lat >= -90 && p.location.lat <= 90 &&
    p.location.lng >= -180 && p.location.lng <= 180
  );
  
  return (
    <div className="space-y-6">
      <div className="space-y-3">
        {punches.map((punch, idx) => (
          <div key={idx} className="flex items-start gap-3 p-3 rounded-xl border border-neutral-200 bg-white shadow-sm">
            <div className={`p-2 rounded-lg ${punch.punchType === 'IN' ? 'bg-emerald-100 text-emerald-700' : 'bg-red-100 text-red-700'}`}>
              <Clock className="w-4 h-4" />
            </div>
            <div className="flex-1">
              <div className="flex items-center justify-between">
                <span className="font-semibold text-neutral-900">{punch.punchType}</span>
                <span className="text-sm font-medium text-neutral-900">
                  {punch.occurredAt ? format(new Date(punch.occurredAt), 'HH:mm:ss') : 'Unknown Time'}
                </span>
              </div>
              <div className="flex items-center gap-2 mt-1">
                {punch.source === 'MOBILE' ? (
                  <span className="flex items-center gap-1 text-xs font-medium text-blue-700 bg-blue-50 px-2 py-0.5 rounded border border-blue-100">
                    <Smartphone className="w-3 h-3" /> Mobile
                  </span>
                ) : (
                  <span className="flex items-center gap-1 text-xs font-medium text-neutral-600 bg-neutral-100 px-2 py-0.5 rounded border border-neutral-200">
                    <Fingerprint className="w-3 h-3" /> {punch.source}
                  </span>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      {mapPunches.length > 0 && (
        <div className="rounded-xl overflow-hidden border border-neutral-200 shadow-sm" style={{ height: '240px', width: '100%' }}>
          <MapContainer 
            center={[mapPunches[0].location.lat, mapPunches[0].location.lng]} 
            zoom={15} 
            style={{ height: '100%', width: '100%' }}
          >
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
            {mapPunches.map((punch, idx) => (
              <Marker 
                key={idx} 
                position={[punch.location.lat, punch.location.lng]}
              >
                <Popup>
                  <div className="text-sm font-medium">
                    {punch.punchType} at {format(new Date(punch.occurredAt), 'HH:mm')}
                  </div>
                  <div className="text-xs text-neutral-500 mt-1">
                    Lat: {punch.location.lat.toFixed(4)}, Lng: {punch.location.lng.toFixed(4)}
                    {punch.location?.accuracy && <><br/>Accuracy: &plusmn;{Math.round(punch.location.accuracy)}m</>}
                  </div>
                </Popup>
              </Marker>
            ))}
          </MapContainer>
        </div>
      )}
      
      {punches.some(p => p.source === 'MOBILE' && (!p.location || p.location.lat == null || p.location.lng == null)) && (
        <div className="p-3 bg-neutral-50 text-neutral-600 text-sm rounded-lg border border-neutral-200">
          Location not available.
        </div>
      )}
    </div>
  );
};
