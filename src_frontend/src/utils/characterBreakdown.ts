export interface CharacterBreakdownEntry {
  character: string
  sequence_ids: string[]
  sequence_numbers: number[]
  appearances: number
  first_sequence: string
}

export function deriveCharacterBreakdown(
  sequences: Array<{
    sequence_id: string
    sequence_number: number
    title: string
    characters: string[]
    location?: string
  }>,
): CharacterBreakdownEntry[] {
  const charMap = new Map<string, { seqIds: Set<string>; seqNums: Set<number> }>()

  for (const seq of sequences) {
    const chars = seq.characters || []
    for (const ch of chars) {
      const key = ch.trim().toUpperCase()
      if (!key) continue
      if (!charMap.has(key)) {
        charMap.set(key, { seqIds: new Set(), seqNums: new Set() })
      }
      const entry = charMap.get(key)!
      entry.seqIds.add(seq.sequence_id)
      entry.seqNums.add(seq.sequence_number)
    }
  }

  const result: CharacterBreakdownEntry[] = []
  for (const [character, data] of charMap) {
    const seqIds = Array.from(data.seqIds)
    const seqNums = Array.from(data.seqNums).sort((a, b) => a - b)
    result.push({
      character,
      sequence_ids: seqIds,
      sequence_numbers: seqNums,
      appearances: seqIds.length,
      first_sequence: seqIds[0] || '',
    })
  }

  result.sort((a, b) => b.appearances - a.appearances || a.character.localeCompare(b.character))
  return result
}
