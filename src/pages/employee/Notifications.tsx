import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { DashboardLayout } from '../../components/layout';
import { Bell, Check } from 'lucide-react';
import { notificationApi, Notification } from '../../services/notificationApi';
import { formatDistanceToNow } from 'date-fns';

export const Notifications = () => {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  const fetchNotifications = async () => {
    try {
      const data = await notificationApi.getNotifications(100, 0); // basic pagination for now
      setNotifications(data || []);
    } catch (error) {
      console.error('Failed to fetch notifications', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchNotifications();
  }, []);

  const handleMarkAsRead = async (id: string) => {
    try {
      await notificationApi.markAsRead(id);
      setNotifications(prev => prev.map(n => n._id === id ? { ...n, isRead: true } : n));
    } catch (error) {
      console.error('Failed to mark as read', error);
    }
  };

  const handleMarkAllAsRead = async () => {
    try {
      await notificationApi.markAllAsRead();
      await fetchNotifications();
    } catch (error) {
      console.error('Failed to mark all as read', error);
    }
  };

  const handleNotificationClick = async (notification: Notification) => {
    if (!notification.isRead) {
      await handleMarkAsRead(notification._id);
    }
    
    if (notification.type === 'MESSAGE') {
      navigate('/mail');
    } else if (notification.type === 'APPROVAL') {
      navigate('/admin/leave-approvals');
    }
  };

  return (
    <DashboardLayout title="Notifications">
      <div className="max-w-4xl mx-auto space-y-6">
        <div className="flex justify-between items-center bg-white p-4 rounded-xl border border-neutral-200 shadow-sm">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-primary-50 rounded-lg">
              <Bell className="w-5 h-5 text-primary-600" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-neutral-900">Your Notifications</h2>
              <p className="text-sm text-neutral-500">Stay updated on approvals and messages.</p>
            </div>
          </div>
          <button 
            onClick={handleMarkAllAsRead}
            className="text-sm font-medium text-primary-600 hover:text-primary-700 hover:underline px-4 py-2"
          >
            Mark all as read
          </button>
        </div>

        <div className="bg-white rounded-xl border border-neutral-200 overflow-hidden shadow-sm">
          {loading ? (
            <div className="p-8 text-center text-neutral-500">Loading notifications...</div>
          ) : notifications.length === 0 ? (
            <div className="p-12 text-center text-neutral-500">
              <Bell className="w-12 h-12 mx-auto text-neutral-300 mb-4" />
              <p>You have no notifications right now.</p>
            </div>
          ) : (
            <div className="divide-y divide-neutral-100">
              {notifications.map((notification) => (
                <div 
                  key={notification._id}
                  className={`p-4 flex gap-4 transition-colors hover:bg-neutral-50 cursor-pointer ${
                    !notification.isRead ? 'bg-primary-50/30' : ''
                  }`}
                  onClick={() => handleNotificationClick(notification)}
                >
                  <div className="mt-1">
                    {!notification.isRead ? (
                      <div className="w-2.5 h-2.5 bg-primary-500 rounded-full" />
                    ) : (
                      <div className="w-2.5 h-2.5 bg-transparent border border-neutral-300 rounded-full" />
                    )}
                  </div>
                  
                  <div className="flex-1">
                    <h4 className={`text-sm font-medium ${!notification.isRead ? 'text-neutral-900' : 'text-neutral-700'}`}>
                      {notification.title}
                    </h4>
                    <p className="text-sm text-neutral-600 mt-1">{notification.message}</p>
                    <p className="text-xs text-neutral-400 mt-2">
                      {formatDistanceToNow(new Date(notification.createdAt), { addSuffix: true })}
                    </p>
                  </div>
                  
                  {!notification.isRead && (
                    <button 
                      onClick={(e) => {
                        e.stopPropagation();
                        handleMarkAsRead(notification._id);
                      }}
                      className="p-2 text-neutral-400 hover:text-primary-600 hover:bg-primary-50 rounded-lg transition-colors self-start"
                      title="Mark as read"
                    >
                      <Check className="w-4 h-4" />
                    </button>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </DashboardLayout>
  );
};

export default Notifications;
