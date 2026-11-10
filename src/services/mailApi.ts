import { api } from '../lib/api';

export interface MailConversation {
  id: string;
  type: string;
  participants: string[];
  createdAt: string;
  updatedAt: string;
  lastMessageAt: string;
}

export interface MailMessage {
  id: string;
  clientMessageId: string;
  conversationId: string;
  senderEmployeeId: string;
  receiverEmployeeId: string;
  subject?: string;
  body: string;
  status: 'SENT' | 'DELIVERED' | 'READ';
  createdAt: string;
  deliveredAt?: string;
  readAt?: string;
}

export const mailApi = {
  getConversations: async (): Promise<MailConversation[]> => {
    const res = await api.get<MailConversation[]>('/conversations');
        return res;
  },
  
  getConversationMessages: async (conversationId: string): Promise<MailMessage[]> => {
    const res = await api.get<MailMessage[]>(`/conversations/${conversationId}/messages`);
        return res;
  },
  
  sendMessage: async (data: { receiverEmployeeId: string, clientMessageId: string, body: string, subject?: string }): Promise<MailMessage> => {
    return api.post<MailMessage>('/messages', data);
  },
  
  markRead: async (conversationId: string): Promise<void> => {
    return api.patch(`/conversations/${conversationId}/read`, {});
  },
  
  getUnreadCount: async (): Promise<{ unreadCount: number }> => {
    return api.get<{ unreadCount: number }>('/unread-count');
  }
};
