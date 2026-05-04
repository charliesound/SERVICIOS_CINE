import { useLayoutEffect } from 'react'
import { Routes, Route, useLocation } from 'react-router-dom'
import PublicRoute from './components/PublicRoute'
import CIDRoute from './components/CIDRoute'
import PlanRoute from './components/PlanRoute'
import AppShell from './components/AppShell'
import LandingPage from './pages/LandingPage'
import LoginPage from './pages/LoginPage'
import RegisterSelectPage from './pages/RegisterSelectPage'
import RegisterCIDPage from './pages/RegisterCIDPage'
import RegisterDemoPage from './pages/RegisterDemoPage'
import RegisterPartnerPage from './pages/RegisterPartnerPage'
import LegalPrivacyPage from './pages/legal/LegalPrivacyPage'
import LegalNoticePage from './pages/legal/LegalNoticePage'
import LegalTermsPage from './pages/legal/LegalTermsPage'
import LegalAiContentPage from './pages/legal/LegalAiContentPage'
import OnboardingPage from './pages/OnboardingPage'
import PendingAccessPage from './pages/PendingAccessPage'
import Dashboard from './pages/Dashboard'
import CreateJob from './pages/CreateJob'
import QueuePage from './pages/QueuePage'
import WorkflowsPage from './pages/WorkflowsPage'
import PlansPage from './pages/PlansPage'
import AdminPage from './pages/AdminPage'
import ProjectHistory from './pages/ProjectHistory'
import ClientPortal from './pages/ClientPortal'
import IngestScansPage from './pages/IngestScansPage'
import IngestScanDetailPage from './pages/IngestScanDetailPage'
import MediaAssetsPage from './pages/MediaAssetsPage'
import MediaAssetDetailPage from './pages/MediaAssetDetailPage'
import DocumentsPage from './pages/DocumentsPage'
import DocumentDetailPage from './pages/DocumentDetailPage'
import ReportsPage from './pages/ReportsPage'
import ReportDetailPage from './pages/ReportDetailPage'
import StorageSourcesPage from './pages/StorageSourcesPage'
import StorageSourceDetailPage from './pages/StorageSourceDetailPage'
import ProjectsPage from './pages/ProjectsPage'
import NewProjectPage from './pages/NewProjectPage'
import ProjectDetailPage from './pages/ProjectDetailPage'
import StoryboardBuilderPage from './pages/StoryboardBuilderPage'
import ProjectFundingPage from './pages/ProjectFundingPage'
import EditorialAssemblyPage from './pages/EditorialAssemblyPage'
import ProjectDashboardPage from './pages/ProjectDashboardPage'
import ProjectMembersPage from './pages/ProjectMembersPage'
import BudgetEstimatorPage from './pages/BudgetEstimatorPage'
import ChangeRequestsPage from './pages/ChangeRequestsPage'
import ProducerPitchPackPage from './pages/ProducerPitchPackPage'
import DistributionPackPage from './pages/DistributionPackPage'
import CommercialCrmPage from './pages/CommercialCrmPage'
import DeliveryOverviewPage from './pages/DeliveryOverviewPage'
import DeliverableDetailPage from './pages/DeliverableDetailPage'
import ReviewsOverviewPage from './pages/ReviewsOverviewPage'
import ReviewDetailPage from './pages/ReviewDetailPage'
import CIDPipelineBuilderPage from './pages/CIDPipelineBuilderPage'
import SolutionsPage from './pages/SolutionsPage'
import CIDProductPage from './pages/CIDProductPage'
import SolutionDetailPage from './pages/SolutionDetailPage'
import PricingPage from './pages/PricingPage'
import { applySeo, SEO_DEFAULT_DESCRIPTION, SEO_DEFAULT_TITLE } from '@/utils/seo'

function RouteSeoDefaults() {
  const location = useLocation()

  useLayoutEffect(() => {
    applySeo({
      title: SEO_DEFAULT_TITLE,
      description: SEO_DEFAULT_DESCRIPTION,
      path: `${location.pathname}${location.search}`,
      robots: 'noindex, nofollow',
    })
  }, [location.pathname, location.search])

  return null
}

export default function App() {
  return (
    <>
      <RouteSeoDefaults />
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/solutions" element={<SolutionsPage />} />
        <Route path="/solutions/cid" element={<CIDProductPage />} />
        <Route path="/solutions/script-breakdown" element={<SolutionDetailPage />} />
        <Route path="/solutions/storyboard" element={<SolutionDetailPage />} />
        <Route path="/solutions/production-planner" element={<SolutionDetailPage />} />
        <Route path="/solutions/dubbing" element={<SolutionDetailPage />} />
        <Route path="/solutions/sound-post" element={<SolutionDetailPage />} />
        <Route path="/solutions/promo-video" element={<SolutionDetailPage />} />
        <Route path="/solutions/vfx" element={<SolutionDetailPage />} />
        <Route path="/pricing" element={<PricingPage />} />
        <Route path="/legal/privacidad" element={<LegalPrivacyPage />} />
        <Route path="/legal/aviso-legal" element={<LegalNoticePage />} />
        <Route path="/legal/terminos" element={<LegalTermsPage />} />
        <Route path="/legal/ia-y-contenidos" element={<LegalAiContentPage />} />

        <Route element={<PublicRoute />}>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register/select" element={<RegisterSelectPage />} />
          <Route path="/register/cid" element={<RegisterCIDPage />} />
          <Route path="/register/demo" element={<RegisterDemoPage />} />
          <Route path="/register/partner" element={<RegisterPartnerPage />} />
        </Route>

        <Route path="/onboarding" element={<OnboardingPage />} />
        <Route path="/pending-access" element={<PendingAccessPage />} />
        <Route path="/project/:jobId" element={<ClientPortal />} />

         <Route element={<CIDRoute><AppShell /></CIDRoute>}>
           <Route
             path="/cid"
             element={
               <CIDRoute>
                 <Dashboard />
               </CIDRoute>
             }
           />
           <Route
             path="/cid/demo"
             element={
               <PlanRoute program="demo">
                 <Dashboard />
               </PlanRoute>
             }
           />
           <Route
             path="/cid/creator"
             element={
               <PlanRoute program="creator">
                 <Dashboard />
               </PlanRoute>
             }
           />
           <Route
             path="/cid/producer"
             element={
               <PlanRoute program="producer">
                 <Dashboard />
               </PlanRoute>
             }
           />
           <Route
             path="/cid/studio"
             element={
               <PlanRoute program="studio">
                 <Dashboard />
               </PlanRoute>
             }
           />
           <Route
             path="/cid/enterprise"
             element={
               <PlanRoute program="enterprise">
                 <Dashboard />
               </PlanRoute>
             }
           />
           <Route path="/dashboard" element={<Dashboard />} />
           <Route path="/projects" element={<ProjectsPage />} />
           <Route path="/projects/new" element={<NewProjectPage />} />
           <Route path="/projects/:projectId" element={<ProjectDetailPage />} />
           <Route path="/projects/:projectId/dashboard" element={<ProjectDashboardPage />} />
           <Route path="/projects/:projectId/members" element={<ProjectMembersPage />} />
           <Route path="/projects/:projectId/budget" element={<BudgetEstimatorPage />} />
           <Route path="/projects/:projectId/change-requests" element={<ChangeRequestsPage />} />
           <Route path="/projects/:projectId/producer-pitch" element={<ProducerPitchPackPage />} />
           <Route path="/projects/:projectId/distribution" element={<DistributionPackPage />} />
           <Route path="/projects/:projectId/crm" element={<CommercialCrmPage />} />
           <Route path="/projects/:projectId/storyboard-builder" element={<StoryboardBuilderPage />} />
           <Route path="/projects/:projectId/editorial" element={<EditorialAssemblyPage />} />
           <Route path="/projects/:projectId/funding" element={<ProjectFundingPage />} />
           <Route path="/projects/:projectId/reviews" element={<ReviewsOverviewPage />} />
           <Route path="/projects/:projectId/reviews/:reviewId" element={<ReviewDetailPage />} />
           <Route path="/projects/:projectId/delivery" element={<DeliveryOverviewPage />} />
           <Route path="/projects/:projectId/delivery/:deliverableId" element={<DeliverableDetailPage />} />
           <Route path="/create" element={<CreateJob />} />
            <Route path="/queue" element={<QueuePage />} />
            <Route path="/history" element={<ProjectHistory />} />
            <Route path="/workflows" element={<WorkflowsPage />} />
            <Route path="/cid/pipeline-builder" element={<CIDPipelineBuilderPage />} />
            <Route path="/plans" element={<PlansPage />} />
           <Route path="/admin" element={<AdminPage />} />
           <Route path="/storage-sources" element={<StorageSourcesPage />} />
           <Route path="/storage-sources/:sourceId" element={<StorageSourceDetailPage />} />
           <Route path="/ingest/scans" element={<IngestScansPage />} />
           <Route path="/ingest/scans/:scanId" element={<IngestScanDetailPage />} />
           <Route path="/ingest/assets" element={<MediaAssetsPage />} />
           <Route path="/ingest/assets/:assetId" element={<MediaAssetDetailPage />} />
           <Route path="/documents" element={<DocumentsPage />} />
           <Route path="/documents/:documentId" element={<DocumentDetailPage />} />
           <Route path="/reports/:reportType" element={<ReportsPage />} />
           <Route path="/reports/:reportType/:reportId" element={<ReportDetailPage />} />
         </Route>
      </Routes>
    </>
  )
}
