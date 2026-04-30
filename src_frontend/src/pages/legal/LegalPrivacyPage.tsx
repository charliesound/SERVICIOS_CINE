import LegalPageShell from './LegalPageShell'

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="landing-panel rounded-[1.8rem] p-6 md:p-8">
      <h2 className="text-2xl font-semibold text-white">{title}</h2>
      <div className="mt-4 space-y-4 text-sm leading-8 text-slate-300 md:text-base">{children}</div>
    </section>
  )
}

export default function LegalPrivacyPage() {
  return (
    <LegalPageShell
      eyebrow="Legal / Privacidad"
      title="Politica de privacidad provisional para la demo de AILinkCinema / CID"
      description="Este texto resume de forma provisional como podria tratarse la informacion en una demo comercial de CID. Debe revisarse y completarse antes de cualquier despliegue publico o actividad comercial a escala."
    >
      <Section title="1. Finalidad de esta pagina">
        <p>
          Esta politica explica, de forma provisional, que datos podrian recogerse durante una demo de AILinkCinema / CID y con que fines operativos se utilizarian.
        </p>
        <p>
          Su objetivo es informar con claridad durante la fase de demostracion del producto. No sustituye una revision juridica formal ni una politica definitiva adaptada al contexto de explotacion real.
        </p>
      </Section>

      <Section title="2. Datos que podrian tratarse">
        <p>
          Durante el uso de la landing o de una demo guiada podrian tratarse datos de contacto y contexto profesional, por ejemplo: nombre, email, empresa, cargo, necesidades del proyecto y mensajes enviados desde formularios.
        </p>
        <p>
          En flujos internos de producto tambien podrian existir datos operativos asociados a usuarios, proyectos, documentos o materiales que el propio equipo de demo cargue voluntariamente para validar funcionalidades.
        </p>
      </Section>

      <Section title="3. Finalidades provisionales del tratamiento">
        <p>De manera provisional, los datos podrian utilizarse para:</p>
        <p>- responder a solicitudes de demo o contacto comercial</p>
        <p>- habilitar accesos de prueba a CID</p>
        <p>- organizar proyectos demo, materiales y flujos de validacion</p>
        <p>- mantener trazabilidad operativa basica del uso interno de la plataforma</p>
      </Section>

      <Section title="4. Base y limites de uso">
        <p>
          En esta fase solo deberia utilizarse informacion necesaria para atender la solicitud, habilitar la demo o evaluar el producto. No debe asumirse automaticamente un tratamiento amplio, indefinido o reutilizable para fines distintos sin una base adecuada y una politica definitiva.
        </p>
      </Section>

      <Section title="5. Conservacion y acceso">
        <p>
          Los datos de demo deberian conservarse solo durante el tiempo necesario para la relacion comercial preliminar, la validacion tecnica o el seguimiento del piloto correspondiente.
        </p>
        <p>
          El acceso deberia limitarse al equipo interno necesario para operaciones, soporte o continuidad comercial de la demo.
        </p>
      </Section>

      <Section title="6. Proveedores y terceros">
        <p>
          La plataforma puede depender de infraestructura tecnica, servicios de correo, almacenamiento o herramientas auxiliares. Este texto no afirma todavia una lista cerrada de encargados ni un marco contractual completo; esa relacion debe documentarse en la version legal definitiva.
        </p>
      </Section>

      <Section title="7. Derechos y contacto">
        <p>
          Si una persona desea solicitar aclaraciones, rectificacion o eliminacion de datos usados en una demo, deberia poder contactar con el equipo responsable a traves de los canales comerciales u operativos habilitados por AILinkCinema.
        </p>
        <p>
          La version final debera concretar responsable del tratamiento, vias de contacto, base juridica definitiva, plazos y procedimiento de ejercicio de derechos.
        </p>
      </Section>
    </LegalPageShell>
  )
}
