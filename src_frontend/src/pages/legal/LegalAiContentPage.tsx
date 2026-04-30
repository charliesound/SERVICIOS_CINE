import LegalPageShell from './LegalPageShell'

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="landing-panel rounded-[1.8rem] p-6 md:p-8">
      <h2 className="text-2xl font-semibold text-white">{title}</h2>
      <div className="mt-4 space-y-4 text-sm leading-8 text-slate-300 md:text-base">{children}</div>
    </section>
  )
}

export default function LegalAiContentPage() {
  return (
    <LegalPageShell
      eyebrow="Legal / IA y contenidos"
      title="Uso provisional de IA y contenidos en la demo de CID"
      description="Esta pagina resume de forma honesta y provisional algunas condiciones sobre materiales, analisis y resultados generados o asistidos por IA dentro de la demo. No sustituye una politica definitiva de propiedad intelectual, compliance o tratamiento de contenidos."
    >
      <Section title="1. Naturaleza asistida del sistema">
        <p>
          CID puede ayudar a estructurar, analizar, visualizar o presentar proyectos audiovisuales mediante procesos asistidos por software e IA. Los resultados deben entenderse como apoyo operativo y creativo, no como sustitucion automatica del criterio profesional humano.
        </p>
      </Section>

      <Section title="2. Materiales aportados por el usuario">
        <p>
          Durante una demo, cualquier guion, tratamiento, documento, imagen o referencia deberia cargarse solo si la persona o entidad que lo aporta dispone de derechos, permisos o legitimacion suficiente para utilizarlo en ese contexto.
        </p>
      </Section>

      <Section title="3. Resultados generados o transformados">
        <p>
          Los outputs de una demo pueden incluir analisis, propuestas visuales, storyboards, estructuras de proyecto, resumentes o materiales derivados. Su validez creativa, juridica, tecnica o comercial debe revisarse antes de cualquier uso real, difusion externa o explotacion posterior.
        </p>
      </Section>

      <Section title="4. Limitaciones y cautelas">
        <p>
          En esta fase no debe asumirse que todo resultado generado por IA es exacto, completo, original, libre de conflictos de derechos o apto para uso contractual sin revision adicional.
        </p>
        <p>
          Tampoco debe asumirse que una demo define por si sola el regimen final de propiedad, licencia, entrenamiento, conservacion o reutilizacion de materiales y resultados.
        </p>
      </Section>

      <Section title="5. Revision humana obligatoria">
        <p>
          La toma de decisiones creativas, editoriales, de produccion, legales o de distribucion debe mantenerse bajo supervision humana. La demo de CID se presenta como una capa de apoyo y coordinacion, no como automatizacion plena del trabajo audiovisual.
        </p>
      </Section>

      <Section title="6. Politica definitiva pendiente">
        <p>
          Antes de un uso comercial estable debera definirse por escrito un marco completo sobre ingestion de materiales, derechos, responsabilidad sobre prompts y resultados, retencion de activos, y limites de uso de funciones asistidas por IA.
        </p>
      </Section>
    </LegalPageShell>
  )
}
