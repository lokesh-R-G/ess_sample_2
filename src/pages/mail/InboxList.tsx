import React, { useEffect, useState } from 'react';
import { mailApi, MailConversation } from '../../services/mailApi';
import { mailWs } from '../../services/mailWebSocket';
import { employeeApi } from '../../services/employeeApi';
import { useAuth } from '../../context/AuthContext';

export const InboxList = ({ onSelect }: { onSelect: (c: MailConversation) => void }) => {
  const [conversations, setConversations] = useState<MailConversation[]>([]);
  const [employees, setEmployees] = useState<any[]>([]);
  const [showNew, setShowNew] = useState(false);
  const [selectedEmp, setSelectedEmp] = useState('');
  const { user } = useAuth();

  useEffect(() => {
    mailApi.getConversations().then(setConversations);
    mailWs.connect();

    const handleNewMessage = (msg: any) => {
      mailApi.getConversations().then(setConversations);
    };
    mailWs.on('message:new', handleNewMessage);
    
    return () => {
      mailWs.off('message:new', handleNewMessage);
    };
  }, []);

  const handleCreateNew = async () => {
    if (!selectedEmp) return;
    // selectedEmp now holds the canonical employeeId
    const newConv: MailConversation = {
      id: 'DRAFT_' + selectedEmp,
      type: 'DIRECT',
      participants: [user?.employeeId || '', selectedEmp],
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      lastMessageAt: new Date().toISOString()
    };
    onSelect(newConv);
    setShowNew(false);
  };

  return (
    <div className="w-1/3 border-r bg-white flex flex-col">
      <div className="p-4 border-b font-bold text-lg flex justify-between items-center">
        <span>Inbox</span>
        <button className="text-sm bg-primary-500 text-white px-3 py-1 rounded" onClick={() => {
          setShowNew(!showNew);
          if (!employees.length) {
            employeeApi.getAllDirectoryEmployees().then(setEmployees);
          }
        }}>
          + New
        </button>
      </div>
      
      {showNew && (
        <div className="p-4 border-b bg-gray-50 flex gap-2">
          <select 
            className="flex-1 border p-1 rounded" 
            value={selectedEmp} 
            onChange={e => setSelectedEmp(e.target.value)}
          >
            <option value="">Select Employee...</option>
            {employees.map(e => (
              <option key={e.employeeId || e.id || e.empId} value={e.employeeId || e.id}>{e.name || `${e.firstName} ${e.lastName}`} ({e.employeeCode || e.empId})</option>
            ))}
          </select>
          <button className="bg-blue-500 text-white px-3 rounded" onClick={handleCreateNew}>Chat</button>
        </div>
      )}

      <div className="flex-1 overflow-y-auto">
        {conversations.map(c => {
          const other = c.participants.find(p => p !== user?.employeeId) || 'Unknown';
          return (
            <div key={c.id} onClick={() => onSelect(c)} className="p-4 border-b cursor-pointer hover:bg-gray-50">
              <div className="font-semibold">{other}</div>
              <div className="text-xs text-gray-500">{new Date(c.lastMessageAt).toLocaleString()}</div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

