import LegalPageShell from './LegalPageShell'

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="landing-panel rounded-[1.8rem] p-6 md:p-8">
      <h2 className="text-2xl font-semibold text-white">{title}</h2>
      <div className="mt-4 space-y-4 text-sm leading-8 text-slate-300 md:text-base">{children}</div>
    </section>
  )
}

export default function LegalTermsPage() {
  return (
    <LegalPageShell
      eyebrow="Legal / Terminos"
      title="Terminos provisionales de acceso y uso para la demo CID"
      description="Estos terminos describen de forma provisional como deberia usarse el entorno demo de AILinkCinema / CID. No constituyen todavia condiciones contractuales finales ni sustituyen una revision legal completa."
    >
      <Section title="1. Acceso demo">
        <p>
          El acceso a CID durante esta fase se ofrece con fines de demostracion, evaluacion comercial, prueba interna o piloto controlado.
        </p>
        <p>
          Algunas cuentas pueden tener acceso inmediato y otras pueden quedar sujetas a revision, activacion manual o validacion por parte del equipo responsable.
        </p>
      </Section>

      <Section title="2. Uso permitido">
        <p>De forma provisional, el usuario deberia utilizar la demo solo para:</p>
        <p>- explorar la plataforma y sus flujos</p>
        <p>- evaluar encaje comercial o tecnico</p>
        <p>- cargar materiales propios con permiso suficiente para la prueba</p>
        <p>- colaborar con el equipo en el contexto de una demo o piloto</p>
      </Section>

      <Section title="3. Uso no permitido">
        <p>Durante la demo no deberia utilizarse la plataforma para:</p>
        <p>- actividades ilicitas o sin autorizacion</p>
        <p>- cargar materiales sobre los que no existan derechos o permisos suficientes</p>
        <p>- intentar vulnerar seguridad, acceso, limites operativos o aislamiento de cuentas</p>
        <p>- presentar la demo como servicio final garantizado si aun esta en evaluacion</p>
      </Section>

      <Section title="4. Estado del producto">
        <p>
          CID puede incluir funciones en evolucion, modulos limitados o capacidades sujetas a cambios. La demo muestra direccion de producto y valor operativo, pero no debe interpretarse automaticamente como un compromiso funcional cerrado para todos los entornos.
        </p>
      </Section>

      <Section title="5. Cuentas, acceso y suspension">
        <p>
          El acceso puede limitarse, pausarse o retirarse si existen incidencias tecnicas, uso indebido, necesidad de mantenimiento o cambios en el alcance comercial del piloto o la demo.
        </p>
      </Section>

      <Section title="6. Materiales y resultados">
        <p>
          Los materiales cargados por el usuario y los resultados generados durante una demo deben tratarse con cautela. Este texto no fija aun un regimen definitivo de propiedad intelectual, licencias, retencion o exportacion; ese marco debera definirse en documentacion contractual posterior.
        </p>
      </Section>

      <Section title="7. Version contractual futura">
        <p>
          Antes de uso comercial estable sera necesario sustituir estos terminos por condiciones completas adaptadas al modelo de negocio, al mercado aplicable y al tratamiento real de datos, contenidos y entregables.
        </p>
      </Section>
    </LegalPageShell>
  )
}
