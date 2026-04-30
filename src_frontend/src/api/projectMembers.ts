import api from './client'

export interface ProjectMember {
  id: string
  user_id: string
  professional_role: string
  can_manage_permissions: boolean
  can_manage_members: boolean
  status: string
  invited_by_user_id: string | null
  created_at: string
  user?: {
    user_id: string | null
    email: string | null
    name: string | null
  }
}

export interface MemberInfo {
  member: ProjectMember
  permissions: string[]
  can_manage_members: boolean
  can_delegate: boolean
  is_owner: boolean
}

export interface AddMemberPayload {
  user_id: string
  professional_role?: string
  can_manage_permissions?: boolean
  can_manage_members?: boolean
}

export interface UpdateMemberPayload {
  professional_role?: string
  can_manage_permissions?: boolean
  can_manage_members?: boolean
}

export const projectMembersApi = {
  list: async (projectId: string): Promise<{ members: ProjectMember[] }> => {
    const { data } = await api.get<{ members: ProjectMember[] }>(
      `/projects/${projectId}/members`
    )
    return data
  },

  getMyMemberInfo: async (projectId: string): Promise<MemberInfo> => {
    const { data } = await api.get<MemberInfo>(
      `/projects/${projectId}/members/me`
    )
    return data
  },

  listRoles: async (): Promise<{ roles: string[] }> => {
    const { data } = await api.get<{ roles: string[] }>(
      '/projects/default/members/roles'
    )
    return data
  },

  add: async (
    projectId: string,
    payload: AddMemberPayload
  ): Promise<{ member: ProjectMember }> => {
    const { data } = await api.post<{ member: ProjectMember }>(
      `/projects/${projectId}/members`,
      payload
    )
    return data
  },

  remove: async (projectId: string, userId: string): Promise<{ success: boolean }> => {
    const { data } = await api.delete<{ success: boolean }>(
      `/projects/${projectId}/members/${userId}`
    )
    return data
  },

  update: async (
    projectId: string,
    userId: string,
    payload: UpdateMemberPayload
  ): Promise<{ member: ProjectMember }> => {
    const { data } = await api.patch<{ member: ProjectMember }>(
      `/projects/${projectId}/members/${userId}`,
      payload
    )
    return data
  },

  delegatePermissions: async (
    projectId: string,
    targetUserId: string,
    canManagePermissions: boolean
  ): Promise<{
    success: boolean
    member_id: string
    can_manage_permissions: boolean
  }> => {
    const { data } = await api.post(
      `/projects/${projectId}/members/delegate`,
      { target_user_id: targetUserId, can_manage_permissions: canManagePermissions }
    )
    return data
  },

  getMemberPermissions: async (
    projectId: string,
    userId: string
  ): Promise<{ user_id: string; permissions: string[] }> => {
    const { data } = await api.get<{ user_id: string; permissions: string[] }>(
      `/projects/${projectId}/members/${userId}/permissions`
    )
    return data
  },
}