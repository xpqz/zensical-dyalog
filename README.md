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

Content and build config are generated from the monorepo by `tools/convert.py` and committed
under `zensical/`. The build is stock Zensical plus one stylesheet
(`zensical/docs/documentation-assetsz/`); the house classes the MkDocs stylesheet styled are
rewritten into plain Markdown at conversion time (see `tools/transforms.py`), and
`docs/asset-switch-issues.md` records the design.

## Regenerating from the monorepo

With a checkout of `dyalog/documentation` as a sibling directory named `documentation`:

```
pip install -r tools/requirements-build.txt -r tools/requirements-dev.txt
pip install -e tools/
python tools/convert.py            # rewrites zensical/ (keeps the two asset directories)
python tools/check_flatten.py      # builds it and gates on known-issues.txt
```

`convert.py` refuses to run when a page in `tools/content/` (a hand-reworked replacement) no
longer matches the source page it was written against; re-merge and update the `.source-sha256`
sidecar. Each guide is mounted at the path mkdocs-monorepo-plugin gave it on the live site, its
slugified `site_name`: for the two .NET guides that is `net-interface-guide/` and
`net-framework-interface-guide/`, not their directory names.
