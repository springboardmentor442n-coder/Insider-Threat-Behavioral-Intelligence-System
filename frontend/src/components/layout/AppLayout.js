import React, { useEffect } from 'react';
import Sidebar from './Sidebar';
import Topbar from './Topbar';
import ChatbotPanel from '../common/ChatbotPanel';
import { useLiveStore } from '../../utils/store';

export default function AppLayout({ children, title, subtitle }) {
  const connectWebSocket = useLiveStore(state => state.connectWebSocket);

  useEffect(() => {
    connectWebSocket();
    return () => {};
  }, [connectWebSocket]);

  return (
    <div style={{ display: 'flex', minHeight: '100vh' }}>
      <Sidebar />
      <div style={{
        marginLeft: 'var(--sidebar-w)',
        flex: 1,
        display: 'flex',
        flexDirection: 'column',
        minHeight: '100vh',
        position: 'relative',
        zIndex: 1,
      }}>
        <Topbar title={title} subtitle={subtitle} />
        <main style={{
          flex: 1,
          padding: '24px',
          paddingTop: 'calc(var(--topbar-h) + 24px)',
          overflowY: 'auto',
        }}>
          {children}
        </main>
      </div>
      
      {/* Floating security chatbot assistant */}
      <ChatbotPanel />
    </div>
  );
}
