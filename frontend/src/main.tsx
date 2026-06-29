import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import App from './App'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <BrowserRouter>
      <App />
      <Toaster
        position="bottom-right"
        toastOptions={{
          className: 'bg-space-800 text-white border border-space-600',
          duration: 4000,
          style: {
            background: '#12121a',
            color: '#fff',
            border: '1px solid #2a2a38',
          },
        }}
      />
    </BrowserRouter>
  </React.StrictMode>
)
