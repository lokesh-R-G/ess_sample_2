import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { User, Mail, Phone, MapPin, Building2, Calendar, Briefcase, CreditCard, UserCheck, Heart, Edit2, Camera, Shield, Award } from 'lucide-react';
import { GlassCard, AnimatedButton, StatusBadge, Modal, Input } from '../../components/ui';
import { DashboardLayout } from '../../components/layout';
import { getProfile, UserProfile, updateProfile } from '../../services/authService';
import { useAuth } from '../../context/AuthContext';

export const Profile: React.FC = () => {
  const { refreshUser } = useAuth();
  const [activeTab, setActiveTab] = useState<'personal' | 'bank' | 'emergency'>('personal');
  const [profile, setProfile] = useState<UserProfile | null>(null);
  
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [editForm, setEditForm] = useState({ 
    mobilePhone: '', 
    personalEmail: '', 
    currentAddressLine1: '',
    currentCity: '',
    currentState: '',
    currentCountry: '',
    currentPincode: ''
  });
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    const loadProfile = async () => {
      try {
        const user = await getProfile();
        setProfile(user);
      } catch {
        setProfile(null);
      }
    };

    loadProfile();
  }, [isEditModalOpen]); // reload after modal closes if it was saved

  const handleEditClick = () => {
    if (profile) {
      setEditForm({
        mobilePhone: profile.contact?.mobilePhone || '',
        personalEmail: profile.contact?.personalEmail || '',
        currentAddressLine1: profile.address?.currentAddressLine1 || '',
        currentCity: profile.address?.currentCity || '',
        currentState: profile.address?.currentState || '',
        currentCountry: profile.address?.currentCountry || '',
        currentPincode: profile.address?.currentPincode || ''
      });
      setIsEditModalOpen(true);
    }
  };

  const handleSaveProfile = async () => {
    try {
      setIsSaving(true);
      await updateProfile(editForm);
      await refreshUser();
      setIsEditModalOpen(false);
    } catch (err) {
      console.error('Failed to update profile', err);
    } finally {
      setIsSaving(false);
    }
  };

  if (!profile) return <DashboardLayout><div className="flex justify-center p-8">Loading Profile...</div></DashboardLayout>;

  const bankDetails = profile.bank ?? { bankName: '', accountNumber: '', ifscCode: '' };
  const emergencyContact = profile.emergencyContact ?? { name: '', relationship: '', phone: '' };
  const personal = profile.personal ?? {};
  const contact = profile.contact ?? {};
  const address = profile.address ?? {};
  const employment = profile.employment ?? {};
  
  const fullName = `${personal.firstName || ''} ${personal.lastName || ''}`.trim() || personal.employeeCode || 'Employee';
  const initials = fullName.split(' ').map((part) => part[0]).join('').slice(0, 2).toUpperCase();
  const formattedAddress = [address.currentAddressLine1, address.currentCity, address.currentState, address.currentCountry].filter(Boolean).join(', ') || 'Address not available';

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <GlassCard className="overflow-hidden">
            <div className="relative h-28 bg-gradient-to-r from-primary-500 to-primary-600" />
            <div className="relative px-6 pb-6">
              <div className="flex flex-col sm:flex-row items-center sm:items-end gap-4 -mt-12">
                <div className="relative group">
                  <div className="w-24 h-24 rounded-2xl bg-primary-500 text-white flex items-center justify-center border-4 border-white shadow-lg text-2xl font-bold">{initials}</div>
                  <motion.button className="absolute inset-0 flex items-center justify-center bg-primary-900/50 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity" whileHover={{ scale: 1.05 }}>
                    <Camera className="w-6 h-6 text-white" />
                  </motion.button>
                </div>
                <div className="flex-1 text-center sm:text-left">
                  <div className="flex flex-col sm:flex-row sm:items-center gap-2 mb-1">
                    <h2 className="text-xl font-bold text-neutral-900">{fullName}</h2>
                    <StatusBadge status="success" label={employment.status || 'Active'} size="sm" />
                  </div>
                  <p className="text-sm text-neutral-600">{employment.designation || 'Designation not available'}</p>
                  <p className="text-xs text-neutral-500 mt-1">{employment.department || 'Department not available'}{employment.branch ? ` | ${employment.branch}` : ''}</p>
                </div>
                {profile.permissions?.canEditMobile && (
                  <AnimatedButton variant="secondary" size="sm" icon={Edit2} onClick={handleEditClick}>Edit Profile</AnimatedButton>
                )}
              </div>
            </div>
          </GlassCard>
        </motion.div>

        <div className="flex items-center gap-2 overflow-x-auto pb-2">
          {[
            { id: 'personal', label: 'Personal & Employment', icon: User },
            { id: 'bank', label: 'Bank Details', icon: CreditCard },
            { id: 'emergency', label: 'Emergency Contact', icon: Heart },
          ].map((tab) => (
            <motion.button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as typeof activeTab)}
              className={`flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium whitespace-nowrap transition-all ${activeTab === tab.id ? 'bg-primary-50 text-primary-600 border border-primary-300' : 'text-neutral-500 hover:bg-neutral-100 hover:text-neutral-700 border border-transparent'}`}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <tab.icon className="w-4 h-4" />
              {tab.label}
            </motion.button>
          ))}
        </div>

        <motion.div key={activeTab} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -20 }}>
          {activeTab === 'personal' && (
            <GlassCard className="p-6">
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="lg:col-span-2 space-y-6">
                  <div>
                    <h3 className="text-sm font-semibold text-primary-600 uppercase tracking-wider mb-4 flex items-center gap-2"><User className="w-4 h-4" />Basic Information</h3>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      {[
                        { icon: UserCheck, label: 'Employee Code', value: personal.employeeCode || 'N/A' },
                        { icon: Mail, label: 'Work Email', value: contact.personalEmail || 'Not available' },
                        { icon: Phone, label: 'Mobile', value: contact.mobilePhone || 'Not available' },
                        { icon: Calendar, label: 'Date of Birth', value: personal.dob ? new Date(personal.dob).toLocaleDateString() : 'Not available' },
                        { icon: User, label: 'Gender', value: personal.gender || 'Not available' },
                        { icon: Heart, label: 'Blood Group', value: personal.bloodGroup || 'Not available' },
                      ].map((item) => (
                        <div key={item.label} className="p-4 rounded-xl bg-neutral-50 border border-neutral-200">
                          <div className="flex items-center gap-2 text-neutral-400 mb-1"><item.icon className="w-4 h-4" /><span className="text-xs">{item.label}</span></div>
                          <p className="text-sm font-medium text-neutral-900">{item.value}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                  <div>
                    <h3 className="text-sm font-semibold text-primary-600 uppercase tracking-wider mb-4 flex items-center gap-2"><MapPin className="w-4 h-4" />Current Address</h3>
                    <div className="p-4 rounded-xl bg-neutral-50 border border-neutral-200">
                      <p className="text-sm text-neutral-700">{formattedAddress}</p>
                      {address.currentPincode && <p className="text-xs text-neutral-500 mt-1">PIN: {address.currentPincode}</p>}
                    </div>
                  </div>
                </div>
                <div className="space-y-6">
                  <div>
                    <h3 className="text-sm font-semibold text-primary-600 uppercase tracking-wider mb-4 flex items-center gap-2"><Building2 className="w-4 h-4" />Employment</h3>
                    <div className="space-y-4">
                      {[
                        { label: 'Date of Joining', value: employment.dateOfJoining ? new Date(employment.dateOfJoining).toLocaleDateString() : 'Not available' },
                        { label: 'Organization', value: employment.organization || 'Not available' },
                        { label: 'Department', value: employment.department || 'Not available' },
                        { label: 'Branch', value: employment.branch || 'Not available' },
                        { label: 'Designation', value: employment.designation || 'Not available' },
                        { label: 'Reporting Manager', value: employment.reportingManager || 'Not available' },
                      ].map((item) => (
                        <div key={item.label} className="p-4 rounded-xl bg-primary-50 border border-primary-200">
                          <p className="text-xs text-neutral-500 mb-1">{item.label}</p>
                          <p className="text-sm font-medium text-neutral-900">{item.value}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </GlassCard>
          )}
          {activeTab === 'bank' && (
            <GlassCard className="p-6">
              <div className="max-w-xl mx-auto">
                <h3 className="text-sm font-semibold text-primary-600 uppercase tracking-wider mb-4 flex items-center gap-2"><CreditCard className="w-4 h-4" />Bank Account Details</h3>
                <div className="space-y-4">
                  <div className="p-4 rounded-xl bg-primary-500 text-white">
                    <div className="flex items-center gap-2 mb-3"><Building2 className="w-5 h-5" /><span className="text-sm font-medium">{bankDetails.bankName || 'Bank details not available'}</span></div>
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-xs text-white/70 mb-1">Account Number</p>
                        <p className="text-lg font-semibold tracking-wider">{bankDetails.accountNumber || 'Not available'}</p>
                      </div>
                    </div>
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    {[
                      { label: 'IFSC Code', value: bankDetails.ifscCode || 'Not available' },
                      { label: 'Account Type', value: bankDetails.accountType || 'Not available' },
                    ].map((item) => (
                      <div key={item.label} className="p-4 rounded-xl bg-neutral-50 border border-neutral-200">
                        <p className="text-xs text-neutral-500 mb-1">{item.label}</p>
                        <p className="text-sm font-medium text-neutral-900">{item.value}</p>
                      </div>
                    ))}
                  </div>
                  <div className="p-4 rounded-xl bg-amber-50 border border-amber-200">
                    <div className="flex items-start gap-3"><Shield className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" /><div><p className="text-sm font-medium text-neutral-900">Secure Information</p><p className="text-xs text-neutral-600 mt-1">Your bank details are encrypted and securely stored. Contact HR to update.</p></div></div>
                  </div>
                </div>
              </div>
            </GlassCard>
          )}
          {activeTab === 'emergency' && (
            <GlassCard className="p-6">
              <div className="max-w-xl mx-auto">
                <h3 className="text-sm font-semibold text-amber-600 uppercase tracking-wider mb-4 flex items-center gap-2"><Heart className="w-4 h-4" />Emergency Contact</h3>
                <div className="space-y-4">
                  <div className="p-5 rounded-xl bg-neutral-50 border border-neutral-200">
                    <div className="flex items-center gap-4">
                      <div className="w-14 h-14 rounded-xl bg-red-100 flex items-center justify-center"><Heart className="w-7 h-7 text-red-600" /></div>
                      <div>
                        <p className="text-lg font-semibold text-neutral-900">{emergencyContact.name || 'Not available'}</p>
                        <p className="text-sm text-neutral-600">{emergencyContact.relationship || 'Not available'}</p>
                      </div>
                    </div>
                  </div>
                  <div className="p-4 rounded-xl bg-neutral-50 border border-neutral-200">
                    <div className="flex items-center gap-3"><Phone className="w-5 h-5 text-primary-500" /><div><p className="text-xs text-neutral-500">Phone Number</p><p className="text-sm font-medium text-neutral-900">{emergencyContact.phone || 'Not available'}</p></div></div>
                  </div>
                  <div className="p-4 rounded-xl bg-amber-50 border border-amber-200">
                    <div className="flex items-start gap-3"><Shield className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" /><div><p className="text-sm font-medium text-neutral-900">Read Only</p><p className="text-xs text-neutral-600 mt-1">This contact will be notified in case of emergencies. Contact HR to update.</p></div></div>
                  </div>
                </div>
              </div>
            </GlassCard>
          )}
        </motion.div>
      </div>

      <Modal isOpen={isEditModalOpen} onClose={() => setIsEditModalOpen(false)} title="Update Contact Information">
        <div className="space-y-4">
          <div className="pt-2">
            <h4 className="text-sm font-semibold text-neutral-900 mb-3">Contact Details</h4>
            <div className="space-y-4">
              <Input 
                label="Mobile Phone" 
                value={editForm.mobilePhone} 
                onChange={(e) => setEditForm({ ...editForm, mobilePhone: e.target.value })} 
                placeholder="+91 9876543210" 
              />
              <Input 
                label="Personal Email" 
                value={editForm.personalEmail} 
                onChange={(e) => setEditForm({ ...editForm, personalEmail: e.target.value })} 
                placeholder="email@example.com" 
              />
            </div>
          </div>
          <div className="pt-2">
            <h4 className="text-sm font-semibold text-neutral-900 mb-3">Current Address</h4>
            <div className="space-y-4">
              <Input 
                label="Address Line 1" 
                value={editForm.currentAddressLine1} 
                onChange={(e) => setEditForm({ ...editForm, currentAddressLine1: e.target.value })} 
                placeholder="123 Street Name" 
              />
              <Input 
                label="City" 
                value={editForm.currentCity} 
                onChange={(e) => setEditForm({ ...editForm, currentCity: e.target.value })} 
                placeholder="City" 
              />
              <div className="grid grid-cols-2 gap-4">
                <Input 
                  label="State" 
                  value={editForm.currentState} 
                  onChange={(e) => setEditForm({ ...editForm, currentState: e.target.value })} 
                  placeholder="State" 
                />
                <Input 
                  label="PIN Code" 
                  value={editForm.currentPincode} 
                  onChange={(e) => setEditForm({ ...editForm, currentPincode: e.target.value })} 
                  placeholder="PIN" 
                />
              </div>
              <Input 
                label="Country" 
                value={editForm.currentCountry} 
                onChange={(e) => setEditForm({ ...editForm, currentCountry: e.target.value })} 
                placeholder="Country" 
              />
            </div>
          </div>
          
          <div className="flex justify-end gap-3 pt-4">
            <AnimatedButton variant="secondary" onClick={() => setIsEditModalOpen(false)}>Cancel</AnimatedButton>
            <AnimatedButton onClick={handleSaveProfile} loading={isSaving}>Save Changes</AnimatedButton>
          </div>
        </div>
      </Modal>

    </DashboardLayout>
  );
};

export default Profile;
