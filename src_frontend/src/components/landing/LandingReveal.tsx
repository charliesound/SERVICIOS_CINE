import { useEffect, useRef, useState } from 'react'
import clsx from 'clsx'

interface LandingRevealProps {
  children: React.ReactNode
  className?: string
  delay?: number
}

export default function LandingReveal({ children, className, delay = 0 }: LandingRevealProps) {
  const ref = useRef<HTMLDivElement | null>(null)
  const [isVisible, setIsVisible] = useState(false)

  useEffect(() => {
    const node = ref.current
    if (!node) return

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true)
          observer.unobserve(entry.target)
        }
      },
      { threshold: 0.16, rootMargin: '0px 0px -10% 0px' }
    )

    observer.observe(node)

    return () => observer.disconnect()
  }, [])

  return (
    <div
      ref={ref}
      className={clsx('landing-reveal', isVisible && 'landing-reveal-visible', className)}
      style={{ transitionDelay: `${delay}ms` }}
    >
      {children}
    </div>
  )
}
