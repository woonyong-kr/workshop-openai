import type { WorkstreamDefinition } from "@cleanmail/contracts";

const workstreams: WorkstreamDefinition[] = [
  {
    key: "web-shell",
    owner: "Agent 1",
    scope: "apps/web",
    deliverables: [
      "landing page and dashboard frame",
      "left sidebar with 전체 정리 entry",
      "review table, checkbox state, and modal shell",
    ],
  },
  {
    key: "gmail-core",
    owner: "Agent 2",
    scope: "packages/gmail-core",
    deliverables: [
      "sender normalization and grouping",
      "classification heuristics ported from Python",
      "unsubscribe parsing and execution planning",
    ],
  },
  {
    key: "auth-data",
    owner: "Agent 3",
    scope: "packages/auth-core + packages/data-core",
    deliverables: [
      "Google OAuth and session primitives",
      "token encryption and rotation helpers",
      "Postgres repositories, audit logs, and purge helpers",
    ],
  },
  {
    key: "integration",
    owner: "Agent 4",
    scope: "apps/web/src/app/api + docs",
    deliverables: [
      "route composition against contracts",
      "policy pages and environment docs",
      "Vercel and Google launch wiring",
    ],
  },
];

const repoSlices = [
  {
    path: "apps/web",
    detail: "Next.js UI shell and route handlers",
  },
  {
    path: "packages/contracts",
    detail: "shared payloads and enums all agents must follow",
  },
  {
    path: "packages/gmail-core",
    detail: "Gmail scan, grouping, classification, unsubscribe logic",
  },
  {
    path: "packages/auth-core",
    detail: "OAuth callback, session cookie, refresh token handling",
  },
  {
    path: "packages/data-core",
    detail: "Postgres schema, repositories, audit trail, purge jobs",
  },
];

export default function Home() {
  return (
    <main className="mx-auto flex min-h-screen w-full max-w-7xl flex-col gap-6 px-6 py-8 lg:px-10">
      <section className="grid gap-6 lg:grid-cols-[300px_minmax(0,1fr)]">
        <aside className="rounded-[28px] border border-[var(--border)] bg-[var(--panel)] p-5 shadow-[0_18px_60px_rgba(44,32,12,0.08)]">
          <div className="mb-8">
            <p className="font-[family-name:var(--font-display)] text-xs uppercase tracking-[0.28em] text-[var(--accent)]">
              Cleanmail
            </p>
            <h1 className="mt-3 font-[family-name:var(--font-display)] text-3xl font-semibold leading-tight">
              Multi-agent workspace
            </h1>
            <p className="mt-3 text-sm leading-6 text-[var(--muted)]">
              불필요한 임시 파일은 제거했고, 지금부터는 역할별로 바로 병렬 작업할 수 있는 구조만 남겼습니다.
            </p>
          </div>

          <nav className="space-y-2 text-sm">
            <div className="rounded-2xl bg-[var(--accent-soft)] px-4 py-3 font-medium text-[var(--accent)]">
              전체 정리
            </div>
            <div className="rounded-2xl px-4 py-3 text-[var(--muted)]">
              인증과 세션
            </div>
            <div className="rounded-2xl px-4 py-3 text-[var(--muted)]">
              Gmail 분류 엔진
            </div>
            <div className="rounded-2xl px-4 py-3 text-[var(--muted)]">
              데이터 계층
            </div>
            <div className="rounded-2xl px-4 py-3 text-[var(--muted)]">
              배포와 검증
            </div>
          </nav>
        </aside>

        <div className="space-y-6">
          <section className="rounded-[32px] border border-[var(--border)] bg-[var(--panel)] p-6 shadow-[0_18px_60px_rgba(44,32,12,0.08)] lg:p-8">
            <p className="text-sm font-medium uppercase tracking-[0.24em] text-[var(--accent)]">
              Repo slices
            </p>
            <div className="mt-4 grid gap-3 md:grid-cols-2">
              {repoSlices.map((slice) => (
                <article
                  key={slice.path}
                  className="rounded-2xl border border-[var(--border)] bg-white/75 p-4"
                >
                  <p className="font-[family-name:var(--font-display)] text-lg font-semibold">
                    {slice.path}
                  </p>
                  <p className="mt-2 text-sm leading-6 text-[var(--muted)]">
                    {slice.detail}
                  </p>
                </article>
              ))}
            </div>
          </section>

          <section className="rounded-[32px] border border-[var(--border)] bg-[var(--panel)] p-6 shadow-[0_18px_60px_rgba(44,32,12,0.08)] lg:p-8">
            <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
              <div>
                <p className="text-sm font-medium uppercase tracking-[0.24em] text-[var(--accent)]">
                  Workstreams
                </p>
                <h2 className="mt-2 font-[family-name:var(--font-display)] text-2xl font-semibold">
                  에이전트별 충돌 없는 분업
                </h2>
              </div>
              <p className="max-w-xl text-sm leading-6 text-[var(--muted)]">
                계약은 `packages/contracts`에 먼저 반영하고, 각 에이전트는 자기 패키지 경계 안에서만 작업합니다.
              </p>
            </div>

            <div className="mt-5 grid gap-4 xl:grid-cols-2">
              {workstreams.map((stream) => (
                <article
                  key={stream.key}
                  className="rounded-3xl border border-[var(--border)] bg-white/80 p-5"
                >
                  <div className="flex items-center justify-between gap-3">
                    <div>
                      <p className="font-[family-name:var(--font-display)] text-xl font-semibold">
                        {stream.owner}
                      </p>
                      <p className="text-sm text-[var(--muted)]">{stream.scope}</p>
                    </div>
                    <span className="rounded-full bg-[var(--accent-soft)] px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-[var(--accent)]">
                      {stream.key}
                    </span>
                  </div>
                  <ul className="mt-4 space-y-2 text-sm leading-6 text-[var(--ink)]">
                    {stream.deliverables.map((deliverable) => (
                      <li key={deliverable} className="rounded-2xl bg-[#f6f1e8] px-3 py-2">
                        {deliverable}
                      </li>
                    ))}
                  </ul>
                </article>
              ))}
            </div>
          </section>
        </div>
      </section>
    </main>
  );
}
