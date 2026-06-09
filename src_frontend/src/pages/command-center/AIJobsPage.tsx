import { t } from '@/i18n'
import { ServerCog } from 'lucide-react'
import CreditOverview from '@/components/command-center/CreditOverview'
import JobHistoryTable from '@/components/command-center/JobHistoryTable'

export default function AIJobsPage() {
  // Mock credit data
  const mockCredits = {
    total: 1000,
    available: 780,
    reserved: 135,
    consumed: 85
  }

  return (
    <div className="space-y-8 max-w-7xl mx-auto pb-12">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="heading-xl flex items-center gap-3">
            <ServerCog className="w-8 h-8 text-indigo-400" />
            {t('internal.commandCenter.aiJobs.title')}
          </h1>
          <p className="text-slate-400 mt-2 text-lg">{t('internal.commandCenter.aiJobs.subtitle')}</p>
        </div>
      </div>

      {/* Credit Overview */}
      <section>
        <CreditOverview {...mockCredits} />
      </section>

      {/* Job History Table */}
      <section className="space-y-4">
        <JobHistoryTable />
      </section>
    </div>
  )
}
