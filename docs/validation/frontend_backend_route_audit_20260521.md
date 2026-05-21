# Frontend ↔ Backend Route Audit — 20260521

**Generated:** 2026-05-21
**Backend routes found:** 440
**Frontend API calls found:** 33
**Frontend pages registered:** 44

---

## A) ✅ OK — Frontend calls matched to backend endpoints

- `GET /projects/{projectId}/breakdown/scenes` (breakdown.ts)
- `GET /projects/{projectId}/breakdown/departments` (breakdown.ts)
- `GET /projects/{projectId}/breakdown/export?format={format}` (breakdown.ts)
- `POST /projects/{projectId}/editorial/reconcile` (editorial.ts)
- `POST /projects/{projectId}/editorial/score` (editorial.ts)
- `GET /projects/{projectId}/editorial/export/fcpxml` (editorial.ts)
- `POST /projects/{projectId}/editorial/export/package` (editorial.ts)
- `POST /projects/{projectId}/editorial/export/davinci-package` (editorial.ts)
- `GET /ops/instances/{backend}` (ops.ts)
- `POST /ops/instances/{backend}/health-check` (ops.ts)
- `POST /projects/{projectId}/members/delegate` (projectMembers.ts)
- `POST /projects/{projectId}/documents` (projects.ts)
- `POST /projects/{projectId}/analyze` (projects.ts)
- `POST /projects/{projectId}/analysis/run` (projects.ts)
- `GET /projects/{projectId}/analysis/summary` (projects.ts)
- `GET /projects/{projectId}/breakdown/scenes` (projects.ts)
- `GET /projects/{projectId}/breakdown/departments` (projects.ts)
- `POST /projects/{projectId}/storyboard` (projects.ts)
- `GET /projects/{projectId}/export/json` (projects.ts)
- `GET /projects/jobs/{jobId}` (projects.ts)
- `GET /projects/{projectId}/jobs/{jobId}/progress` (projects.ts)
- `GET /delivery/deliverables/{deliverableId}/download` (projects.ts)
- `GET /projects/{projectId}/export/zip` (projects.ts)
- `POST /queue/{jobId}/cancel` (queue.ts)
- `POST /queue/{jobId}/retry` (queue.ts)
- `POST /projects/{projectId}/analysis/run` (scriptAnalysis.ts)
- `GET /projects/{projectId}/analysis/summary` (scriptAnalysis.ts)
- `GET /projects/{projectId}/analysis/export` (scriptAnalysis.ts)
- `GET /projects/{projectId}/module-status` (scriptAnalysis.ts)
- `DELETE /projects/{projectId}/shots/{shotId}` (storyboard.ts)
- `POST /projects/{projectId}/storyboard/sequences/{sequenceId}/regenerate` (storyboard.ts)
- `GET /projects/{projectId}/storyboard/sequences/{sequenceId}/export/zip` (storyboard.ts)
- `GET /projects/{projectId}/storyboard/shots/{shotId}/{type}` (storyboard.ts)

---

## B) ❌ Missing backend — Frontend calls with no backend match

### Allowlisted (known non-blocking)

- `GET /projects/{projectId}/storyboard/shots/{shotId}/{type}` (storyboard.ts) — NOT_FOUND


---

## C) 🗄️ Backend orphan — Backend endpoints not consumed by frontend

- `DELETE /api/producer/saved-opportunities/{param}`
- `DELETE /api/projects/{param}/documents/{param}`
- `DELETE /api/projects/{param}/funding/private-sources/{param}`
- `DELETE /api/projects/{param}/funding/tracking/{param}`
- `DELETE /api/projects/{param}/integrations/google-drive/link-folder/{param}`
- `DELETE /api/projects/{param}/members/{param}`
- `DELETE /api/solutions/{param}`
- `GET /api/admin/funding/calls`
- `GET /api/admin/funding/calls/{param}`
- `GET /api/admin/funding/sources`
- `GET /api/admin/internal/dashboard`
- `GET /api/admin/internal/demo-requests`
- `GET /api/admin/internal/organizations`
- `GET /api/admin/internal/organizations/{param}`
- `GET /api/admin/internal/partner-interests`
- `GET /api/admin/internal/users`
- `GET /api/admin/internal/users/{param}`
- `GET /api/admin/jobs`
- `GET /api/admin/organizations`
- `GET /api/admin/projects`
- `GET /api/admin/scheduler/status`
- `GET /api/admin/system/overview`
- `GET /api/apps)
async def list_apps():
    apps = await get_all_apps()
    return {`
- `GET /api/apps/categories`
- `GET /api/apps/category/{param}`
- `GET /api/apps/integrated`
- `GET /api/apps/standalone`
- `GET /api/apps/{param}`
- `GET /api/auth/me`
- `GET /api/cid/script-to-prompt/director-lenses`
- `GET /api/cid/script-to-prompt/director-lenses/{param}`
- `GET /api/cid/script-to-prompt/montage-profiles`
- `GET /api/cid/visual-reference/profiles/{param}`
- `GET /api/cinematic-taxonomy, response_model=CinematicTaxonomyResponse)
async def get_full_taxonomy():
    service = CinematicTaxonomyService()
    raw = service.get_full_taxonomy()
    categories = {
        cat: [_serialize_element(el) for el in elements]
        for cat, elements in raw.items()
    }
    total = sum(len(v) for v in categories.values())
    return CinematicTaxonomyResponse(categories=categories, total_elements=total)


@router.get(`
- `GET /api/cinematic-taxonomy/presets/{param}`
- `GET /api/cinematic-taxonomy/{param}`
- `GET /api/comfysearch/scan`
- `GET /api/comfysearch/workflows/{param}`
- `GET /api/crm/contacts`
- `GET /api/crm/contacts/{param}`
- `GET /api/delivery/deliverables/{param}`
- `GET /api/delivery/projects/{param}/deliverables`
- `GET /api/delivery/reviews/{param}/deliverable`
- `GET /api/demo/jobs/{param}`
- `GET /api/demo/narrative-html`
- `GET /api/demo/narrative-project`
- `GET /api/demo/presets`
- `GET /api/demo/projects`
- `GET /api/demo/status`
- `GET /api/demo/users`
- `GET /api/dev/cid-test/status`
- `GET /api/dubbing/audit/job/{param}`
- `GET /api/dubbing/jobs/{param}`
- `GET /api/dubbing/projects/{param}/jobs`
- `GET /api/events/subscribe/{param}`
- `GET /api/funding/opportunities`
- `GET /api/funding/opportunities/{param}`
- `GET /api/funding/{param}/funding/checklist`
- `GET /api/funding/{param}/funding/dossier`
- `GET /api/funding/{param}/funding/dossier/export/pdf`
- `GET /api/funding/{param}/funding/matcher-status`
- `GET /api/funding/{param}/funding/matches`
- `GET /api/funding/{param}/funding/matches-rag`
- `GET /api/funding/{param}/funding/matches/{param}/evidence`
- `GET /api/funding/{param}/funding/profile`
- `GET /api/ingest/assets`
- `GET /api/ingest/assets/{param}`
- `GET /api/ingest/camera-reports`
- `GET /api/ingest/camera-reports/{param}`
- `GET /api/ingest/director-notes`
- `GET /api/ingest/director-notes/{param}`
- `GET /api/ingest/documents/{param}`
- `GET /api/ingest/documents/{param}/events`
- `GET /api/ingest/scans`
- `GET /api/ingest/scans/{param}`
- `GET /api/ingest/script-notes`
- `GET /api/ingest/script-notes/{param}`
- `GET /api/ingest/sound-reports`
- `GET /api/ingest/sound-reports/{param}`
- `GET /api/integrations/google-drive/callback`
- `GET /api/integrations/google-drive/connect`
- `GET /api/integrations/google-drive/status`
- `GET /api/metrics, response_model=MetricsResponse)
async def get_metrics():
    return metrics_collector.get_metrics()


@router.get(`
- `GET /api/modules/catalog`
- `GET /api/modules/me`
- `GET /api/modules/{param}`
- `GET /api/ops/can-run`
- `GET /api/ops/capabilities`
- `GET /api/ops/capabilities/{param}`
- `GET /api/ops/comfyui/classify`
- `GET /api/ops/comfyui/models`
- `GET /api/ops/comfyui/prompt/{param}/status`
- `GET /api/ops/comfyui/recommend`
- `GET /api/ops/comfyui/search`
- `GET /api/ops/comfyui/storyboard/status`
- `GET /api/ops/comfyui/workflows`
- `GET /api/ops/instances`
- `GET /api/ops/llm/status`
- `GET /api/ops/ollama/status`
- `GET /api/ops/status`
- `GET /api/pipelines/jobs`
- `GET /api/pipelines/jobs/{param}`
- `GET /api/pipelines/presets`
- `GET /api/plans/catalog`
- `GET /api/plans/me`
- `GET /api/plans/{param}`
- `GET /api/plans/{param}/can-run/{param}`
- `GET /api/postproduction/status`
- `GET /api/producer/dashboard`
- `GET /api/producer/demo-requests`
- `GET /api/producer/funding/opportunities`
- `GET /api/producer/saved-opportunities`
- `GET /api/projects)
async def list_projects(
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
):
    user_org_id = str(tenant.organization_id)

    result = await db.execute(
        select(Project)
        .where(Project.organization_id == user_org_id)
        .order_by(Project.created_at.desc(), Project.id.desc())
    )
    projects = result.scalars().all()

    return {`
- `GET /api/projects/{param}`
- `GET /api/projects/{param}/assets`
- `GET /api/projects/{param}/assets/image-assets`
- `GET /api/projects/{param}/breakdown/export`
- `GET /api/projects/{param}/budgets)
async def list_project_budgets(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
):
    `
- `GET /api/projects/{param}/budgets/active`
- `GET /api/projects/{param}/budgets/{param}`
- `GET /api/projects/{param}/budgets/{param}/export/csv`
- `GET /api/projects/{param}/budgets/{param}/export/json`
- `GET /api/projects/{param}/change-requests)
async def list_change_requests_endpoint(
    project_id: str,
    status: Optional[str] = None,
    target_module: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
):
    `
- `GET /api/projects/{param}/change-requests/{param}`
- `GET /api/projects/{param}/concept-art/jobs`
- `GET /api/projects/{param}/crm/communications`
- `GET /api/projects/{param}/crm/opportunities`
- `GET /api/projects/{param}/crm/opportunities/{param}`
- `GET /api/projects/{param}/crm/summary`
- `GET /api/projects/{param}/crm/tasks`
- `GET /api/projects/{param}/dashboard`
- `GET /api/projects/{param}/distribution-packs`
- `GET /api/projects/{param}/distribution-packs/{param}`
- `GET /api/projects/{param}/distribution-packs/{param}/export/json`
- `GET /api/projects/{param}/distribution-packs/{param}/export/markdown`
- `GET /api/projects/{param}/distribution-packs/{param}/export/zip`
- `GET /api/projects/{param}/documents`
- `GET /api/projects/{param}/documents/{param}`
- `GET /api/projects/{param}/documents/{param}/chunks`
- `GET /api/projects/{param}/documents/{param}/download`
- `GET /api/projects/{param}/editorial/assembly`
- `GET /api/projects/{param}/editorial/audio-metadata`
- `GET /api/projects/{param}/editorial/export/fcpxml/validate`
- `GET /api/projects/{param}/editorial/media-relink-report`
- `GET /api/projects/{param}/editorial/recommended-takes`
- `GET /api/projects/{param}/editorial/takes`
- `GET /api/projects/{param}/funding/matcher/jobs`
- `GET /api/projects/{param}/funding/matcher/status`
- `GET /api/projects/{param}/funding/notifications`
- `GET /api/projects/{param}/funding/private-sources`
- `GET /api/projects/{param}/funding/private-summary`
- `GET /api/projects/{param}/funding/tracking`
- `GET /api/projects/{param}/funding/tracking/{param}`
- `GET /api/projects/{param}/funding/tracking/{param}/checklist`
- `GET /api/projects/{param}/integrations/google-drive/folders`
- `GET /api/projects/{param}/integrations/google-drive/link-folder`
- `GET /api/projects/{param}/integrations/google-drive/sync-status`
- `GET /api/projects/{param}/jobs`
- `GET /api/projects/{param}/jobs/{param}`
- `GET /api/projects/{param}/members)
async def list_project_members(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
):
    `
- `GET /api/projects/{param}/members/me`
- `GET /api/projects/{param}/members/roles`
- `GET /api/projects/{param}/members/{param}/permissions`
- `GET /api/projects/{param}/metrics`
- `GET /api/projects/{param}/planned-shots)
async def list_planned_shots(
    project_id: str,
    sequence_number: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
):
    `
- `GET /api/projects/{param}/planned-shots/coverage`
- `GET /api/projects/{param}/presentation/assets/{param}/preview`
- `GET /api/projects/{param}/presentation/assets/{param}/thumbnail`
- `GET /api/projects/{param}/presentation/export/pdf`
- `GET /api/projects/{param}/presentation/filmstrip`
- `GET /api/projects/{param}/presentation/filmstrip.html`
- `GET /api/projects/{param}/producer-pitch`
- `GET /api/projects/{param}/producer-pitch/active`
- `GET /api/projects/{param}/producer-pitch/{param}`
- `GET /api/projects/{param}/producer-pitch/{param}/export/json`
- `GET /api/projects/{param}/producer-pitch/{param}/export/markdown`
- `GET /api/projects/{param}/producer-pitch/{param}/export/zip`
- `GET /api/projects/{param}/sales-opportunities`
- `GET /api/projects/{param}/script/change-reports`
- `GET /api/projects/{param}/script/versions`
- `GET /api/projects/{param}/script/versions/{param}`
- `GET /api/projects/{param}/shooting-plans)
async def list_shooting_plans(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
):
    `
- `GET /api/projects/{param}/shooting-plans/coverage`
- `GET /api/projects/{param}/shooting-plans/{param}`
- `GET /api/projects/{param}/shooting-plans/{param}/coverage`
- `GET /api/projects/{param}/shots`
- `GET /api/projects/{param}/storyboard`
- `GET /api/projects/{param}/storyboard/options`
- `GET /api/projects/{param}/storyboard/sequences`
- `GET /api/projects/{param}/storyboard/sequences/{param}`
- `GET /api/projects/{param}/storyboard/sheet/artifacts/{filename:path}`
- `GET /api/projects/{param}/storyboard/shots/{param}/image`
- `GET /api/projects/{param}/storyboard/shots/{param}/revisions`
- `GET /api/projects/{param}/storyboard/shots/{param}/thumbnail`
- `GET /api/projects/{param}/visual-bible, response_model=ProjectVisualBibleResponse)
async def api_get_visual_bible(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
):
    vb = await get_or_create_visual_bible(db, project_id, tenant)
    return _to_response(vb)


@router.put(`
- `GET /api/queue/status`
- `GET /api/queue/status/{param}`
- `GET /api/render/jobs`
- `GET /api/render/jobs/{param}`
- `GET /api/reviews/projects/{param}`
- `GET /api/reviews/{param}`
- `GET /api/reviews/{param}/comments`
- `GET /api/sales-targets`
- `GET /api/sales-targets/{param}`
- `GET /api/solutions, response_model=list[SolutionOut])
async def list_all(backend: str = None, tag: str = None):
    return list_solutions(backend=backend, tag=tag)


@router.post(`
- `GET /api/solutions/{param}`
- `GET /api/storage-sources, response_model=StorageSourceListResponse)
async def list_storage_sources(
    project_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> StorageSourceListResponse:
    user_org_id = str(tenant.organization_id)

    if project_id:
        project_result = await db.execute(
            select(Project).where(
                Project.id == project_id,
                Project.organization_id == user_org_id,
            )
        )
        project = project_result.scalar_one_or_none()
        if not project:
            raise HTTPException(status_code=404, detail=`
- `GET /api/storage-sources/{param}`
- `GET /api/storage-sources/{param}/authorizations`
- `GET /api/storage-sources/{param}/handshake`
- `GET /api/storage-sources/{param}/watch-paths`
- `GET /api/users`
- `GET /api/users/{param}`
- `GET /api/v1/comfyui/health`
- `GET /api/v1/comfyui/instances`
- `GET /api/v1/comfyui/instances/{param}`
- `GET /api/v1/comfyui/instances/{param}/health`
- `GET /api/v1/comfyui/resolve/{param}`
- `GET /api/workflows/catalog`
- `GET /api/workflows/experimental/modules/{param}`
- `GET /api/workflows/experimental/status`
- `GET /api/workflows/presets`
- `GET /api/workflows/presets/{param}`
- `PATCH /api/admin/funding/calls/{param}`
- `PATCH /api/crm/contacts/{param}`
- `PATCH /api/delivery/deliverables/{param}`
- `PATCH /api/ingest/camera-reports/{param}`
- `PATCH /api/ingest/director-notes/{param}`
- `PATCH /api/ingest/documents/{param}`
- `PATCH /api/ingest/script-notes/{param}`
- `PATCH /api/ingest/sound-reports/{param}`
- `PATCH /api/projects/{param}/crm/opportunities/{param}`
- `PATCH /api/projects/{param}/distribution-packs/{param}`
- `PATCH /api/projects/{param}/funding/notifications/{param}/read`
- `PATCH /api/projects/{param}/funding/private-sources/{param}`
- `PATCH /api/projects/{param}/funding/tracking/{param}`
- `PATCH /api/projects/{param}/funding/tracking/{param}/checklist/{param}`
- `PATCH /api/projects/{param}/members/{param}`
- `PATCH /api/projects/{param}/producer-pitch/{param}`
- `PATCH /api/projects/{param}/sales-opportunities/{param}`
- `PATCH /api/reviews/{param}`
- `PATCH /api/sales-targets/{param}`
- `PATCH /api/storage-sources/{param}`
- `PATCH /api/users/{param}/plan`
- `POST /api/admin/funding/calls`
- `POST /api/admin/funding/sources`
- `POST /api/admin/funding/sync/mock-refresh`
- `POST /api/admin/funding/sync/seed`
- `POST /api/apps/refresh`
- `POST /api/auth/forgot-password`
- `POST /api/auth/login`
- `POST /api/auth/register`
- `POST /api/auth/register/cid`
- `POST /api/auth/register/demo`
- `POST /api/auth/register/partner`
- `POST /api/auth/reset-password`
- `POST /api/cid/script-to-prompt/analyze-full`
- `POST /api/cid/script-to-prompt/director-lenses/choose`
- `POST /api/cid/script-to-prompt/directorial-intent`
- `POST /api/cid/script-to-prompt/editorial-beats`
- `POST /api/cid/script-to-prompt/intent`
- `POST /api/cid/script-to-prompt/montage-intent`
- `POST /api/cid/script-to-prompt/parse`
- `POST /api/cid/script-to-prompt/prompt`
- `POST /api/cid/script-to-prompt/run`
- `POST /api/cid/script-to-prompt/shot-editorial-purpose`
- `POST /api/cid/script-to-prompt/validate`
- `POST /api/cid/visual-reference/align-with-script`
- `POST /api/cid/visual-reference/analyze`
- `POST /api/cid/visual-reference/apply-to-scene`
- `POST /api/cid/visual-reference/apply-to-storyboard`
- `POST /api/cid/visual-reference/enriched-intent`
- `POST /api/cinematic-taxonomy/enrich-prompt`
- `POST /api/comfysearch/reindex`
- `POST /api/comfysearch/search`
- `POST /api/crm/contacts`
- `POST /api/crm/contacts/{param}/archive`
- `POST /api/delivery/projects/{param}/deliverables`
- `POST /api/delivery/projects/{param}/export`
- `POST /api/demo/quick-start`
- `POST /api/demo/reset`
- `POST /api/demo/seed`
- `POST /api/demo/seed-narrative`
- `POST /api/dev/cid-test/run-full-pipeline`
- `POST /api/dev/cid-test/simulate-access`
- `POST /api/dev/cid-test/simulate-demo-project`
- `POST /api/dubbing/contracts/{param}/validate`
- `POST /api/dubbing/projects/{param}/jobs`
- `POST /api/events/job-status`
- `POST /api/funding/{param}/budget/estimate`
- `POST /api/funding/{param}/funding/dossier/export/pdf/persist`
- `POST /api/funding/{param}/funding/recompute`
- `POST /api/funding/{param}/funding/recompute-rag`
- `POST /api/ingest/camera-reports`
- `POST /api/ingest/director-notes`
- `POST /api/ingest/documents, response_model=DocumentAssetResponse)
async def create_document_asset(
    payload: DocumentAssetCreate,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
    ) -> DocumentAssetResponse:
    document = await document_service.create_document(
        db,
        user_org_id=str(tenant.organization_id),
        payload=payload.model_dump(exclude_none=True),
        uploaded_by=tenant.user_id,
    )
    return _document_response(document)


@router.get(`
- `POST /api/ingest/documents/{param}/approve`
- `POST /api/ingest/documents/{param}/classify`
- `POST /api/ingest/documents/{param}/derive-preview`
- `POST /api/ingest/documents/{param}/derive-report`
- `POST /api/ingest/documents/{param}/extract`
- `POST /api/ingest/documents/{param}/structure`
- `POST /api/ingest/script-notes`
- `POST /api/ingest/sound-reports`
- `POST /api/integrations/google-drive/disconnect`
- `POST /api/ops/comfyui/concept-art/compile-workflow-dry-run`
- `POST /api/ops/comfyui/pipeline-builder`
- `POST /api/ops/comfyui/storyboard/compile-workflow-dry-run`
- `POST /api/ops/comfyui/storyboard/render`
- `POST /api/ops/comfyui/storyboard/render-dry-run`
- `POST /api/ops/health-check-all`
- `POST /api/pipelines/execute`
- `POST /api/pipelines/generate`
- `POST /api/pipelines/validate`
- `POST /api/plans/change`
- `POST /api/producer/demo-request`
- `POST /api/producer/saved-opportunities`
- `POST /api/projects, response_model=ProjectResponse)
async def create_project(
    payload: CreateProjectPayload,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
):
    user_org_id = str(tenant.organization_id)

    await _enforce_plan_limit(
        db=db,
        organization_id=user_org_id,
        user_plan=tenant.plan,
        resource=`
- `POST /api/projects/intake/idea`
- `POST /api/projects/{param}/analyze/local-ollama`
- `POST /api/projects/{param}/ask`
- `POST /api/projects/{param}/budgets/generate`
- `POST /api/projects/{param}/budgets/{param}/activate`
- `POST /api/projects/{param}/budgets/{param}/archive`
- `POST /api/projects/{param}/budgets/{param}/recalculate`
- `POST /api/projects/{param}/change-requests)
async def create_change_request_endpoint(
    project_id: str,
    payload: CreateChangeRequestPayload,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
):
    `
- `POST /api/projects/{param}/change-requests/{param}/apply`
- `POST /api/projects/{param}/change-requests/{param}/approve`
- `POST /api/projects/{param}/change-requests/{param}/reject`
- `POST /api/projects/{param}/concept-art/compile-workflow-dry-run`
- `POST /api/projects/{param}/crm/communications`
- `POST /api/projects/{param}/crm/opportunities`
- `POST /api/projects/{param}/crm/opportunities/{param}/status`
- `POST /api/projects/{param}/crm/tasks`
- `POST /api/projects/{param}/crm/tasks/{param}/cancel`
- `POST /api/projects/{param}/crm/tasks/{param}/complete`
- `POST /api/projects/{param}/distribution-packs/generate`
- `POST /api/projects/{param}/distribution-packs/{param}/approve`
- `POST /api/projects/{param}/distribution-packs/{param}/archive`
- `POST /api/projects/{param}/documents/reindex`
- `POST /api/projects/{param}/editorial/assembly`
- `POST /api/projects/{param}/editorial/audio-metadata/scan`
- `POST /api/projects/{param}/funding/matcher/trigger`
- `POST /api/projects/{param}/funding/private-sources`
- `POST /api/projects/{param}/funding/tracking`
- `POST /api/projects/{param}/intake/script`
- `POST /api/projects/{param}/integrations/google-drive/link-folder`
- `POST /api/projects/{param}/integrations/google-drive/sync`
- `POST /api/projects/{param}/jobs/{param}/retry`
- `POST /api/projects/{param}/key-visual/compile-workflow-dry-run`
- `POST /api/projects/{param}/members)
async def add_project_member_endpoint(
    project_id: str,
    payload: AddMemberPayload,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
):
    `
- `POST /api/projects/{param}/planned-shots/generate`
- `POST /api/projects/{param}/planned-shots/{param}/approve`
- `POST /api/projects/{param}/planned-shots/{param}/reject`
- `POST /api/projects/{param}/presentation/export-pdf`
- `POST /api/projects/{param}/presentation/export/pdf/persist`
- `POST /api/projects/{param}/producer-pitch/generate`
- `POST /api/projects/{param}/producer-pitch/{param}/approve`
- `POST /api/projects/{param}/producer-pitch/{param}/archive`
- `POST /api/projects/{param}/sales-opportunities`
- `POST /api/projects/{param}/sales-opportunities/suggest`
- `POST /api/projects/{param}/script-intelligence/analyze`
- `POST /api/projects/{param}/script/upload`
- `POST /api/projects/{param}/script/versions`
- `POST /api/projects/{param}/script/versions/compare`
- `POST /api/projects/{param}/script/versions/{param}/activate`
- `POST /api/projects/{param}/shooting-plans)
async def create_shooting_plan_endpoint(
    project_id: str,
    payload: CreatePlanPayload,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
):
    `
- `POST /api/projects/{param}/shooting-plans/{param}/approve`
- `POST /api/projects/{param}/shots`
- `POST /api/projects/{param}/storyboard/comfyui/plan`
- `POST /api/projects/{param}/storyboard/comfyui/render-dry-run`
- `POST /api/projects/{param}/storyboard/estimate-credits`
- `POST /api/projects/{param}/storyboard/generate`
- `POST /api/projects/{param}/storyboard/prompts/from-analysis`
- `POST /api/projects/{param}/storyboard/render`
- `POST /api/projects/{param}/storyboard/repair-assets`
- `POST /api/projects/{param}/storyboard/sequences/{param}/feedback`
- `POST /api/projects/{param}/storyboard/sequences/{param}/generate`
- `POST /api/projects/{param}/storyboard/sequences/{param}/plan`
- `POST /api/projects/{param}/storyboard/sequences/{param}/regenerate-failed`
- `POST /api/projects/{param}/storyboard/sheet`
- `POST /api/projects/{param}/storyboard/shots/{param}/feedback`
- `POST /api/projects/{param}/storyboard/shots/{param}/regenerate`
- `POST /api/projects/{param}/visual-bible/preview-prompt`
- `POST /api/projects/{param}/visual-bible/reset`
- `POST /api/render/jobs`
- `POST /api/render/jobs/{param}/retry`
- `POST /api/reviews/projects/{param}`
- `POST /api/reviews/{param}/comments`
- `POST /api/reviews/{param}/decisions`
- `POST /api/sales-targets`
- `POST /api/solutions/seed`
- `POST /api/solutions/{param}/execute`
- `POST /api/storage-sources, response_model=StorageSourceResponse)
async def create_storage_source(
    payload: StorageSourceCreate,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> StorageSourceResponse:
    user_org_id = str(tenant.organization_id)

    project_result = await db.execute(
        select(Project).where(
            Project.id == payload.project_id,
            Project.organization_id == user_org_id,
        )
    )
    project = project_result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail=`
- `POST /api/storage-sources/{param}/authorize`
- `POST /api/storage-sources/{param}/scan`
- `POST /api/storage-sources/{param}/validate`
- `POST /api/storage-sources/{param}/watch-paths`
- `POST /api/users`
- `POST /api/workflows/build`
- `POST /api/workflows/plan`
- `POST /api/workflows/presets`
- `POST /api/workflows/validate`
- `PUT /api/projects/{param}/script`
- `PUT /api/projects/{param}/shots/bulk-reorder`
- `PUT /api/projects/{param}/shots/{param}`

---

## D) 📋 Router not registered check

All route files in `src/routes/` are registered in `app_factory.py`.
Manual verification confirms all routers are included (see app_factory.py `_register_routers`)

---

## E) 🔀 Prefix mismatch / Double-prefix issues

_None_

---

## F) ⚠️ Empty-state risk by page

| Page | File | Risk | Loading | Error | Empty | Retry |
|------|------|------|---------|-------|-------|-------|
| BreakdownPage | BreakdownPage.tsx | LOW | ✅ | ✅ | ✅ | ✅ |
| ScriptAnalysisProPage | ScriptAnalysisProPage.tsx | LOW | ✅ | ✅ | ✅ | ✅ |
| BudgetEstimatorPage | BudgetEstimatorPage.tsx | MEDIUM | ✅ | ✅ | ❌ | ❌ |
| StoryboardBuilderPage | StoryboardBuilderPage.tsx | LOW | ✅ | ✅ | ✅ | ✅ |
| ProjectDashboardPage | ProjectDashboardPage.tsx | LOW | ✅ | ✅ | ✅ | ❌ |
| ProjectMembersPage | ProjectMembersPage.tsx | LOW | ✅ | ✅ | ✅ | ❌ |
| ProjectFundingPage | ProjectFundingPage.tsx | HIGH | ❌ | ❌ | ❌ | ❌ |
| EditorialAssemblyPage | EditorialAssemblyPage.tsx | MEDIUM | ✅ | ✅ | ❌ | ❌ |
| ProducerPitchPackPage | ProducerPitchPackPage.tsx | MEDIUM | ✅ | ✅ | ❌ | ❌ |
| DistributionPackPage | DistributionPackPage.tsx | MEDIUM | ✅ | ✅ | ❌ | ❌ |
| CommercialCrmPage | CommercialCrmPage.tsx | LOW | ✅ | ✅ | ✅ | ❌ |
| ChangeRequestsPage | ChangeRequestsPage.tsx | LOW | ✅ | ✅ | ✅ | ❌ |
| ReviewsOverviewPage | ReviewsOverviewPage.tsx | LOW | ✅ | ✅ | ✅ | ❌ |
| DeliveryOverviewPage | DeliveryOverviewPage.tsx | LOW | ✅ | ✅ | ✅ | ❌ |

---

## G) 📊 Summary

- **Total frontend API calls:** 33
- **Total backend endpoints:** 440
- **Missing backend (critical):** 0
- **Missing backend (allowlisted):** 1
- **Prefix/double-prefix issues:** 0
- **Pages with HIGH empty-state risk:** 1
- **Pages with MEDIUM empty-state risk:** 4
