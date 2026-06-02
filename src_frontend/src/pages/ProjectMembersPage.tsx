import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { Users, UserPlus, Shield, X } from 'lucide-react'
import { projectMembersApi } from '@/api/projectMembers'
import type { ProjectMember } from '@/api/projectMembers'
import { t } from '@/i18n'

const ROLE_LABELS: Record<string, string> = {
  owner: 'internal.projectMembers.roles.owner',
  producer: 'internal.projectMembers.roles.producer',
  executive_producer: 'internal.projectMembers.roles.executiveProducer',
  production_manager: 'internal.projectMembers.roles.productionManager',
  director: 'internal.projectMembers.roles.director',
  editor: 'internal.projectMembers.roles.editor',
  sound: 'internal.projectMembers.roles.sound',
  dop: 'internal.projectMembers.roles.dop',
  script_supervisor: 'internal.projectMembers.roles.scriptSupervisor',
  viewer: 'internal.projectMembers.roles.viewer',
}

function RoleBadge({ role }: { role: string }) {
  const labels: Record<string, string> = {
    owner: 'bg-red-500/20 text-red-400 border-red-500/30',
    producer: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
    executive_producer: 'bg-orange-500/20 text-orange-400 border-orange-500/30',
    production_manager: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
    director: 'bg-purple-500/20 text-purple-400 border-purple-500/30',
    editor: 'bg-green-500/20 text-green-400 border-green-500/30',
    viewer: 'bg-gray-500/20 text-gray-400 border-gray-500/30',
  }
  const bg = labels[role] || labels.viewer
  return (
    <span className={`px-2 py-0.5 text-xs font-medium rounded-full border ${bg}`}>
      {ROLE_LABELS[role] ? t(ROLE_LABELS[role]) : role}
    </span>
  )
}

export default function ProjectMembersPage() {
  const { projectId = '' } = useParams()
  const [members, setMembers] = useState<ProjectMember[]>([])
  const [myInfo, setMyInfo] = useState<{ can_manage_members: boolean; can_delegate: boolean; is_owner: boolean } | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showAddModal, setShowAddModal] = useState(false)
  const [selectedRole, setSelectedRole] = useState('viewer')

  useEffect(() => {
    loadData()
  }, [projectId])

  async function loadData() {
    try {
      setIsLoading(true)
      const [membersRes, myInfoRes] = await Promise.all([
        projectMembersApi.list(projectId),
        projectMembersApi.getMyMemberInfo(projectId),
      ])
      setMembers(membersRes.members)
      setMyInfo({
        can_manage_members: myInfoRes.can_manage_members,
        can_delegate: myInfoRes.can_delegate,
        is_owner: myInfoRes.is_owner,
      })
    } catch (e) {
      setError(t('internal.projectMembers.errorLoading'))
    } finally {
      setIsLoading(false)
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-12">
        <div className="animate-spin w-8 h-8 border-2 border-amber-500 border-t-transparent rounded-full" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="card">
        <div className="text-red-400">{error}</div>
        <Link to={`/projects/${projectId}/dashboard`} className="btn-secondary mt-4">
          {t('internal.projectMembers.backToDashboard')}
        </Link>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="heading-lg">{t('internal.projectMembers.title')}</h1>
          </div>
          <p className="mt-1 text-slate-400">
            {members.length} miembro{members.length !== 1 ? 's' : ''}
          </p>
        </div>

        <div className="flex gap-3">
          <Link to={`/projects/${projectId}/dashboard`} className="btn-secondary">
            {t('internal.projectMembers.backToDashboard')}
          </Link>
          {myInfo?.can_manage_members && (
            <button
              onClick={() => setShowAddModal(true)}
              className="btn-primary flex items-center gap-2"
            >
              <UserPlus className="w-4 h-4" />
              {t('internal.projectMembers.addMember')}
            </button>
          )}
        </div>
      </div>

      {myInfo?.can_delegate && !myInfo?.is_owner && (
        <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/30">
          <div className="flex items-center gap-2 text-amber-400">
            <Shield className="w-5 h-5" />
            <span className="font-medium">{t('internal.projectMembers.delegatedPermissions')}</span>
          </div>
          <p className="mt-1 text-sm text-slate-400">
            Puedes gestionar permisos de otros miembros.
          </p>
        </div>
      )}

      <div className="card overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="border-b border-white/10">
              <th className="text-left py-3 px-4 text-sm font-medium text-slate-400">{t('internal.projectMembers.table.user')}</th>
              <th className="text-left py-3 px-4 text-sm font-medium text-slate-400">{t('internal.projectMembers.table.role')}</th>
              <th className="text-left py-3 px-4 text-sm font-medium text-slate-400">{t('internal.projectMembers.table.permissions')}</th>
              <th className="text-left py-3 px-4 text-sm font-medium text-slate-400">{t('internal.projectMembers.table.status')}</th>
              {myInfo?.can_manage_members && (
                <th className="text-right py-3 px-4 text-sm font-medium text-slate-400">{t('internal.projectMembers.table.actions')}</th>
              )}
            </tr>
          </thead>
          <tbody>
            {members.map((member) => (
              <tr key={member.id} className="border-b border-white/5 hover:bg-white/5">
                <td className="py-3 px-4">
                  <div>
                    <div className="font-medium">{member.user?.name || t('internal.projectMembers.fallbackUser')}</div>
                    <div className="text-sm text-slate-500">{member.user?.email || member.user_id}</div>
                  </div>
                </td>
                <td className="py-3 px-4">
                  <RoleBadge role={member.professional_role} />
                </td>
                <td className="py-3 px-4">
                  <div className="flex gap-2">
                    {member.can_manage_permissions && (
                      <span className="badge badge-blue">{t('internal.projectMembers.permissions.manage')}</span>
                    )}
                    {member.can_manage_members && (
                      <span className="badge badge-purple">{t('internal.projectMembers.permissions.members')}</span>
                    )}
                    {!member.can_manage_permissions && !member.can_manage_members && (
                      <span className="text-sm text-slate-500">{t('internal.projectMembers.permissions.basic')}</span>
                    )}
                  </div>
                </td>
                <td className="py-3 px-4">
                  <span className={`px-2 py-0.5 text-xs rounded-full ${
                    member.status === 'active'
                      ? 'bg-green-500/20 text-green-400'
                      : 'bg-gray-500/20 text-gray-400'
                  }`}>
                    {member.status === 'active' ? 'Activo' : member.status}
                  </span>
                </td>
                {myInfo?.can_manage_members && (
                  <td className="py-3 px-4 text-right">
                    {!member.can_manage_members && member.professional_role !== 'owner' && (
                      <button className="text-sm text-red-400 hover:text-red-300">
                        Remover
                      </button>
                    )}
                  </td>
                )}
              </tr>
            ))}
          </tbody>
        </table>

        {members.length === 0 && (
          <div className="p-8 text-center text-slate-500">
            <Users className="w-12 h-12 mx-auto mb-3 opacity-50" />
            <p>{t('internal.projectMembers.noMembers')}</p>
          </div>
        )}
      </div>

      {showAddModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="card w-full max-w-md space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="heading-md">{t('internal.projectMembers.addMemberTitle')}</h2>
              <button onClick={() => setShowAddModal(false)} className="text-slate-400 hover:text-white">
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-2">
              <label className="text-sm text-slate-400">{t('internal.projectMembers.selectUser')}</label>
              <input
                type="text"
                placeholder={t('internal.projectMembers.searchUserPlaceholder')}
                className="input w-full"
              />
            </div>

            <div className="space-y-2">
              <label className="text-sm text-slate-400">{t('internal.projectMembers.role')}</label>
              <select
                value={selectedRole}
                onChange={(e) => setSelectedRole(e.target.value)}
                className="input w-full"
              >
                <option value="viewer">{t('internal.projectMembers.roles.viewer')}</option>
                <option value="producer">{t('internal.projectMembers.roles.producer')}</option>
                <option value="director">{t('internal.projectMembers.roles.director')}</option>
                <option value="editor">{t('internal.projectMembers.roles.editor')}</option>
                <option value="production_manager">{t('internal.projectMembers.roles.productionManager')}</option>
              </select>
            </div>

            <div className="flex justify-end gap-3 pt-4">
              <button onClick={() => setShowAddModal(false)} className="btn-secondary">
                {t('internal.common.cancel')}
              </button>
              <button className="btn-primary">
                {t('internal.projectMembers.add')}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}