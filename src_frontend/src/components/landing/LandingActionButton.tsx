import { Link } from 'react-router-dom'

interface LandingActionButtonProps {
  destination: string
  variant: 'primary' | 'secondary' | 'ghost'
  children: React.ReactNode
}

export default function LandingActionButton({ destination, variant, children }: LandingActionButtonProps) {
  const baseClassName =
    variant === 'primary'
      ? 'landing-cta-primary'
      : variant === 'secondary'
        ? 'landing-cta-secondary'
        : 'landing-cta-ghost'

  if (destination.startsWith('#')) {
    return (
      <a href={destination} className={baseClassName}>
        {children}
      </a>
    )
  }

  return (
    <Link to={destination} className={baseClassName}>
      {children}
    </Link>
  )
}
