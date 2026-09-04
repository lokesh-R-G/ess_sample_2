import { getAuthToken } from '../lib/api';

type EventCallback = (payload: any) => void;

class MailWebSocket {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private listeners: Map<string, EventCallback[]> = new Map();
  private baseWsUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8000';

  connect() {
    if (this.ws?.readyState === WebSocket.OPEN) return;
    
    const token = getAuthToken();
    if (!token) return;

    this.ws = new WebSocket(`${this.baseWsUrl}/api/v2/mail/ws?token=${token}`);

    this.ws.onopen = () => {
      console.log('Mailbox WS Connected');
      this.reconnectAttempts = 0;
    };

    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type) {
          const cbs = this.listeners.get(data.type) || [];
          cbs.forEach(cb => cb(data.payload));
          
          // Auto-ACK new messages
          if (data.type === 'message:new') {
            this.send('message:ack', { messageIds: [data.payload.id] });
          }
        }
      } catch (e) {
        console.error('WS Parse Error', e);
      }
    };

    this.ws.onclose = () => {
      console.log('Mailbox WS Disconnected');
      this.attemptReconnect();
    };
  }

  private attemptReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      setTimeout(() => {
        this.reconnectAttempts++;
        this.connect();
      }, Math.min(1000 * Math.pow(2, this.reconnectAttempts), 10000));
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  on(event: string, callback: EventCallback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event)!.push(callback);
  }

  off(event: string, callback: EventCallback) {
    if (!this.listeners.has(event)) return;
    const cbs = this.listeners.get(event)!.filter(cb => cb !== callback);
    this.listeners.set(event, cbs);
  }

  send(type: string, payload: any) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ type, ...payload }));
    }
  }
}

export const mailWs = new MailWebSocket();
