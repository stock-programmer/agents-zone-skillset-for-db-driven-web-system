# Story: Developer Story Creation Command

Transform PRD requirements and architecture into **hyper-detailed developer stories** that give tester and coder subagents EVERYTHING they need.

## Your Mission

Create stories that serve as the **single source of truth** for tester/coder. They will ONLY have the story file - no additional context gathering.

## Critical Principles

**Story = Ultimate Context Engine**:

- Story file is the ONLY context tester/coder will have
- They will NOT search codebase or read other docs
- ALL technical details must be IN the story
- Include specific file paths, patterns, library versions

**Prevent LLM Mistakes**:

- Wrong libraries → Exact library names/imports
- Wrong locations → Exact file paths
- Reinventing → List existing utilities to reuse
- Breaking patterns → Provide pattern REFERENCES (not full code)
- Vague implementations → Interface signatures, struct fields

**Token Efficient**: Every sentence guides implementation. No fluff, scannable structure.

## Code Policy (IMPORTANT)

**Stories define WHAT to build, not HOW.**

### ✅ DO Include

- Pattern references (Go): `See internal/handlers/users.go:25-45`
- Pattern references (Python): `See app/api/handlers/users.py:25-45`
- Interface signatures (Go): `GetUser(ctx, id) (*User, error)`
- Interface signatures (Python): `def get_user(user_id: int) -> User | None`
- Struct field lists (Go): `User: ID, Name, Email, CreatedAt`
- Data model fields (Python): `User: id, name, email, created_at`
- Utility one-liners (Go): `lo.ToPtr(value)`
- Utility one-liners (Python): `value if value is not None else default`
- Anti-patterns (Go): `❌ Don't use fmt.Println`
- Anti-patterns (Python): `❌ Don't use print`

### ❌ DO NOT Include

- Full function implementations (coder should implement)
- Complete test files (tester should write)
- Entire struct definitions (field list sufficient)
- Multi-line code blocks >10 lines (too detailed, becomes stale)

**Why**: Stories with full code = copy-paste exercises. Full code drifts. Stories should guide, not dictate.

## Workflow

### Phase 1: Deep Context Gathering (CRITICAL)

**Step 1.1: Read Source Documents**

1. PRD.md - Requirements, AC, MVP scope
2. ARCHITECTURE.md - Technical design, patterns, structure
3. go.mod/pyproject.toml/package.json - Exact library versions
4. Existing handlers/services - Code patterns
5. Existing tests - Test patterns
6. Previous stories - Learnings, patterns

**Step 1.2: Extract Technical Details** (MUST INCLUDE):

```markdown
## Technical Context

### Exact Versions (from go.mod/pyproject.toml)

- Go: 1.21, Gin: v1.9.1, testify: v1.8.4
- Python: 3.11, FastAPI: 0.110.0, pytest: 8.1.1
- Vue: 3.4, Vite: 5.x, Vitest: 1.x, Playwright: 1.x, Pinia: 2.x, Vue Router: 4.x

### File Paths (from ARCHITECTURE.md)

- Handler: `internal/api/handlers/[name].go`
- Service: `internal/services/[name].go`
- Tests: `test/integration/[name]_test.go`
- Handler (Python): `app/api/handlers/[name].py`
- Service (Python): `app/services/[name].py`
- Tests (Python): `tests/integration/test_[name].py`
- Component (Vue): `src/components/[Name].vue`
- View (Vue): `src/views/[Name]View.vue`
- Composable (Vue): `src/composables/use[Name].ts`
- Store (Vue): `src/stores/[name].ts`
- Router (Vue): `src/router/index.ts`
- Unit Tests (Vue): `tests/unit/components/[Name].spec.ts`
- E2E Tests: `tests/e2e/[feature].e2e.ts`

### Existing Utilities to Reuse

- Pointer: `lo.ToPtr()` from samber/lo
- Error: `fmt.Errorf("context: %w", err)`
- HTTP errors: `gin.AbortWithStatusJSON()`
- Optional handling: `value if value is not None else default`
- Error: `raise RuntimeError(f"context: {err}") from err`
- HTTP errors: `raise HTTPException(status_code=..., detail=...)`
- `useRouter()` / `useRoute()` — Vue Router 导航
- `defineStore()` — Pinia 状态管理
- VueUse composables — `useLocalStorage`, `useFetch` 等
- UI 组件库组件 — `ElButton`, `ElForm` 等 (或项目使用的组件库)

### Pattern References (paths, NOT full code)

- Handler: See `internal/api/handlers/users.go:25-45`
- Service: See `internal/services/users.go:30-50`
- Test: See `test/integration/users_test.go:15-40`
- Handler (Python): See `app/api/handlers/users.py:25-45`
- Service (Python): See `app/services/users.py:30-50`
- Test (Python): See `tests/integration/test_users.py:15-40`
- Component (Vue): See `src/components/ExistingComponent.vue:10-30`
- Composable (Vue): See `src/composables/useExisting.ts:5-20`
- Unit Test (Vue): See `tests/unit/components/Existing.spec.ts:10-40`
- E2E Test: See `tests/e2e/existing-feature.e2e.ts:5-30`
```

**Step 1.3: Identify Anti-Patterns**:

```markdown
### Anti-Patterns (DO NOT DO)

- ❌ Custom pointer helpers - use `lo.ToPtr()`
- ❌ Hand-written API structs - use `internal/api/gen/`
- ❌ Direct SQL - use GORM repository
- ❌ fmt.Println - use `zap.Logger`
- ❌ Hand-written API schemas - use shared Pydantic models in `app/schemas/`
- ❌ Direct SQL string concatenation - use SQLAlchemy repository
- ❌ print - use `logging.getLogger(__name__)`
- ❌ 直接操作 DOM (`document.querySelector`) — 用 `ref`/`reactive`
- ❌ 在组件中直接 fetch — 抽取到 composable 或 store action
- ❌ 全局 mutable state — 用 Pinia store
- ❌ 在 `<script setup>` 中写大量逻辑 — 抽取到 composable
```

### Phase 2: Test Scenario Planning

**Step 2.1: Analyze Feature Complexity**

**Simple** (use LIGHT scenarios):

- Basic CRUD only
- 1-3 straightforward AC
- No state transitions/workflows
- No external integrations
- No complex business logic

**Complex** (use FULL scenarios):

- Business logic (calculations, validations)
- 4+ AC
- Multi-step flows (OAuth, CIBA, payment)
- State machines (consent lifecycle)
- External integrations (external APIs)
- Financial/security/time-sensitive operations

**Step 2.2: Design Test Scenarios**

**Simple Features** (Light Template):

```markdown
## Test Scenarios

**Strategy**: Integration tests following standard CRUD pattern
**Coverage**: AC tests + basic error cases (404, 400, 500)
**Pattern**: See `test/integration_test/[similar]_test.go` (Go) or `tests/integration/test_[similar].py` (Python)
```

**Complex Features** (Full Template):

```markdown
## Test Scenarios

### Test Strategy

**Coverage**: [Unit + Integration | Integration-only]
**Complexity**: [Simple CRUD | Moderate | Complex Multi-step]

### Test Layer Breakdown

| Layer       | Scope             | Justification     |
| ----------- | ----------------- | ----------------- |
| Unit        | [Isolated logic]  | Fast feedback     |
| Integration | [Endpoints/flows] | Real dependencies |

### Boundary Analysis

**Input**: [field: min, max, zero, null, empty]
**State**: [transitions: valid/invalid]
**Temporal**: [expiration, timing issues]

### Edge Cases

- Missing/invalid fields (AC#)
- External API failures (timeout, 500)
- Token expiration, invalid transitions
- [Feature-specific edge cases]

### Risk Areas

**High**: [Component/flow - why risky]
**Medium**: [Standard operations]
**Low**: [Read-only, no logic]

### Pattern References

- Integration: `test/integration_test/[example]_test.go`
- Unit: `internal/[package]/[example]_test.go`
- Integration (Python): `tests/integration/test_[example].py`
- Unit (Python): `tests/unit/test_[example].py`
- Table-driven for boundaries
```

**Vue Frontend Features** (Frontend Template):

```markdown
## Test Scenarios (Vue Frontend)

### Test Strategy
**Coverage**: Component unit (Vitest) + E2E (Playwright)

### Component Tests
- 渲染：props 传入后 DOM 正确展示
- 交互：click/input/submit 触发正确行为
- 状态：Pinia store 变更反映到 UI
- 异步：API 加载中显示 loading，完成后显示数据，失败显示错误

### E2E Tests
- 用户完整流程：登录 → 操作 → 验证结果
- 页面导航：路由跳转正确
- 表单：填写 → 提交 → 反馈

### Pattern References
- Component Test: `tests/unit/components/[Example].spec.ts`
- Composable Test: `tests/unit/composables/[useExample].spec.ts`
- E2E Test: `tests/e2e/[example-feature].e2e.ts`
```

### Phase 3: Story Scope Definition

**Step 3.1: Clarify with User**

1. Which feature/epic? (Specific PRD section)
2. Story size? (1-3 days completable)
3. Dependencies? (Prerequisite stories)

**Step 3.2: Break Down if Needed**
If scope too large, propose multiple stories with clear boundaries.

### Phase 4: Write Story Document

**Story Structure**:

#### Section 1: Header

```markdown
# Story: [Epic.Story] [Title]

**Status**: ready-for-dev
**Epic**: [Epic name]
**Depends On**: [Previous stories or "None"]
```

#### Section 2: User Story

```markdown
As a [role], I want [action], so that [benefit].
```

#### Section 3: Acceptance Criteria (BDD - for Tester)

```markdown
### AC1: [Happy Path]

**Given** [precondition] **When** [action] **Then** [expected result]

### AC2: [Error Case]

**Given** [error condition] **When** [action] **Then** [error response + status]
```

**AC Writing Rule — Side Effects in "Then"**:
When the feature produces side effects (disk write, DB mutation, cache update, message send), the **Then** clause MUST include the system-level outcome, not just the user-visible response.

- ❌ `Then 文件上传成功，列表显示新文件` (only UI outcome — tester will only check API response)
- ✅ `Then 文件上传成功，文件写入 uploads/ 目录且内容与原始文件一致，DB 记录创建` (includes side effect)
- ❌ `Then 文件正常下载到本地` (vague — tester will check status 200 only)
- ✅ `Then 返回的文件流内容与上传时的原始文件内容一致` (verifiable side effect)

**AC Writing Rule — Durable Database State**:
When the feature writes to the database, the **Then** clause MUST describe durable state after the operation completes, not just visibility inside the current session/transaction.

- ❌ `Then 返回 success 且当前 session 内可查到数据`
- ✅ `Then 操作结束后，使用新的 session / 新连接仍可查询到新写入的记录`

#### Section 4: Technical Context (for Coder - CRITICAL)

```markdown
## Technical Context

### Tech Stack & Versions

[From go.mod/pyproject.toml/package.json]

### File Locations

[Exact paths]

### Utilities to Reuse

[One-liners: `lo.ToPtr(value)` (Go), `value if value is not None else default` (Python)]

### Pattern References

[Paths + lines: `See internal/handlers/users.go:25-45` (Go), `See app/api/handlers/users.py:25-45` (Python)]

### Interface Signatures (if new)

[Method signatures: `GetUser(ctx, id) (*User, error)` (Go), `def get_user(user_id: int) -> User | None` (Python)]

### Struct Fields (if new)

[Field lists: `User: ID, Name, Email`]

### Anti-Patterns

[Specific things NOT to do + alternatives]
```

#### Section 5: Tasks (for Coder)

```markdown
### Task 1: [Name] (AC: #1)

- [ ] Create `path/to/file.go`
- [ ] Create `path/to/file.py`
- [ ] Implement [function]
- [ ] Follow pattern from `path/to/reference.go`
- [ ] Follow pattern from `path/to/reference.py`
```

#### Section 6: Test Requirements (for Tester)

```markdown
### Integration Tests (REQUIRED)

Location: `test/integration/[name]_test.go`
Location (Python): `tests/integration/test_[name].py`

| Test Case  | AC  | Input      | Expected   |
| ---------- | --- | ---------- | ---------- |
| Happy path | #1  | valid      | 200 + data |
| Not found  | #2  | invalid ID | 404        |

### Vue Component Tests

Location: `tests/unit/components/[Name].spec.ts`

### E2E Tests

Location: `tests/e2e/[feature].e2e.ts`

### Mock Requirements

- Mock [external service]
- Use fixtures from `test/fixtures/`
```

#### Section 7: Definition of Done

```markdown
- [ ] All AC have passing tests
- [ ] No regressions
- [ ] No TODO/FIXME in production
- [ ] Code follows patterns
- [ ] Coverage >80%
```

### Phase 5: Validation

**Content Checks**:

- [ ] All AC testable (Given-When-Then)
- [ ] AC "Then" clauses include side effects, not just API responses
- [ ] Side-Effect Verification table filled for all state-changing operations
- [ ] DB-writing stories include Transaction Ownership and Durable Persistence Verification
- [ ] If the story writes database state, the story text explicitly contains `fresh session` or `new connection`; otherwise the story is invalid
- [ ] Mock Policy: core side effects (disk, DB, cache) NOT listed as mocked
- [ ] File paths REAL (from architecture)
- [ ] Library versions REAL (from go.mod/pyproject.toml)
- [ ] Anti-patterns specific to codebase
- [ ] Tasks map to AC
- [ ] Test requirements cover all AC

**Code Policy Checks**:

- [ ] NO full function implementations (use references)
- [ ] NO complete test code (use requirements table)
- [ ] NO code blocks >10 lines
- [ ] Pattern references to REAL files + lines
- [ ] Interface signatures concise (one line/method)
- [ ] Struct definitions field lists only

### Phase 6: Save Story

**CRITICAL: Save story to dev branch, NOT worktree**

When using git worktrees:

```bash
# ✅ CORRECT: Save story to dev branch
cd [project-root]/[project]-dev-branch
# Story file saved here in plans/

# Then create worktree for implementation
git worktree add [project-root]/[project]-S${NUM}-feature -b S${NUM}-feature
cd [project-root]/[project]-S${NUM}-feature
# Implement code here - story already in dev ✅
```

**Why this matters**: Story files created in worktree branches are lost when worktrees are deleted. Story files must survive in the main dev branch for documentation continuity.

Save to: `plans/S${NUM}-[title].md` (or project-specific plans directory)

## Story Template

```markdown
# Story: [Epic.Story] [Title]

**Status**: ready-for-dev
**Epic**: [Epic name]
**Depends On**: [Dependencies]

---

## User Story

As a [role], I want [action], so that [benefit].

---

## Acceptance Criteria

### AC1: [Name]

**Given** [precondition] **When** [action] **Then** [result]

### AC2: [Name]

**Given** [precondition] **When** [action] **Then** [result]

---

## Technical Context

### Tech Stack & Versions

- Language: [version], Framework: [version], Database: [version]

### File Locations

[Exact paths where new files go]

### Utilities to Reuse

- `lo.ToPtr(value)` - Pointers (samber/lo)
- `fmt.Errorf("context: %w", err)` - Error wrapping
- `logger.Info("msg", zap.String("k", v))` - Logging (uber/zap)
- `value if value is not None else default` - Optional handling
- `raise RuntimeError(f"context: {err}") from err` - Error wrapping
- `logger = logging.getLogger(__name__)` - Logging (`logging`)

### Pattern References

- Handler: `internal/api/handlers/[existing].go:[lines]`
- Service: `internal/services/[existing].go:[lines]`
- Test: `test/integration/[existing]_test.go:[lines]`
- Handler (Python): `app/api/handlers/[existing].py:[lines]`
- Service (Python): `app/services/[existing].py:[lines]`
- Test (Python): `tests/integration/test_[existing].py:[lines]`
- Component (Vue): `src/components/[Existing].vue:[lines]`
- Composable (Vue): `src/composables/use[Existing].ts:[lines]`
- Unit Test (Vue): `tests/unit/components/[Existing].spec.ts:[lines]`
- E2E Test: `tests/e2e/[existing-feature].e2e.ts:[lines]`

### Anti-Patterns

- ❌ [Thing not to do] → Do [this] instead
- ❌ 直接操作 DOM (`document.querySelector`) → 用 `ref`/`reactive`
- ❌ 在组件中直接 fetch → 抽取到 composable 或 store action
- ❌ 全局 mutable state → 用 Pinia store
- ❌ 在 `<script setup>` 中写大量逻辑 → 抽取到 composable

---

## Implementation Guidance

### [Component] Fields (if new struct)

FieldName1, FieldName2, FieldName3 (types if non-obvious)

### Interface Signatures (if new interface)

- `MethodName(param1, param2) (ReturnType, error)`
- `OtherMethod(ctx, id) (*Result, error)`
- `def method_name(param1: str, param2: int) -> ReturnType:`
- `def other_method(user_id: int) -> Result | None:`

### Key Logic (prose, not code)

- [Step 1], [Step 2], [Edge case handling]

### Transaction Ownership (for DB-writing features)

- `transaction_owner`: which function/module/process is responsible for the final commit
- `rollback_scope`: what unit rolls back on failure (row/file/request/job/batch)
- `nested_scope`: if savepoints or nested transactions are used, what they isolate and what they do not durably commit
- `durability_boundary`: when data must become visible to a fresh session / new process

---

## Tasks

### Task 1: [Name] (AC: #1, #2)

- [ ] [Subtask]
      **Files**: `path/to/file.go`
      **Pattern**: `path/to/reference.go`
- [ ] [Subtask]
      **Files**: `path/to/file.py`
      **Pattern**: `path/to/reference.py`

### Task 2: [Name] (AC: #3)

- [ ] [Subtask]
      **Depends On**: Task 1

---

## Test Scenarios

[Content from Phase 2 - light or full template based on complexity]

---

## Test Requirements

### Integration Tests

**Location**: `test/integration/[name]_test.go`
**Location (Python)**: `tests/integration/test_[name].py`

| Test Case | AC  | Input   | Expected |
| --------- | --- | ------- | -------- |
| [case]    | #1  | [input] | [output] |

### Vue Component Tests

**Location**: `tests/unit/components/[Name].spec.ts`

### E2E Tests

**Location**: `tests/e2e/[feature].e2e.ts`

### Mocks Required

- [What to mock and how]

### Durable Persistence Verification (REQUIRED for DB writes)

If the feature writes database state, the story MUST include at least one verification step that proves durability beyond the writer session.

- Verify data from a fresh session or new connection after the operation completes
- For CLI/job/batch/script entrypoints, prefer running the entrypoint, letting the process/session end, then querying with a new connection
- If savepoints or nested transactions are used, verify that the final transaction owner makes data durable

### Side-Effect Verification (CRITICAL)

List all operations where the system changes external state beyond the API response.
Tester MUST write assertions for each. These MUST NOT be mocked away.

| Side Effect                   | Verification Method                        | Example Assertion                    |
| ----------------------------- | ------------------------------------------ | ------------------------------------ |
| [e.g. File written to disk]   | [e.g. Check file exists + content matches] | `assert os.path.exists(path)`        |
| [e.g. DB record updated]      | [e.g. Query DB after operation]            | `assert record.status == "approved"` |
| [e.g. File deleted from disk] | [e.g. Check file no longer exists]         | `assert not os.path.exists(path)`    |
| DOM 元素出现                  | 查找元素并验证存在                          | `expect(wrapper.find('.error-msg').text()).toBe('Invalid')` |
| 路由跳转                      | 检查 router.currentRoute                   | `expect(router.currentRoute.value.path).toBe('/dashboard')` |
| Store 状态变更                | 读取 store 属性                             | `expect(store.items).toHaveLength(3)` |
| localStorage 写入             | 读取 localStorage                           | `expect(localStorage.getItem('token')).toBeTruthy()` |
| API 请求发送                  | MSW handler 拦截验证                        | `expect(apiCalls).toContainEqual({method: 'POST', url: '/api/users'})` |

**Mock Policy**:

- ✅ Mock: External APIs, third-party services, email/SMS senders
- ❌ NEVER mock: Disk I/O, database writes, cache writes, queue publishing — these are core side effects that MUST be tested with real operations (use tmp_path, test DB, etc.)

**Frontend Mock Policy**:
- ✅ Mock: Backend API (MSW intercept)、第三方 SDK
- ❌ NEVER mock: Vue Router navigation、Pinia store actions、DOM rendering、浏览器 API (在 E2E 中)

---

## Definition of Done

- [ ] All AC have passing tests
- [ ] No regressions
- [ ] No TODO/FIXME
- [ ] Follows patterns
- [ ] Coverage >80%
```

## Integration with TDD Workflow

```
/story creates story.md
       ↓
tester reads story.md → writes failing tests
       ↓
coder reads story.md + tests → implements code
       ↓
Done when Definition of Done met
```

**Tester and coder will ONLY read the story file. They trust it has everything.**

## After Completion

**Immediate Actions**:

1. **Verify story file committed to dev branch**:
   ```bash
   cd [project-root]/[project]-dev-branch
   git add plans/S${NUM}*.md
   git commit -m "docs: Add S${NUM} story"
   git push origin dev
   ```
2. **Verify file exists** before proceeding:
   ```bash
   ls -lh plans/S${NUM}*.md
   # Must show file - if not found, story will be lost!
   ```

Update `PROGRESS.md`:

1. Mark [x] Story phase complete
2. Add story info to Current Work section
3. Note story file path for validation
