import React, { useEffect, useState } from 'react';
import { mailApi, MailConversation, MailMessage } from '../../services/mailApi';
import { mailWs } from '../../services/mailWebSocket';
import { useAuth } from '../../context/AuthContext';
import { v4 as uuidv4 } from 'uuid';

export const ConversationView = ({ conversation }: { conversation: MailConversation | null }) => {
  const [messages, setMessages] = useState<MailMessage[]>([]);
  const [draft, setDraft] = useState('');
  const { user } = useAuth();

  useEffect(() => {
    if (!conversation) return;
    if (conversation.id.startsWith('DRAFT_')) {
      setMessages([]);
      return;
    }
    mailApi.getConversationMessages(conversation.id).then(msgs => {
            setMessages(msgs);
    });
    mailApi.markRead(conversation.id);

    const handleNew = (msg: MailMessage) => {
            if (msg.conversationId === conversation.id) {
                setMessages(prev => [...prev, msg]);
                mailApi.markRead(conversation.id);
      }
    };
    
    mailWs.on('message:new', handleNew);
    return () => mailWs.off('message:new', handleNew);
  }, [conversation]);

  const send = async () => {
    if (!draft.trim() || !conversation || !user) return;
    const receiver = conversation.participants.find(p => p !== user.employeeId);
    if (!receiver) return;

    
    const msg = await mailApi.sendMessage({
      receiverEmployeeId: receiver,
      clientMessageId: uuidv4(),
      body: draft
    });
    setMessages(prev => [...prev, msg]);
    setDraft('');
  };

  if (!conversation) return <div className="flex-1 flex items-center justify-center bg-gray-50">Select a conversation</div>;

  return (
    <div className="flex-1 flex flex-col bg-white">
      <div className="p-4 border-b font-bold flex justify-between">
        <span>Chat</span>
      </div>
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map(m => (
          <div key={m.id} className={`flex flex-col ${m.senderEmployeeId === user?.employeeId ? 'items-end' : 'items-start'}`}>
            <div className={`p-3 rounded-lg max-w-xs ${m.senderEmployeeId === user?.employeeId ? 'bg-blue-500 text-white' : 'bg-gray-100'}`}>
              {m.body}
            </div>
            <div className="text-xs text-gray-400 mt-1 flex space-x-1">
              <span>{new Date(m.createdAt).toLocaleTimeString()}</span>
              {m.senderEmployeeId === user?.employeeId && (
                <span>
                  {m.status === 'SENT' && '✓'}
                  {m.status === 'DELIVERED' && '✓✓'}
                  {m.status === 'READ' && <span className="text-blue-500">✓✓</span>}
                </span>
              )}
            </div>
          </div>
        ))}
      </div>
      <div className="p-4 border-t flex space-x-2">
        <input 
          className="flex-1 border rounded-lg p-2" 
          value={draft} 
          onChange={e => setDraft(e.target.value)} 
          onKeyDown={e => e.key === 'Enter' && send()}
          placeholder="Type a message..."
        />
        <button className="px-4 py-2 bg-blue-600 text-white rounded-lg" onClick={send}>Send</button>
      </div>
    </div>
  );
};
