import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Bell, Search, Menu, User, Settings, LogOut, ChevronDown } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { notificationApi, Notification } from '../../services/notificationApi';
import { formatDistanceToNow } from 'date-fns';

interface HeaderProps {
  onMenuClick?: () => void;
  title?: string;
  subtitle?: string;
}

export const Header: React.FC<HeaderProps> = ({
  onMenuClick,
  title = 'Dashboard',
  subtitle,
}) => {
  const [showNotifications, setShowNotifications] = useState(false);
  const [showProfile, setShowProfile] = useState(false);
  const [searchFocused, setSearchFocused] = useState(false);
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  const handleLogout = () => {
    localStorage.removeItem('ess_auth_token');
    localStorage.removeItem('ess_auth_user');
    logout();
    navigate('/login');
  };

  const fetchNotifications = async () => {
    try {
      const [{ unreadCount = 0 } = {}, notifs = []] = await Promise.all([
        notificationApi.getUnreadCount(),
        notificationApi.getNotifications(5, 0)
      ]);
      setUnreadCount(unreadCount);
      setNotifications(notifs);
    } catch (error) {
      console.error('Failed to fetch notifications', error);
    }
  };

  useEffect(() => {
    fetchNotifications();
  }, []);

  const handleMarkAllRead = async () => {
    try {
      await notificationApi.markAllAsRead();
      await fetchNotifications();
    } catch (error) {
      console.error('Failed to mark all as read', error);
    }
  };

  const handleNotificationClick = async (notification: Notification) => {
    if (!notification.isRead) {
      try {
        await notificationApi.markAsRead(notification._id);
        setUnreadCount(prev => Math.max(0, prev - 1));
        setNotifications(prev => prev.map(n => n._id === notification._id ? { ...n, isRead: true } : n));
      } catch (error) {
        console.error('Failed to mark as read', error);
      }
    }
    // Simple navigation based on type
    if (notification.type === 'MESSAGE') {
      navigate('/mail');
    } else if (notification.type === 'APPROVAL') {
      navigate('/admin/leave-approvals');
    }
    setShowNotifications(false);
  };

  return (
    <header className="sticky top-0 z-30 bg-white border-b border-neutral-200">
      <div className="flex items-center justify-between h-16 px-4 lg:px-6">
        {/* Left Section */}
        <div className="flex items-center gap-4">
          <motion.button
            onClick={onMenuClick}
            className="lg:hidden p-2 rounded-lg hover:bg-neutral-100 text-neutral-500 hover:text-neutral-800 transition-colors"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <Menu className="w-5 h-5" />
          </motion.button>

          <div>
            <h1 className="text-lg font-semibold text-neutral-900">{title}</h1>
            {subtitle && <p className="text-xs text-neutral-500">{subtitle}</p>}
          </div>
        </div>

        {/* Center - Search */}
        <div className="hidden md:flex flex-1 max-w-md mx-8">
          <div className={`relative w-full transition-all duration-200 ${searchFocused ? 'scale-105' : ''}`}>
            <Search className={`absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 transition-colors ${searchFocused ? 'text-primary-500' : 'text-neutral-400'}`} />
            <input
              type="text"
              placeholder="Search..."
              onFocus={() => setSearchFocused(true)}
              onBlur={() => setSearchFocused(false)}
              className="w-full pl-10 pr-4 py-2 rounded-lg bg-white border border-neutral-300 text-neutral-900 placeholder-neutral-400 focus:outline-none focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20 transition-all"
            />
          </div>
        </div>

        {/* Right Section */}
        <div className="flex items-center gap-2">
          {/* Notifications */}
          <div className="relative">
            <motion.button
              onClick={() => {
                setShowNotifications(!showNotifications);
                if (!showNotifications) fetchNotifications();
              }}
              className="relative p-2.5 rounded-lg hover:bg-neutral-100 text-neutral-500 hover:text-neutral-800 transition-colors"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <Bell className="w-5 h-5" />
              {unreadCount > 0 && (
                <span className="absolute top-1 right-1 w-2 h-2 bg-primary-500 rounded-full" />
              )}
            </motion.button>

            <AnimatePresence>
              {showNotifications && (
                <motion.div
                  className="absolute right-0 mt-2 w-80 bg-white rounded-xl border border-neutral-200 shadow-xl overflow-hidden"
                  initial={{ opacity: 0, y: -10, scale: 0.95 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  exit={{ opacity: 0, y: -10, scale: 0.95 }}
                >
                  <div className="p-3 border-b border-neutral-200 flex items-center justify-between">
                    <h3 className="text-sm font-semibold text-neutral-900">Notifications</h3>
                    <button onClick={handleMarkAllRead} className="text-xs text-primary-500 cursor-pointer hover:underline">Mark all read</button>
                  </div>
                  <div className="max-h-80 overflow-y-auto">
                    {notifications.length === 0 ? (
                      <div className="p-4 text-center text-sm text-neutral-500">No notifications</div>
                    ) : (
                      notifications.map((notification) => (
                        <motion.div
                          key={notification._id}
                          onClick={() => handleNotificationClick(notification)}
                          className={`p-3 hover:bg-neutral-50 cursor-pointer border-b border-neutral-100 last:border-0 ${
                            !notification.isRead ? 'bg-primary-50/50' : ''
                          }`}
                          whileHover={{ x: 4 }}
                        >
                          <div className="flex items-start gap-3">
                            <div className={`w-2 h-2 mt-2 rounded-full ${!notification.isRead ? 'bg-primary-500' : 'bg-neutral-300'}`} />
                            <div className="flex-1">
                              <p className="text-sm font-medium text-neutral-800">{notification.title}</p>
                              <p className="text-xs text-neutral-500 mt-0.5">{notification.message}</p>
                              <p className="text-xs text-neutral-400 mt-1">{formatDistanceToNow(new Date(notification.createdAt), { addSuffix: true })}</p>
                            </div>
                          </div>
                        </motion.div>
                      ))
                    )}
                  </div>
                  <div className="p-2 border-t border-neutral-200 text-center">
                    <button onClick={() => navigate('/notifications')} className="text-xs text-primary-500 hover:underline">View all notifications</button>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>


          {/* Profile Dropdown */}
          <div className="relative">
            <motion.button
              onClick={() => setShowProfile(!showProfile)}
              className="flex items-center gap-2 p-1.5 pr-3 rounded-lg hover:bg-neutral-100 transition-colors"
              whileHover={{ scale: 1.02 }}
            >
              <div className="w-8 h-8 rounded-full bg-primary-100 border-2 border-primary-500 flex items-center justify-center">
                <span className="text-primary-600 text-xs font-semibold">
                  {user?.name ? user.name.split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase() : 'U'}
                </span>
              </div>
              <ChevronDown className="w-4 h-4 text-neutral-400" />
            </motion.button>

            <AnimatePresence>
              {showProfile && (
                <motion.div
                  className="absolute right-0 mt-2 w-56 bg-white rounded-xl border border-neutral-200 shadow-xl overflow-hidden"
                  initial={{ opacity: 0, y: -10, scale: 0.95 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  exit={{ opacity: 0, y: -10, scale: 0.95 }}
                >
                  <div className="p-3 border-b border-neutral-200">
                    <p className="text-sm font-medium text-neutral-900">{user?.name || 'User'}</p>
                    <p className="text-xs text-neutral-500">{user?.email || 'email@notavailable.com'}</p>
                    <p className="text-xs text-neutral-400 mt-1">Employee ID: {user?.empId || 'N/A'}</p>
                  </div>
                  <div className="p-2">
                    {[
                      { icon: User, label: 'My Profile', path: '/profile' },
                      { icon: Settings, label: 'Settings', path: '/settings' },
                    ].map((item) => (
                      <motion.button
                        key={item.label}
                        onClick={() => {
                          navigate(item.path);
                          setShowProfile(false);
                        }}
                        className="flex items-center gap-3 w-full px-3 py-2 rounded-lg text-neutral-600 hover:bg-neutral-100 hover:text-neutral-900 transition-colors"
                        whileHover={{ x: 4 }}
                      >
                        <item.icon className="w-4 h-4" />
                        <span className="text-sm">{item.label}</span>
                      </motion.button>
                    ))}
                  </div>
                  <div className="p-2 border-t border-neutral-200">
                    <motion.button
                      onClick={handleLogout}
                      className="flex items-center gap-3 w-full px-3 py-2 rounded-lg text-neutral-600 hover:bg-red-50 hover:text-red-600 transition-colors"
                      whileHover={{ x: 4 }}
                    >
                      <LogOut className="w-4 h-4" />
                      <span className="text-sm">Logout</span>
                    </motion.button>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
