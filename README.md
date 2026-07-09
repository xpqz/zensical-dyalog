# zensical-dyalog

The Dyalog user documentation as a single flattened [Zensical](https://zensical.org) project,
ported from the MkDocs monorepo at [dyalog/documentation](https://github.com/dyalog/documentation).

The monorepo split existed only to keep author build times tolerable across ~3,050 markdown
files. Zensical's differential builds remove that constraint, so the 14 sub-projects are
flattened into one project here. Every public URL from the monorepo is preserved, so existing
links keep resolving.

This repository is generated out-of-place from the monorepo source by a conversion script
(retained under tooling until cutover) and becomes the authoring home once Zensical reaches
parity. The phased migration is described in
[docs/plans/zensical-port-plan.md](docs/plans/zensical-port-plan.md).

## Status

Bootstrapping. Content and build config are populated by the conversion script during Phase 3
of the plan. Until then this repository holds the plan and this README.
