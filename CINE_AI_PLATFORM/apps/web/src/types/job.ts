/**
 * LEGACY-TRANSIENT
 *
 * Tipo mantenido temporalmente para compatibilidad durante la migración
 * de dashboard mientras se retira el consumo legacy de /jobs.
 */
export interface Job {
  id: string;
  shot_id: string;
  status: string;
  prompt_id?: string | null;
  error?: string | null;
}
