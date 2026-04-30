export type DemoProject = {
  id: string
  name: string
  type: string
  status: 'desarrollo' | 'preproduccion' | 'produccion' | 'postproduccion' | 'entregado'
  description: string
  genre: string
  duration_minutes: number
  budget: number
}

export const DEMO_PROJECTS: DemoProject[] = [
  {
    id: 'proj-001',
    name: 'La Ultima Llamada',
    type: 'cortometraje',
    status: 'produccion',
    description: 'Drama sobre un director que recibe una llamada inesperada que cambia todo.',
    genre: 'Drama',
    duration_minutes: 15,
    budget: 12000,
  },
  {
    id: 'proj-002',
    name: 'El Viaje de Ana',
    type: 'largometraje',
    status: 'desarrollo',
    description: 'Road movie experimental sobre una mujer que busca su identidad.',
    genre: 'Experimental',
    duration_minutes: 90,
    budget: 85000,
  },
  {
    id: 'proj-003',
    name: 'Sombras en la Ciudad',
    type: 'documental',
    status: 'postproduccion',
    description: 'Documental sobre la vida nocturna en Madrid.',
    genre: 'Documental',
    duration_minutes: 75,
    budget: 25000,
  },
  {
    id: 'proj-004',
    name: 'Codigo Secreto',
    type: 'largometraje',
    status: 'entregado',
    description: 'Thriller de ciencia ficcion sobre inteligencia artificial.',
    genre: 'Sci-Fi',
    duration_minutes: 110,
    budget: 250000,
  },
]
