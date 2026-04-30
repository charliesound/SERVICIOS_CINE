import LegalPageShell from './LegalPageShell'

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="landing-panel rounded-[1.8rem] p-6 md:p-8">
      <h2 className="text-2xl font-semibold text-white">{title}</h2>
      <div className="mt-4 space-y-4 text-sm leading-8 text-slate-300 md:text-base">{children}</div>
    </section>
  )
}

export default function LegalNoticePage() {
  return (
    <LegalPageShell
      eyebrow="Legal / Aviso legal"
      title="Aviso legal provisional de AILinkCinema / CID"
      description="Este aviso legal es una version provisional para acompanar la demo comercial del producto. Debe completarse con identificacion societaria, datos de contacto y clausulas definitivas antes de una publicacion oficial o explotacion comercial estable."
    >
      <Section title="1. Naturaleza del sitio">
        <p>
          Esta web y sus vistas asociadas presentan de forma preliminar AILinkCinema / CID como plataforma para desarrollo, produccion y coordinacion audiovisual asistida por IA.
        </p>
        <p>
          El contenido disponible en esta demo tiene finalidad informativa, comercial y de validacion de producto.
        </p>
      </Section>

      <Section title="2. Informacion del responsable">
        <p>
          La identificacion completa de la entidad responsable, domicilio, NIF, vias de contacto y demas datos obligatorios no se detallan aun en esta version provisional.
        </p>
        <p>
          Esa informacion debe incorporarse y verificarse antes de cualquier despliegue publico definitivo.
        </p>
      </Section>

      <Section title="3. Uso del contenido">
        <p>
          Los textos, interfaces, conceptos visuales y materiales mostrados en esta demo se facilitan para evaluar el producto y su propuesta comercial. No debe asumirse licencia general de reutilizacion, redistribucion o explotacion de dichos materiales sin autorizacion expresa.
        </p>
      </Section>

      <Section title="4. Disponibilidad del servicio">
        <p>
          Al tratarse de una demo tecnica o comercial, ciertas funciones pueden estar sujetas a cambios, limitaciones, incidencias temporales o desactivacion sin previo aviso.
        </p>
        <p>
          La mera presencia de una funcionalidad en demo no implica disponibilidad contractual permanente ni SLA definitivo.
        </p>
      </Section>

      <Section title="5. Limitacion provisional de declaraciones">
        <p>
          Este entorno no debe interpretarse como oferta juridicamente cerrada, ni como garantia total de disponibilidad, cumplimiento normativo exhaustivo, idoneidad para un uso concreto o ausencia absoluta de errores.
        </p>
      </Section>

      <Section title="6. Version definitiva pendiente">
        <p>
          Antes de una salida publica formal debera completarse este aviso legal con revision especializada, datos del responsable, politica de propiedad intelectual, jurisdiccion aplicable y clausulas definitivas de uso del sitio.
        </p>
      </Section>
    </LegalPageShell>
  )
}
