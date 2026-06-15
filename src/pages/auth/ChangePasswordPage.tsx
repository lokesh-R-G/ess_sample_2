import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Lock, ArrowRight } from 'lucide-react';
import { AnimatedButton, BackgroundParticles, GlassCard, Input } from '../../components/ui';
import { useAuth } from '../../context/AuthContext';

export default function ChangePasswordPage() {
  const navigate = useNavigate();
  const { changePassword } = useAuth();
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setError('');

    if (newPassword !== confirmPassword) {
      setError('New password and confirmation do not match');
      return;
    }

    try {
      setIsLoading(true);
      await changePassword(currentPassword, newPassword);
      navigate('/dashboard', { replace: true });
    } catch (submissionError) {
      setError(submissionError instanceof Error ? submissionError.message : 'Unable to change password');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen relative overflow-hidden flex items-center justify-center p-4 bg-gradient-to-br from-neutral-50 to-white">
      <BackgroundParticles />
      <GlassCard className="relative w-full max-w-md p-8">
        <div className="flex items-center gap-3 mb-6">
          <div className="w-12 h-12 rounded-xl bg-primary-500 flex items-center justify-center text-white">
            <Lock className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-neutral-900">Change Password</h1>
            <p className="text-sm text-neutral-500">Set your new password to continue</p>
          </div>
        </div>

        <form className="space-y-4" onSubmit={handleSubmit}>
          <Input label="Current Password" type="password" value={currentPassword} onChange={(e) => setCurrentPassword(e.target.value)} required />
          <Input label="New Password" type="password" value={newPassword} onChange={(e) => setNewPassword(e.target.value)} required />
          <Input label="Confirm Password" type="password" value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} required />
          {error ? <p className="text-sm text-red-600">{error}</p> : null}
          <AnimatedButton type="submit" variant="primary" size="lg" fullWidth loading={isLoading} icon={ArrowRight} iconPosition="right">
            Update Password
          </AnimatedButton>
        </form>
      </GlassCard>
    </div>
  );
}
