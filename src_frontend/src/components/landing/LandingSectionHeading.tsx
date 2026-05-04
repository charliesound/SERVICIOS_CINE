import clsx from 'clsx'

interface LandingSectionHeadingProps {
  eyebrow: string
  title: string
  description: string
  align?: 'left' | 'center'
}

export default function LandingSectionHeading({
  eyebrow,
  title,
  description,
  align = 'left',
}: LandingSectionHeadingProps) {
  return (
    <div className={clsx(align === 'center' ? 'mx-auto max-w-3xl text-center' : 'max-w-2xl')}>
      <p className="editorial-kicker text-amber-300/90">{eyebrow}</p>
      <h2 className="mt-4 font-display text-4xl font-semibold leading-[0.92] text-white md:text-6xl">{title}</h2>
      <p className="mt-4 max-w-2xl text-base leading-7 text-slate-300 md:text-lg md:leading-8">{description}</p>
    </div>
  )
}
