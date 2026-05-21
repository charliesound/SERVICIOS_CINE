export function getScriptUnitLabel(
  analysis?: { sequence_map?: { total_sequences: number } } | null,
  shots?: Array<{ metadata_json?: Record<string, unknown> | null }> | null,
): string {
  if (analysis?.sequence_map && analysis.sequence_map.total_sequences > 0) {
    return 'Secuencias'
  }
  if (shots && shots.length > 0) {
    for (const shot of shots) {
      const meta = shot.metadata_json
      if (meta && typeof meta === 'object') {
        const seqLabel = meta.script_label as string | undefined
        if (seqLabel && /secuencia|seq|sequence/i.test(seqLabel)) return 'Secuencias'
      }
    }
  }
  return 'Escenas/Secuencias'
}

export function getScriptUnitLabelSingular(
  analysis?: { sequence_map?: { total_sequences: number } } | null,
  shots?: Array<{ metadata_json?: Record<string, unknown> | null }> | null,
): string {
  const label = getScriptUnitLabel(analysis, shots)
  if (label === 'Secuencias') return 'Secuencia'
  return 'Escena'
}
