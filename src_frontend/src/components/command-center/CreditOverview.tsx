import { t } from '@/i18n'
import { Coins, PiggyBank, Receipt, Wallet } from 'lucide-react'

interface CreditOverviewProps {
  total: number
  available: number
  reserved: number
  consumed: number
}

export default function CreditOverview({ total, available, reserved, consumed }: CreditOverviewProps) {
  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div className="stat-card group">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-indigo-500/10 flex items-center justify-center">
            <Wallet className="w-5 h-5 text-indigo-400" />
          </div>
          <div>
            <p className="text-2xl font-bold text-white">{total}</p>
            <p className="text-sm text-slate-400">{t('internal.commandCenter.aiJobs.credits.total')}</p>
          </div>
        </div>
      </div>

      <div className="stat-card group">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-green-500/10 flex items-center justify-center">
            <Coins className="w-5 h-5 text-green-400" />
          </div>
          <div>
            <p className="text-2xl font-bold text-white">{available}</p>
            <p className="text-sm text-slate-400">{t('internal.commandCenter.aiJobs.credits.available')}</p>
          </div>
        </div>
      </div>

      <div className="stat-card group">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-amber-500/10 flex items-center justify-center">
            <PiggyBank className="w-5 h-5 text-amber-400" />
          </div>
          <div>
            <p className="text-2xl font-bold text-white">{reserved}</p>
            <p className="text-sm text-slate-400">{t('internal.commandCenter.aiJobs.credits.reserved')}</p>
          </div>
        </div>
      </div>

      <div className="stat-card group">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-blue-500/10 flex items-center justify-center">
            <Receipt className="w-5 h-5 text-blue-400" />
          </div>
          <div>
            <p className="text-2xl font-bold text-white">{consumed}</p>
            <p className="text-sm text-slate-400">{t('internal.commandCenter.aiJobs.credits.consumed')}</p>
          </div>
        </div>
      </div>
    </div>
  )
}
