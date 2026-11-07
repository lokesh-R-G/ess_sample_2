import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ShieldAlert, ArrowLeft, Home } from 'lucide-react';
import { motion } from 'framer-motion';

const AccessRestrictedPage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-neutral-50 flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="max-w-md w-full bg-white rounded-2xl shadow-xl overflow-hidden border border-neutral-100"
      >
        <div className="bg-red-50 p-6 flex justify-center border-b border-red-100">
          <div className="w-20 h-20 bg-red-100 rounded-full flex items-center justify-center">
            <ShieldAlert className="w-10 h-10 text-red-600" />
          </div>
        </div>
        
        <div className="p-8 text-center space-y-4">
          <h1 className="text-3xl font-bold text-neutral-900">403</h1>
          <h2 className="text-xl font-semibold text-neutral-800">Access Restricted</h2>
          <p className="text-neutral-500">
            You don't have permission to access this page. If you believe this is an error, please contact your administrator.
          </p>

          <div className="pt-6 flex flex-col sm:flex-row gap-3 justify-center">
            <button
              onClick={() => navigate(-1)}
              className="flex items-center justify-center gap-2 px-6 py-2.5 rounded-xl border border-neutral-200 text-neutral-600 hover:bg-neutral-50 font-medium transition-colors"
            >
              <ArrowLeft className="w-4 h-4" />
              Go Back
            </button>
            <button
              onClick={() => navigate('/dashboard')}
              className="flex items-center justify-center gap-2 px-6 py-2.5 rounded-xl bg-primary-600 text-white hover:bg-primary-700 font-medium transition-colors shadow-sm"
            >
              <Home className="w-4 h-4" />
              Dashboard
            </button>
          </div>
        </div>
      </motion.div>
    </div>
  );
};

export default AccessRestrictedPage;
