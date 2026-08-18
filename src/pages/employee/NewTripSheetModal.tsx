import React, { useState, useEffect, useRef } from 'react';
import { Calculator, UploadCloud } from 'lucide-react';
import { Modal, Input, Select, AnimatedButton } from '../../components/ui';
import { reimbursementApi, TripSheetRequest } from '../../services/reimbursement.api';

interface Props {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export default function NewTripSheetModal({ isOpen, onClose, onSuccess }: Props) {
  const [formData, setFormData] = useState<TripSheetRequest>({
    tripDate: new Date().toISOString().split('T')[0],
    fromLocation: '',
    toLocation: '',
    tripType: 'One Way',
    startOdometer: 0,
    endOdometer: 0,
    claimedDistance: 0,
    description: '',
    attachmentIds: [],
  });

  const [calculatedDistance, setCalculatedDistance] = useState(0);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const dist = Math.max(0, formData.endOdometer - formData.startOdometer);
    setCalculatedDistance(dist);
    setFormData(prev => ({ ...prev, claimedDistance: dist }));
  }, [formData.startOdometer, formData.endOdometer]);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    
    try {
      setIsUploading(true);
      const res = await reimbursementApi.uploadAttachment(file);
      setFormData(prev => ({
        ...prev,
        attachmentIds: [...prev.attachmentIds, res.id]
      }));
    } catch (err) {
      setError("Failed to upload attachment");
    } finally {
      setIsUploading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (calculatedDistance <= 0) {
      setError('Distance must be greater than 0');
      return;
    }

    try {
      setIsSubmitting(true);
      await reimbursementApi.submitTripSheet(formData);
      onSuccess();
    } catch (err: any) {
      setError(err.message || err.response?.data?.detail || 'Failed to submit trip sheet');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!isOpen) return null;

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="New Trip Sheet" size="lg">
      <div className="p-6">
        {error && (
          <div className="mb-6 p-4 bg-red-50 text-red-700 rounded-lg border border-red-100 text-sm">
            {error}
          </div>
        )}

        <form id="trip-sheet-form" onSubmit={handleSubmit} className="space-y-6">
          <div className="grid grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-neutral-700 mb-1">Trip Date</label>
              <Input
                type="date"
                required
                value={formData.tripDate}
                onChange={(e) => setFormData({ ...formData, tripDate: e.target.value })}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-neutral-700 mb-1">Trip Type</label>
              <Select
                value={formData.tripType}
                onChange={(e) => setFormData({ ...formData, tripType: e.target.value })}
                options={[
                  { label: 'One Way', value: 'One Way' },
                  { label: 'Round Trip', value: 'Round Trip' }
                ]}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-neutral-700 mb-1">From Location</label>
              <Input
                type="text"
                required
                placeholder="e.g. Office"
                value={formData.fromLocation}
                onChange={(e) => setFormData({ ...formData, fromLocation: e.target.value })}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-neutral-700 mb-1">To Location</label>
              <Input
                type="text"
                required
                placeholder="e.g. Client Site"
                value={formData.toLocation}
                onChange={(e) => setFormData({ ...formData, toLocation: e.target.value })}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-neutral-700 mb-1">Start Odometer (KM)</label>
              <Input
                type="number"
                min="0"
                step="0.1"
                required
                value={formData.startOdometer || ''}
                onChange={(e) => setFormData({ ...formData, startOdometer: parseFloat(e.target.value) || 0 })}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-neutral-700 mb-1">End Odometer (KM)</label>
              <Input
                type="number"
                min="0"
                step="0.1"
                required
                value={formData.endOdometer || ''}
                onChange={(e) => setFormData({ ...formData, endOdometer: parseFloat(e.target.value) || 0 })}
              />
            </div>
          </div>

          <div className="bg-neutral-50 p-4 rounded-xl border border-neutral-200">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-lg bg-primary-100 flex items-center justify-center">
                  <Calculator className="w-4 h-4 text-primary-600" />
                </div>
                <div>
                  <p className="text-sm font-medium text-neutral-900">Calculated Distance</p>
                  <p className="text-xs text-neutral-500">Based on odometer readings</p>
                </div>
              </div>
              <div className="text-right">
                <p className="text-xl font-bold text-neutral-900">{calculatedDistance.toFixed(1)} KM</p>
              </div>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-neutral-700 mb-1">Description / Purpose</label>
            <textarea
              required
              rows={3}
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="w-full px-4 py-2 border border-neutral-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              placeholder="Provide reason for this trip..."
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-neutral-700 mb-1">Attachments</label>
            <div className="mt-1 flex items-center gap-4">
              <input
                type="file"
                ref={fileInputRef}
                className="hidden"
                onChange={handleFileUpload}
              />
              <AnimatedButton
                type="button"
                onClick={() => fileInputRef.current?.click()}
                disabled={isUploading}
                icon={UploadCloud}
                variant="secondary"
              >
                {isUploading ? 'Uploading...' : 'Upload Bill/Ticket'}
              </AnimatedButton>
              <span className="text-sm text-neutral-500">
                {formData.attachmentIds.length} file(s) attached
              </span>
            </div>
          </div>
        </form>
      </div>
      <div className="p-6 border-t border-neutral-200 bg-neutral-50 flex justify-end gap-3 rounded-b-2xl">
        <AnimatedButton type="button" onClick={onClose} variant="secondary">
          Cancel
        </AnimatedButton>
        <AnimatedButton
          type="submit"
          form="trip-sheet-form"
          disabled={isSubmitting || calculatedDistance <= 0}
        >
          {isSubmitting ? 'Submitting...' : 'Submit Claim'}
        </AnimatedButton>
      </div>
    </Modal>
  );
}
