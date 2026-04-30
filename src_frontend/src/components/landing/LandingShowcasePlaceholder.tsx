interface LandingShowcasePlaceholderProps {
  variant: 'control' | 'storyboard' | 'business'
}

const storyboardFrames = Array.from({ length: 8 }, (_, index) => index)

export default function LandingShowcasePlaceholder({ variant }: LandingShowcasePlaceholderProps) {
  if (variant === 'storyboard') {
    return (
      <div className="landing-placeholder-shell">
        <div className="landing-placeholder-window">
          <div className="landing-placeholder-toolbar">
            <span />
            <span />
            <span />
          </div>
          <div className="landing-storyboard-grid">
            {storyboardFrames.map((frame) => (
              <div key={frame} className="landing-storyboard-frame">
                <div className="landing-storyboard-art" />
                <div className="landing-storyboard-meta">
                  <span>Seq 0{Math.floor(frame / 2) + 1}</span>
                  <span>Beat {frame + 1}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  if (variant === 'business') {
    return (
      <div className="landing-placeholder-shell">
        <div className="landing-placeholder-window">
          <div className="landing-placeholder-toolbar">
            <span />
            <span />
            <span />
          </div>
          <div className="landing-business-layout">
            <div className="landing-business-card landing-business-card-hero">
              <p>Funding map</p>
              <div className="landing-business-bars">
                <span style={{ width: '88%' }} />
                <span style={{ width: '64%' }} />
                <span style={{ width: '76%' }} />
              </div>
            </div>
            <div className="landing-business-card">
              <p>Budget scenarios</p>
              <div className="landing-business-rings">
                <span />
                <span />
                <span />
              </div>
            </div>
            <div className="landing-business-card">
              <p>Checklist</p>
              <ul>
                <li />
                <li />
                <li />
                <li />
              </ul>
            </div>
            <div className="landing-business-card landing-business-card-wide">
              <p>Review to delivery</p>
              <div className="landing-business-track">
                <span />
                <span />
                <span />
                <span />
              </div>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="landing-placeholder-shell">
      <div className="landing-placeholder-window">
        <div className="landing-placeholder-toolbar">
          <span />
          <span />
          <span />
        </div>
        <div className="landing-control-placeholder">
          <div className="landing-control-sidebar">
            {['Guion', 'Analisis', 'Storyboard', 'Presupuesto', 'Produccion'].map((item) => (
              <div key={item} className="landing-control-chip">
                {item}
              </div>
            ))}
          </div>
          <div className="landing-control-main">
            <div className="landing-control-stage landing-control-stage-hero">
              <div className="landing-control-stage-glow" />
              <div className="landing-control-chart" />
            </div>
            <div className="landing-control-stage-grid">
              <div className="landing-control-stage">
                <div className="landing-control-lines">
                  <span />
                  <span />
                  <span />
                </div>
              </div>
              <div className="landing-control-stage">
                <div className="landing-control-dots">
                  <span />
                  <span />
                  <span />
                  <span />
                </div>
              </div>
              <div className="landing-control-stage">
                <div className="landing-control-bars">
                  <span />
                  <span />
                  <span />
                </div>
              </div>
              <div className="landing-control-stage">
                <div className="landing-control-mini-track">
                  <span />
                  <span />
                  <span />
                  <span />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
