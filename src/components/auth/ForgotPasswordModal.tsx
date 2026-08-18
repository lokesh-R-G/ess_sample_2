import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Mail, Key, Lock, ArrowRight, CheckCircle } from 'lucide-react';
import { authApi } from '../../services/authService';
import AnimatedButton from '../ui/AnimatedButton';

interface ForgotPasswordModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const ForgotPasswordModal: React.FC<ForgotPasswordModalProps> = ({ isOpen, onClose }) => {
  const [step, setStep] = useState<1 | 2 | 3>(1);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  
  const [employeeCode, setEmployeeCode] = useState('');
  const [email, setEmail] = useState('');
  const [otp, setOtp] = useState('');
  const [resetToken, setResetToken] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [successMsg, setSuccessMsg] = useState('');

  const handleClose = () => {
    // Reset state on close
    setStep(1);
    setEmployeeCode('');
    setEmail('');
    setOtp('');
    setResetToken('');
    setNewPassword('');
    setConfirmPassword('');
    setError('');
    setSuccessMsg('');
    onClose();
  };

  const handleRequestOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    try {
      await authApi.forgotPassword(employeeCode, email);
      // Backend returns a generic message even if failed. We just proceed to step 2 for OTP entry
      setStep(2);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'The employee code or email is invalid.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleVerifyOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    try {
      const response = await authApi.verifyResetOtp(employeeCode, email, otp);
      setResetToken(response.resetToken);
      setStep(3);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Invalid or expired OTP.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleResetPassword = async (e: React.FormEvent) => {
    e.preventDefault();
    if (newPassword !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }
    setIsLoading(true);
    setError('');
    try {
      await authApi.resetPassword(employeeCode, resetToken, newPassword, confirmPassword);
      setSuccessMsg('Password reset successfully. You can now login with your new password.');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to reset password.');
    } finally {
      setIsLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-neutral-900/50 backdrop-blur-sm">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.95 }}
          className="bg-white rounded-2xl shadow-xl w-full max-w-md overflow-hidden relative"
        >
          <button
            onClick={handleClose}
            className="absolute top-4 right-4 text-neutral-400 hover:text-neutral-600 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>

          <div className="p-8">
            <h2 className="text-2xl font-bold text-neutral-900 mb-2">Reset Password</h2>
            
            {successMsg ? (
              <div className="text-center py-6">
                <CheckCircle className="w-12 h-12 text-green-500 mx-auto mb-4" />
                <p className="text-neutral-700">{successMsg}</p>
                <AnimatedButton variant="primary" className="mt-6" onClick={handleClose} fullWidth>
                  Back to Login
                </AnimatedButton>
              </div>
            ) : (
              <>
                <p className="text-neutral-500 mb-6 text-sm">
                  {step === 1 && "Enter your Employee Code and Personal Email to receive a reset code."}
                  {step === 2 && "Enter the 6-digit code sent to your personal email."}
                  {step === 3 && "Create a new, strong password."}
                </p>

                {error && (
                  <div className="mb-4 p-3 bg-red-50 text-red-700 rounded-lg text-sm border border-red-100">
                    {error}
                  </div>
                )}

                {step === 1 && (
                  <form onSubmit={handleRequestOtp} className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-neutral-700 mb-1">Employee Code</label>
                      <div className="relative">
                        <Key className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-neutral-400" />
                        <input
                          type="text"
                          required
                          value={employeeCode}
                          onChange={(e) => setEmployeeCode(e.target.value)}
                          className="w-full pl-10 pr-4 py-2 border border-neutral-300 rounded-lg focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500"
                          placeholder="e.g. 202102"
                        />
                      </div>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-neutral-700 mb-1">Personal Email</label>
                      <div className="relative">
                        <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-neutral-400" />
                        <input
                          type="email"
                          required
                          value={email}
                          onChange={(e) => setEmail(e.target.value)}
                          className="w-full pl-10 pr-4 py-2 border border-neutral-300 rounded-lg focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500"
                          placeholder="your.email@example.com"
                        />
                      </div>
                    </div>
                    <AnimatedButton type="submit" variant="primary" fullWidth loading={isLoading} icon={ArrowRight} iconPosition="right">
                      Send OTP
                    </AnimatedButton>
                  </form>
                )}

                {step === 2 && (
                  <form onSubmit={handleVerifyOtp} className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-neutral-700 mb-1">6-Digit OTP</label>
                      <input
                        type="text"
                        required
                        maxLength={6}
                        pattern="\d{6}"
                        value={otp}
                        onChange={(e) => setOtp(e.target.value)}
                        className="w-full px-4 py-2 border border-neutral-300 rounded-lg focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 text-center tracking-widest text-lg"
                        placeholder="000000"
                      />
                    </div>
                    <AnimatedButton type="submit" variant="primary" fullWidth loading={isLoading}>
                      Verify OTP
                    </AnimatedButton>
                  </form>
                )}

                {step === 3 && (
                  <form onSubmit={handleResetPassword} className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-neutral-700 mb-1">New Password</label>
                      <div className="relative">
                        <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-neutral-400" />
                        <input
                          type="password"
                          required
                          value={newPassword}
                          onChange={(e) => setNewPassword(e.target.value)}
                          className="w-full pl-10 pr-4 py-2 border border-neutral-300 rounded-lg focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500"
                          placeholder="••••••••"
                        />
                      </div>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-neutral-700 mb-1">Confirm Password</label>
                      <div className="relative">
                        <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-neutral-400" />
                        <input
                          type="password"
                          required
                          value={confirmPassword}
                          onChange={(e) => setConfirmPassword(e.target.value)}
                          className="w-full pl-10 pr-4 py-2 border border-neutral-300 rounded-lg focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500"
                          placeholder="••••••••"
                        />
                      </div>
                    </div>
                    <AnimatedButton type="submit" variant="primary" fullWidth loading={isLoading}>
                      Reset Password
                    </AnimatedButton>
                  </form>
                )}
              </>
            )}
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
};

export default ForgotPasswordModal;
