import type { UserProfile } from '@/types'
import { canAccessCID, needsOnboarding } from '@/store'

export type PostLoginTarget = '/' | '/cid' | '/dashboard' | '/onboarding' | '/pending-access'

export function resolvePostLoginRoute(user: UserProfile | null): PostLoginTarget {
  if (!user) return '/'

  if (canAccessCID(user)) {
    if (needsOnboarding(user)) {
      return '/onboarding'
    }
    return '/cid'
  }

  if (user.signup_type === 'demo_request') {
    return '/dashboard'
  }

  if (user.signup_type === 'partner_interest') {
    return '/dashboard'
  }

  if (user.account_status === 'pending' || user.account_status === undefined) {
    return '/pending-access'
  }

  return '/dashboard'
}
