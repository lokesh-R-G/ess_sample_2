import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
<<<<<<< HEAD
import { User, Lock, Eye, EyeOff, ArrowRight } from 'lucide-react';
import { BackgroundParticles, AnimatedButton } from '../../components/ui';
import { useAuth } from '../../context/AuthContext';

export const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [showPassword, setShowPassword] = useState(false);
  const [formData, setFormData] = useState({ employeeId: '', password: '' });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      const result = await login(formData.employeeId.trim(), formData.password);
      navigate(result.mustChangePassword ? '/change-password' : '/dashboard', { replace: true });
    } catch (submissionError) {
      setError(submissionError instanceof Error ? submissionError.message : 'Unable to sign in');
    } finally {
      setIsLoading(false);
    }
=======
import { User, Lock, Building2, Eye, EyeOff, ArrowRight } from 'lucide-react';
import { BackgroundParticles, AnimatedButton, Select } from '../../components/ui';

interface LoginPageProps {
  onLogin?: () => void;
}

export const LoginPage: React.FC<LoginPageProps> = ({ onLogin }) => {
  const navigate = useNavigate();
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);
  const [formData, setFormData] = useState({
    employeeId: '',
    branch: '',
    password: '',
  });
  const [isLoading, setIsLoading] = useState(false);

  const branches = [
    { value: 'BR-001', label: 'Bangalore HQ' },
    { value: 'BR-002', label: 'Mumbai Office' },
    { value: 'BR-003', label: 'Delhi NCR' },
    { value: 'BR-004', label: 'Chennai Branch' },
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    await new Promise((resolve) => setTimeout(resolve, 1500));
    setIsLoading(false);
    onLogin?.();
    navigate('/dashboard');
>>>>>>> d905dc76d127cb40376e7b8239e6f855343afc15
  };

  return (
    <div className="min-h-screen relative overflow-hidden flex items-center justify-center p-4 bg-gradient-to-br from-neutral-50 to-white">
      {/* Background Effects */}
      <BackgroundParticles />

      {/* Login Card */}
      <motion.div
        className="relative w-full max-w-md"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
      >
        {/* Main Card */}
        <motion.div
          className="relative bg-white rounded-2xl border border-neutral-200 shadow-xl overflow-hidden"
          transition={{ duration: 0.2 }}
        >
          {/* Logo Section */}
          <div className="p-8 text-center bg-gradient-to-r from-primary-500 to-primary-600">
            <motion.div
              className="inline-flex items-center justify-center w-20 h-20 rounded-2xl bg-white mb-4 shadow-lg"
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.2, type: 'spring', stiffness: 300 }}
            >
              <span className="text-primary-500 font-bold text-2xl">IDS</span>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
            >
              <h1 className="text-2xl font-bold text-white mb-1">IDS Pvt Ltd</h1>
              <p className="text-sm text-white/90">Employee Self Service Portal</p>
            </motion.div>
          </div>

          {/* Form Section */}
          <form onSubmit={handleSubmit} className="p-8 space-y-5">
            {/* Employee ID */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.4 }}
            >
              <label className="block text-sm font-medium text-neutral-700 mb-1.5">
                Employee ID
              </label>
              <div className="relative">
                <User className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-neutral-400" />
                <input
                  type="text"
                  value={formData.employeeId}
                  onChange={(e) => setFormData({ ...formData, employeeId: e.target.value })}
                  placeholder="Enter your Employee ID"
                  className="w-full pl-12 pr-4 py-3.5 rounded-xl bg-white border border-neutral-300 text-neutral-900 placeholder-neutral-400 focus:outline-none focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20 transition-all"
                  required
                />
              </div>
            </motion.div>

<<<<<<< HEAD
            {/* Password */}
=======
            {/* Branch Selection */}
>>>>>>> d905dc76d127cb40376e7b8239e6f855343afc15
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.5 }}
            >
              <label className="block text-sm font-medium text-neutral-700 mb-1.5">
<<<<<<< HEAD
=======
                Branch
              </label>
              <div className="relative">
                <Building2 className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-neutral-400 z-10" />
                <select
                  value={formData.branch}
                  onChange={(e) => setFormData({ ...formData, branch: e.target.value })}
                  className="w-full pl-12 pr-10 py-3.5 rounded-xl appearance-none bg-white border border-neutral-300 text-neutral-900 focus:outline-none focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20 transition-all cursor-pointer"
                  required
                >
                  <option value="" disabled className="bg-white">Select Branch</option>
                  {branches.map((branch) => (
                    <option key={branch.value} value={branch.value} className="bg-white">
                      {branch.label}
                    </option>
                  ))}
                </select>
                <div className="absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none">
                  <svg className="w-4 h-4 text-neutral-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </div>
              </div>
            </motion.div>

            {/* Password */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.6 }}
            >
              <label className="block text-sm font-medium text-neutral-700 mb-1.5">
>>>>>>> d905dc76d127cb40376e7b8239e6f855343afc15
                Password
              </label>
              <div className="relative">
                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-neutral-400" />
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  placeholder="Enter your password"
                  className="w-full pl-12 pr-12 py-3.5 rounded-xl bg-white border border-neutral-300 text-neutral-900 placeholder-neutral-400 focus:outline-none focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20 transition-all"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-4 top-1/2 -translate-y-1/2 text-neutral-400 hover:text-neutral-600 transition-colors"
                >
                  {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
              </div>
            </motion.div>

            {/* Remember Me & Forgot Password */}
            <motion.div
              className="flex items-center justify-between"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
<<<<<<< HEAD
              transition={{ delay: 0.6 }}
            >
              <span className="text-sm text-neutral-500">Use your Employee ID and default password on first login.</span>
=======
              transition={{ delay: 0.7 }}
            >
              <label className="flex items-center gap-2 cursor-pointer group">
                <div className="relative">
                  <input
                    type="checkbox"
                    checked={rememberMe}
                    onChange={(e) => setRememberMe(e.target.checked)}
                    className="sr-only"
                  />
                  <div className={`w-5 h-5 rounded-md border-2 transition-all ${
                    rememberMe
                      ? 'bg-primary-500 border-primary-500'
                      : 'border-neutral-300 group-hover:border-primary-400'
                  }`}>
                    {rememberMe && (
                      <svg className="w-full h-full text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                      </svg>
                    )}
                  </div>
                </div>
                <span className="text-sm text-neutral-600 group-hover:text-neutral-800 transition-colors">Remember me</span>
              </label>
>>>>>>> d905dc76d127cb40376e7b8239e6f855343afc15
              <button type="button" className="text-sm text-primary-500 hover:text-primary-600 transition-colors">
                Forgot Password?
              </button>
            </motion.div>

<<<<<<< HEAD
            {error ? <p className="text-sm text-red-600">{error}</p> : null}

=======
>>>>>>> d905dc76d127cb40376e7b8239e6f855343afc15
            {/* Login Button */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
<<<<<<< HEAD
              transition={{ delay: 0.7 }}
=======
              transition={{ delay: 0.8 }}
>>>>>>> d905dc76d127cb40376e7b8239e6f855343afc15
            >
              <AnimatedButton
                type="submit"
                variant="primary"
                size="lg"
                fullWidth
                loading={isLoading}
                icon={ArrowRight}
                iconPosition="right"
              >
                {isLoading ? 'Signing in...' : 'Sign In'}
              </AnimatedButton>
            </motion.div>

<<<<<<< HEAD
=======
            {/* Demo Credentials */}
            <motion.div
              className="text-center pt-4 border-t border-neutral-200"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.9 }}
            >
              <p className="text-xs text-neutral-500 mb-2">Demo Credentials</p>
              <div className="text-xs text-neutral-600 space-y-0.5">
                <p>Employee ID: <span className="text-primary-500 font-medium">EMP-001</span></p>
                <p>Password: <span className="text-primary-500 font-medium">demo@123</span></p>
              </div>
            </motion.div>
>>>>>>> d905dc76d127cb40376e7b8239e6f855343afc15
          </form>
        </motion.div>

        {/* Footer */}
        <motion.p
          className="text-center text-xs text-neutral-500 mt-6"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1 }}
        >
          Powered by <span className="text-primary-500 font-medium">IDS Pvt Ltd</span> | Enterprise HRMS v2.0
        </motion.p>
      </motion.div>
    </div>
  );
};

export default LoginPage;
