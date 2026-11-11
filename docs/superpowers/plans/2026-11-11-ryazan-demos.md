# Ryazan demo portfolio Implementation Plan

> **For agentic workers:** execute inline using superpowers:executing-plans; one independent final review.

**Goal:** three honest, distinct static demos and a portfolio, tested and published to GitHub Pages when authorized access is available.

**Architecture:** separate source folders, shared accessible primitives, deterministic Python copy into `portfolio-dist/`. No production dependencies, external fonts, forms, trackers or backend. Original SVG illustrations.

**Tech Stack:** HTML5, CSS3, vanilla JavaScript, Python standard library for packaging/static validation, installed Playwright CLI for browser QA.

**Spec:** user attachments `CODEX_DEMO_SITES_BRIEF_RYAZAN_v1.2.md` and `MASTER_PLAN_RYAZAN_WEBSITES_FREELANCE_v1.9.md` (local originals remain unchanged).

## Global Constraints

- Every page visibly carries «Демонстрационный проект. Не является сайтом действующей компании».
- Gallery captions: «Пример оформления, не реальная работа заказчика».
- No real contacts, company claims, testimonials, prices, personal data collection or requests.
- Only new demos and portfolio may be published; previous employer projects: external links only.
- Relative URLs must work under a GitHub project subpath.
- Check all seven pages at 360, 390, 768 and 1440 CSS px.

## Review Focus

1. Project subpaths: local href/src and fragment targets resolve after packaging.
2. Small screens and zoom: no horizontal overflow, nav can be dismissed and survives resizing.
3. Keyboard: dialog Escape, focus containment/restoration, gallery navigation and visible focus.
4. Safety: no submissions, storage, analytics, remote asset requests or secrets.
5. Publication evidence: workflow and real URLs only; Russian access requires separate owner check.

## Tasks

- [ ] 1. Create `scripts/validate.py` acceptance checks and browser scenarios; run on empty tree (expected failure).
- [ ] 2. Implement `shared/`, `demo-ventilation/`, `demo-furniture/` (four pages), `demo-autoservice/`, `portfolio-src/`. Distinct layouts, original SVG, menus, FAQ, dialogs, gallery, service picker. Add per-demo README/ASSETS/QA.
- [ ] 3. Implement `scripts/build.py`, package only website files, validate source and distribution, serve via HTTP and run browser matrix/interactions, inspect screenshots. Fix demonstrated defects.
- [ ] 4. Add `.github/workflows/deploy-pages.yml`, deploy docs, prior-work register and links status. Independent review, targeted security/quality checks. Publish to a new public repository with authorized `gh` when available; otherwise record `DEPLOY_BLOCKED_AUTH` and one required login step.
- [ ] 5. Record actual tests and deployment result; append confirmed results to a working copy of MASTER PLAN without rewriting history. Deliver files and portable archive.

## Execution ledger

- Preflight: workspace is an empty unborn Git repository; no tracked source, no remote. Work in place; isolate publication with explicit tracked-file allowlist and attachment ignore. No existing BagePC application touched.
- Authorization: publication explicitly authorized in brief. GitHub connector identifies Bage340, but exposes no repository creation/Pages API; `gh auth status` reports not logged in. Owner asked for native `gh auth login` while local work continues.
- Design calls: ventilation blue/ice technical schematic; furniture cream/umber editorial interiors; autoservice charcoal/lime circular wheel illustration; portfolio light editorial blue. System fonts, no third-party media.
