// build-feature.js — серьёзный (не "на коленке") цикл разработки фичи ПравоАгент.
// plan → параллельная сборка (backend+frontend) → adversarial verify → synthesize.
//
// Запуск: "use a workflow build-feature" (или Workflow tool с name: 'build-feature'),
// передать spec в args: { spec: "..." }.

export const meta = {
  name: 'build-feature',
  description:
    'Цикл разработки фичи: план → параллельная сборка (backend+frontend) → ' +
    'адверсариальная проверка (code-reviewer + security-auditor) → синтез. ' +
    'Без заглушек, с проверкой tenant_id и безопасности.',
  phases: [
    { title: 'Plan', detail: 'main: spec → план + критерии приёмки' },
    { title: 'Build', detail: 'backend-dev + frontend-dev параллельно' },
    { title: 'Verify', detail: 'code-reviewer + security-auditor (adversarial)' },
    { title: 'Synthesize', detail: 'main: правки находок + сводка' },
  ],
}

const SCHEMA = (label) => ({
  type: 'object',
  required: ['summary'],
  properties: {
    summary: { type: 'string', description: label },
    findings: {
      type: 'array',
      items: {
        type: 'object',
        required: ['severity', 'location', 'issue'],
        properties: {
          severity: { type: 'string', enum: ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'OK'] },
          location: { type: 'string', description: 'file:line' },
          issue: { type: 'string' },
        },
      },
    },
  },
})

phase('Plan')
const spec = (typeof args !== 'undefined' && args && args.spec) || '(spec не передан — уточни у пользователя)'
log('Plan: превращаю spec в план реализации')
const plan = await agent(
  'Ты ведущий разработчик ПравоАгент. Преврати спецификацию в план реализации. ' +
    'Укажи: (1) файлы для backend, (2) файлы для frontend, (3) критерии приёмки, ' +
    '4) риски/edge-cases, (5) какие ADR затрагивает. Не пиши код — только план. ' +
    'Спецификация:\n' + spec,
  { label: 'plan', phase: 'Plan' }
)

phase('Build')
log('Build: backend-dev + frontend-dev параллельно')
const [backend, frontend] = await parallel([
  () => agent(
    'Реализуй backend-часть по плану. FastAPI async + type hints, tenant_id во всех ' +
      'tenant-запросах, LangGraph/model_router по ADR, явная обработка ошибок. ' +
      'Никаких заглушек без "FLAGGING FOR REVIEW". План:\n' + plan,
    { label: 'backend-dev', phase: 'Build', agentType: 'backend-dev' }
  ),
  () => agent(
    'Реализуй UI по плану. HTMX/Alpine/Jinja2, цвета только из static/css/tokens.css, ' +
      'enterprise-стиль (без AI-vibe), доступность, адаптив. План:\n' + plan,
    { label: 'frontend-dev', phase: 'Build', agentType: 'frontend-dev' }
  ),
])

phase('Verify')
log('Verify: adversarial review (code-reviewer + security-auditor)')
const [review, security] = await parallel([
  () => agent(
    'Дотошно проверь обе части (backend + frontend). Ищи: заглушки/TODO/mock, баги, ' +
      'нарушения ADR, ПРОПУЩЕННЫЕ tenant_id, SQL/prompt-inject/XSS/path-traversal, ' +
      'голые except. VERDICT: OK | NOT OK + findings с severity и file:line. ' +
      'Backend:\n' + backend + '\n\nFrontend:\n' + frontend,
    { label: 'code-reviewer', phase: 'Verify', agentType: 'code-reviewer', schema: SCHEMA('review verdict') }
  ),
  () => agent(
    'Аудит безопасности для legal-data платформы. Tenant isolation (каждый tenant-запрос ' +
      'фильтруется по tenant_id из сессии), PII в логах, prompt-injection (|safe для LLM ' +
      'запрещён), секреты, authn/authz/RBAC, лимиты загрузок. SEVERITY + file:line + fix. ' +
      'Backend:\n' + backend + '\n\nFrontend:\n' + frontend,
    { label: 'security-auditor', phase: 'Verify', agentType: 'security-auditor', schema: SCHEMA('security audit') }
  ),
])

phase('Synthesize')
log('Synthesize: правка находок + сводка')
const synthesis = await agent(
  'Синтезируй результат сборки фичи ПравоАгент. ' +
    '1) Если review/security вернули CRITICAL/HIGH — ИСПРАВЬ их (через Edit/Write). ' +
    '2) MEDIUM/LOW — исправь если дёшево, иначе отметь. ' +
    '3) Никаких заглушек без "FLAGGING FOR REVIEW". ' +
    '4) В конце — краткая сводка: что сделано, статус verify, готовность к /deploy. ' +
    'Review:\n' + JSON.stringify(review, null, 2) +
    '\n\nSecurity:\n' + JSON.stringify(security, null, 2) +
    '\n\nBackend-результат:\n' + backend +
    '\n\nFrontend-результат:\n' + frontend,
  { label: 'synthesize', phase: 'Synthesize' }
)

return { plan, backend, frontend, review, security, synthesis }
