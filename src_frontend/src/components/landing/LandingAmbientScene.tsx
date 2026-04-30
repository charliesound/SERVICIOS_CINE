const particles = [
  { left: '8%', top: '18%', size: '0.45rem', delay: '0s', duration: '16s' },
  { left: '18%', top: '68%', size: '0.35rem', delay: '1.4s', duration: '18s' },
  { left: '32%', top: '34%', size: '0.28rem', delay: '2.3s', duration: '14s' },
  { left: '48%', top: '12%', size: '0.4rem', delay: '0.8s', duration: '20s' },
  { left: '56%', top: '74%', size: '0.3rem', delay: '2.9s', duration: '17s' },
  { left: '68%', top: '28%', size: '0.5rem', delay: '1.2s', duration: '22s' },
  { left: '78%', top: '60%', size: '0.36rem', delay: '3.2s', duration: '15s' },
  { left: '88%', top: '20%', size: '0.42rem', delay: '0.4s', duration: '19s' },
]

export default function LandingAmbientScene() {
  return (
    <div aria-hidden="true" className="landing-ambient-scene">
      <div className="landing-ambient-grid" />
      <div className="landing-ambient-blob landing-ambient-blob-a" />
      <div className="landing-ambient-blob landing-ambient-blob-b" />
      <div className="landing-ambient-blob landing-ambient-blob-c" />
      <div className="landing-ambient-blob landing-ambient-blob-d" />

      {particles.map((particle, index) => (
        <span
          key={`${particle.left}-${particle.top}-${index}`}
          className="landing-ambient-particle"
          style={{
            left: particle.left,
            top: particle.top,
            width: particle.size,
            height: particle.size,
            animationDelay: particle.delay,
            animationDuration: particle.duration,
          }}
        />
      ))}
    </div>
  )
}
