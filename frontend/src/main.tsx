import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import './index.css';
import App from './App.tsx';
import { ToastProvider } from './components/ToastProvider.tsx';

// ToastProvider wraps everything so any component in the tree can call
// useToast() to fire a notification. It renders the toast UI itself at
// the bottom of the screen, outside of any scrollable content.
createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter>
      <ToastProvider>
        <App />
      </ToastProvider>
    </BrowserRouter>
  </StrictMode>,
);
