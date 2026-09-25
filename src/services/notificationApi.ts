import { api } from '../lib/api';

export interface Notification {
  _id: string;
  recipientEmployeeId: string;
  type: string;
  event: string;
  title: string;
  message: string;
  entityType?: string;
  entityId?: string;
  actorEmployeeId?: string;
  isRead: boolean;
  readAt?: string;
  createdAt: string;
}

export interface UnreadCountResponse {
  unreadCount: number;
}

export const notificationApi = {
  getNotifications: async (limit: number = 20, skip: number = 0): Promise<Notification[]> => {
    return await api.get<Notification[]>(`/v2/notification?limit=${limit}&skip=${skip}`);
  },

  getUnreadCount: async (): Promise<UnreadCountResponse> => {
    return await api.get<UnreadCountResponse>('/v2/notification/unread-count');
  },

  markAsRead: async (id: string): Promise<void> => {
    await api.patch(`/v2/notification/${id}/read`);
  },

  markAllAsRead: async (): Promise<void> => {
    await api.patch('/v2/notification/read-all');
  }
};
