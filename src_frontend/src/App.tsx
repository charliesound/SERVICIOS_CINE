import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import CreateJob from './pages/CreateJob'
import QueuePage from './pages/QueuePage'
import WorkflowsPage from './pages/WorkflowsPage'
import PlansPage from './pages/PlansPage'
import AdminPage from './pages/AdminPage'
import LoginPage from './pages/LoginPage'
import ProjectHistory from './pages/ProjectHistory'
import ClientPortal from './pages/ClientPortal'

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      
      {/* Public portal for clients */}
      <Route path="/project/:jobId" element={<ClientPortal />} />
      
      <Route path="/" element={<Layout />}>
        <Route index element={<Dashboard />} />
        <Route path="create" element={<CreateJob />} />
        <Route path="queue" element={<QueuePage />} />
        <Route path="history" element={<ProjectHistory />} />
        <Route path="workflows" element={<WorkflowsPage />} />
        <Route path="plans" element={<PlansPage />} />
        <Route path="admin" element={<AdminPage />} />
      </Route>
    </Routes>
  )
}