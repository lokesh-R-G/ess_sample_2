import React, { useState } from 'react';
import { InboxList } from './InboxList';
import { ConversationView } from './ConversationView';
import { MailConversation } from '../../services/mailApi';
import { DashboardLayout } from '../../components/layout/DashboardLayout';

export const MailboxLayout = () => {
  const [selected, setSelected] = useState<MailConversation | null>(null);

  return (
    <DashboardLayout>
      <div className="flex h-[calc(100vh-80px)] bg-gray-100 p-6">
        <div className="flex flex-1 rounded-2xl overflow-hidden shadow-xl border">
          <InboxList onSelect={setSelected} />
          <ConversationView conversation={selected} />
        </div>
      </div>
    </DashboardLayout>
  );
};
