# Marco legal — AI Dubbing Legal Studio

## Cumplimiento normativo

El sistema está diseñado para cumplir con:

- **RGPD (UE) 2016/679**: Protección de datos personales
- **LOPDGDD 3/2018**: Ley Orgánica de Protección de Datos española
- **Ley de Propiedad Intelectual**: Derechos de autor y voces
- **Código Civil**: Contratos y consentimientos

## Validación legal de contratos

Cada job en modo `voz_original_ia_autorizada` ejecuta:

1. **Contrato activo**: El contrato no está desactivado
2. **Consentimiento IA**: Existe cláusula explícita de consentimiento para uso de IA
3. **Idioma autorizado**: El idioma destino está en la lista del contrato
4. **Territorio autorizado**: El territorio de explotación está permitido
5. **Tipo de uso**: El uso (dubbing, trailer, etc.) está autorizado
6. **Vigencia**: La fecha actual no supera la fecha de expiración

Si cualquiera falla → `blocked_legal` + alerta + audit log.

## Trazabilidad

Cada operación queda registrada en `audit_logs`:

- Quién (user_id)
- Qué (action)
- Cuándo (created_at)
- Dónde (ip_address)
- Contexto (project_id, job_id, entity_type, entity_id)
- Detalles técnicos (modelos, prompts, versiones)

## Informe legal

Por cada job se puede generar un informe PDF que incluye:
- Datos del proyecto y organización
- Contrato asociado y permisos
- Actor/voz utilizada
- Modelos y proveedores
- Timestamps de cada paso
- Resultado de validaciones
- Aprobaciones
- Hash de archivos generados

## Recomendaciones

- No usar voces sin contrato activo con consentimiento IA explícito
- Revisar expiraciones de contratos semanalmente
- Mantener logs de auditoría por mínimo 3 años
- No exponer rutas internas en informes para clientes externos
- No compartir claves API ni secretos en logs
