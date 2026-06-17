import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { User, Mail, Phone, MapPin, Building2, Calendar, Briefcase, CreditCard, UserCheck, Heart, Edit2, Camera, Shield, Award } from 'lucide-react';
import { GlassCard, AnimatedButton, StatusBadge, Modal, Input } from '../../components/ui';
import { DashboardLayout } from '../../components/layout';
import { getCurrentUser, UserProfile, updateProfile } from '../../services/authService';
import { useAuth } from '../../context/AuthContext';

export const Profile: React.FC = () => {
  const { refreshUser } = useAuth();
  const [activeTab, setActiveTab] = useState<'personal' | 'bank' | 'emergency'>('personal');
  const [profile, setProfile] = useState<UserProfile | null>(null);
  
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [editForm, setEditForm] = useState({ name: '', phone: '', address: '' });
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    const loadProfile = async () => {
      try {
        const user = await getCurrentUser();
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
        name: profile.name || '',
        phone: profile.phone || '',
        address: profile.address || '',
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

  const bankDetails = profile?.bankDetails ?? { bankName: '', accountNumber: '', ifscCode: '' };
  const emergencyContact = profile?.emergencyContact ?? { name: '', relationship: '', phone: '' };
  const initials = (profile?.name ?? profile?.empId ?? 'E').split(' ').map((part) => part[0]).join('').slice(0, 2).toUpperCase();

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
                    <h2 className="text-xl font-bold text-neutral-900">{profile?.name ?? 'Employee'}</h2>
                    <StatusBadge status="success" label="Active" size="sm" />
                  </div>
                  <p className="text-sm text-neutral-600">{profile?.designation ?? 'Designation not available'}</p>
                  <p className="text-xs text-neutral-500 mt-1">{profile?.department ?? 'Department not available'}{profile?.branch ? ` | ${profile.branch}` : ''}</p>
                </div>
                <AnimatedButton variant="secondary" size="sm" icon={Edit2} onClick={handleEditClick}>Edit Profile</AnimatedButton>
              </div>
            </div>
          </GlassCard>
        </motion.div>

        <div className="flex items-center gap-2 overflow-x-auto pb-2">
          {[
            { id: 'personal', label: 'Personal Details', icon: User },
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
                        { icon: UserCheck, label: 'Employee ID', value: profile?.empId ?? 'N/A' },
                        { icon: Mail, label: 'Email', value: profile?.email ?? 'Not available' },
                        { icon: Phone, label: 'Phone', value: profile?.phone ?? 'Not available' },
                        { icon: Calendar, label: 'Joining Date', value: profile?.joiningDate ?? 'Not available' },
                        { icon: Briefcase, label: 'Employee Type', value: profile?.employeeType ?? 'Not available' },
                        { icon: User, label: 'Reporting To', value: profile?.reportingTo ?? 'Not available' },
                      ].map((item) => (
                        <div key={item.label} className="p-4 rounded-xl bg-neutral-50 border border-neutral-200">
                          <div className="flex items-center gap-2 text-neutral-400 mb-1"><item.icon className="w-4 h-4" /><span className="text-xs">{item.label}</span></div>
                          <p className="text-sm font-medium text-neutral-900">{item.value}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                  <div>
                    <h3 className="text-sm font-semibold text-primary-600 uppercase tracking-wider mb-4 flex items-center gap-2"><MapPin className="w-4 h-4" />Address</h3>
                    <div className="p-4 rounded-xl bg-neutral-50 border border-neutral-200">
                      <p className="text-sm text-neutral-700">{profile?.address ?? 'Address not available'}</p>
                    </div>
                  </div>
                </div>
                <div className="space-y-6">
                  <div>
                    <h3 className="text-sm font-semibold text-primary-600 uppercase tracking-wider mb-4 flex items-center gap-2"><Building2 className="w-4 h-4" />Organization</h3>
                    <div className="space-y-4">
                      {[
                        { label: 'Department', value: profile?.department ?? 'Not available' },
                        { label: 'Branch', value: profile?.branch ?? 'Not available' },
                        { label: 'Designation', value: profile?.designation ?? 'Not available' },
                      ].map((item) => (
                        <div key={item.label} className="p-4 rounded-xl bg-primary-50 border border-primary-200">
                          <p className="text-xs text-neutral-500 mb-1">{item.label}</p>
                          <p className="text-sm font-medium text-neutral-900">{item.value}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                  <div>
                    <h3 className="text-sm font-semibold text-primary-600 uppercase tracking-wider mb-4 flex items-center gap-2"><Award className="w-4 h-4" />Quick Stats</h3>
                    <div className="grid grid-cols-2 gap-3">
                      <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200 text-center">
                        <p className="text-2xl font-bold text-emerald-600">--</p>
                        <p className="text-xs text-neutral-600">Years</p>
                      </div>
                      <div className="p-4 rounded-xl bg-blue-50 border border-blue-200 text-center">
                        <p className="text-2xl font-bold text-blue-600">--</p>
                        <p className="text-xs text-neutral-600">Leave Balance</p>
                      </div>
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
                      { label: 'Branch', value: profile?.branch || 'Not available' },
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
                    <div className="flex items-start gap-3"><Heart className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" /><div><p className="text-sm font-medium text-neutral-900">Important</p><p className="text-xs text-neutral-600 mt-1">This contact will be notified in case of emergencies. Keep this information up to date.</p></div></div>
                  </div>
                </div>
              </div>
            </GlassCard>
          )}
        </motion.div>
      </div>

      <Modal isOpen={isEditModalOpen} onClose={() => setIsEditModalOpen(false)} title="Edit Profile">
        <div className="space-y-4">
          <Input 
            label="Full Name" 
            value={editForm.name} 
            onChange={(e) => setEditForm({ ...editForm, name: e.target.value })} 
            placeholder="John Doe" 
          />
          <Input 
            label="Phone Number" 
            value={editForm.phone} 
            onChange={(e) => setEditForm({ ...editForm, phone: e.target.value })} 
            placeholder="+91 9876543210" 
          />
          <Input 
            label="Address" 
            value={editForm.address} 
            onChange={(e) => setEditForm({ ...editForm, address: e.target.value })} 
            placeholder="123 Street Name, City, Country" 
          />
          
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
