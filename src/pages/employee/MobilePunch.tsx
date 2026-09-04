import React, { useState, useEffect } from 'react';
import { DashboardLayout } from '../../components/layout';
import { 
  submitMobilePunch, 
  getTodayPunches, 
  MobilePunch,
  getMyAttendance
} from '../../services/attendanceService';
import { Clock, MapPin, AlertCircle, CheckCircle, Smartphone } from 'lucide-react';
import { format } from 'date-fns';
import { useAuth } from '../../context/AuthContext';

export default function MobilePunchPage() {
  const { user } = useAuth();
  const [punches, setPunches] = useState<MobilePunch[]>([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [status, setStatus] = useState<'Punched In' | 'Not Punched In'>('Not Punched In');
  const [clientEventId, setClientEventId] = useState<string>(crypto.randomUUID());

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      // Fetch both today's raw punches and today's attendance status
      const [punchesRes, attendanceRes] = await Promise.all([
        getTodayPunches(),
        getMyAttendance(
          format(new Date(), 'yyyy-MM-dd'),
          format(new Date(), 'yyyy-MM-dd')
        )
      ]);
      
      setPunches(punchesRes.data.records);

      // Determine current status
      const todayRecord = attendanceRes.data.records[0];
      if (todayRecord) {
        if (todayRecord.inTime && !todayRecord.outTime) {
          setStatus('Punched In');
        } else {
          setStatus('Not Punched In');
        }
      } else {
        // Fallback to deriving from raw punches if no attendance record yet
        if (punchesRes.data.records.length > 0) {
          const lastPunch = punchesRes.data.records[punchesRes.data.records.length - 1];
          setStatus(lastPunch.punchType === 'IN' ? 'Punched In' : 'Not Punched In');
        } else {
          setStatus('Not Punched In');
        }
      }

    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load today\'s punches.');
    } finally {
      setLoading(false);
    }
  };

  const handlePunch = async () => {
    setSubmitting(true);
    setError(null);

    const punchType = status === 'Punched In' ? 'OUT' : 'IN';
    const payload = {
      punchType,
      occurredAt: new Date().toISOString(),
      clientEventId,
      latitude: null as number | null,
      longitude: null as number | null,
      locationAccuracy: null as number | null,
    };

    try {
      if ('geolocation' in navigator) {
        try {
          const position = await new Promise<GeolocationPosition>((resolve, reject) => {
            navigator.geolocation.getCurrentPosition(resolve, reject, {
              timeout: 5000,
              maximumAge: 0
            });
          });
          payload.latitude = position.coords.latitude;
          payload.longitude = position.coords.longitude;
          payload.locationAccuracy = position.coords.accuracy;
        } catch (geoErr) {
          // Continue without location if permission denied or timeout
          console.warn('Geolocation failed or denied:', geoErr);
        }
      }

      await submitMobilePunch(payload);
      
      // Success! Generate a new clientEventId for the NEXT punch
      setClientEventId(crypto.randomUUID());
      
      // Refresh data
      await fetchData();

    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to submit punch. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex justify-center items-center min-h-[50vh]">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="max-w-md mx-auto py-8 px-4 sm:px-6 lg:px-8">
        
        <div className="bg-white overflow-hidden shadow rounded-2xl mb-6">
          <div className="px-4 py-5 sm:p-6 text-center">
            <h2 className="text-xl font-semibold text-gray-900 mb-2">Mobile Punch</h2>
            
            <div className="my-6">
              <div className={`inline-flex items-center px-4 py-2 rounded-full text-sm font-medium ${
                status === 'Punched In' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
              }`}>
                {status === 'Punched In' ? (
                  <CheckCircle className="w-4 h-4 mr-2" />
                ) : (
                  <AlertCircle className="w-4 h-4 mr-2" />
                )}
                {status}
              </div>
            </div>

            <button
              onClick={handlePunch}
              disabled={submitting}
              className={`
                relative w-48 h-48 rounded-full shadow-lg transition-all duration-200 flex flex-col items-center justify-center mx-auto
                ${submitting ? 'opacity-70 cursor-not-allowed transform scale-95' : 'hover:shadow-xl active:scale-95'}
                ${status === 'Punched In' 
                  ? 'bg-gradient-to-br from-red-500 to-red-600 text-white shadow-red-200' 
                  : 'bg-gradient-to-br from-indigo-500 to-indigo-600 text-white shadow-indigo-200'
                }
              `}
            >
              <div className="absolute inset-0 rounded-full border-4 border-white opacity-20"></div>
              {submitting ? (
                <div className="animate-spin rounded-full h-12 w-12 border-4 border-white border-t-transparent"></div>
              ) : (
                <>
                  <Smartphone className="w-12 h-12 mb-2" />
                  <span className="text-2xl font-bold tracking-wider">
                    {status === 'Punched In' ? 'PUNCH OUT' : 'PUNCH IN'}
                  </span>
                </>
              )}
            </button>

            {error && (
              <div className="mt-6 rounded-md bg-red-50 p-4 text-left">
                <div className="flex">
                  <div className="flex-shrink-0">
                    <AlertCircle className="h-5 w-5 text-red-400" aria-hidden="true" />
                  </div>
                  <div className="ml-3">
                    <h3 className="text-sm font-medium text-red-800">{error}</h3>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        <div className="bg-white shadow rounded-2xl overflow-hidden">
          <div className="px-4 py-5 border-b border-gray-200 sm:px-6">
            <h3 className="text-lg leading-6 font-medium text-gray-900 flex items-center">
              <Clock className="w-5 h-5 mr-2 text-gray-500" />
              Today's Punches
            </h3>
          </div>
          
          <ul className="divide-y divide-gray-200">
            {punches.length === 0 ? (
              <li className="px-4 py-8 text-center text-gray-500">
                No punches recorded today.
              </li>
            ) : (
              punches.map((punch) => (
                <li key={punch.punchId} className="px-4 py-4 sm:px-6">
                  <div className="flex items-center justify-between">
                    <div className="flex flex-col">
                      <p className="text-sm font-medium text-gray-900">
                        {format(new Date(punch.occurredAt), 'hh:mm:ss a')}
                      </p>
                      <p className="text-xs text-gray-500 mt-1 flex items-center">
                        {punch.source}
                        {punch.location && (
                          <span className="ml-2 flex items-center text-indigo-600">
                            <MapPin className="w-3 h-3 mr-1" />
                            Location saved
                          </span>
                        )}
                      </p>
                    </div>
                    <div className={`px-3 py-1 rounded-full text-xs font-medium ${
                      punch.punchType === 'IN' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                    }`}>
                      {punch.punchType}
                    </div>
                  </div>
                </li>
              ))
            )}
          </ul>
        </div>

      </div>
    </DashboardLayout>
  );
}
