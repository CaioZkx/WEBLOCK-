import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './context/AuthContext'
import LoginPage from './pages/LoginPage'
import DashboardPage from './pages/DashboardPage'
import Layout from './components/layout/Layout'

function ProtectedRoute({ children }) {
  const { user, loading } = useAuth()
  if (loading) return <div style={{display:'flex',alignItems:'center',justifyContent:'center',height:'100vh',fontFamily:'Inter',color:'#64748b'}}>Carregando...</div>
  if (!user) return <Navigate to="/login" replace />
  return <Layout>{children}</Layout>
}

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/dashboard" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
          <Route path="/logs"      element={<ProtectedRoute><LogsPage /></ProtectedRoute>} />
          <Route path="/users"     element={<ProtectedRoute><UsersPage /></ProtectedRoute>} />
          <Route path="/locations" element={<ProtectedRoute><LocationsPage /></ProtectedRoute>} />
          <Route path="/simulate"  element={<ProtectedRoute><SimulatePage /></ProtectedRoute>} />
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  </React.StrictMode>
)

// Lazy inline pages to keep bundle simple
function LogsPage()      { const L = React.lazy(() => import('./pages/LogsPage'));      return <React.Suspense fallback={<p>...</p>}><L /></React.Suspense> }
function UsersPage()     { const L = React.lazy(() => import('./pages/UsersPage'));     return <React.Suspense fallback={<p>...</p>}><L /></React.Suspense> }
function LocationsPage() { const L = React.lazy(() => import('./pages/LocationsPage')); return <React.Suspense fallback={<p>...</p>}><L /></React.Suspense> }
function SimulatePage()  { const L = React.lazy(() => import('./pages/SimulatePage'));  return <React.Suspense fallback={<p>...</p>}><L /></React.Suspense> }
