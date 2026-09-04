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
    return api.get<MailConversation[]>('/v2/mail/conversations');
  },
  
  getConversationMessages: async (conversationId: string): Promise<MailMessage[]> => {
    return api.get<MailMessage[]>(`/v2/mail/conversations/${conversationId}/messages`);
  },
  
  sendMessage: async (data: { receiverEmployeeId: string, clientMessageId: string, body: string, subject?: string }): Promise<MailMessage> => {
    return api.post<MailMessage>('/v2/mail/messages', data);
  },
  
  markRead: async (conversationId: string): Promise<void> => {
    return api.patch(`/v2/mail/conversations/${conversationId}/read`, {});
  },
  
  getUnreadCount: async (): Promise<{ unreadCount: number }> => {
    return api.get<{ unreadCount: number }>('/v2/mail/unread-count');
  }
};
