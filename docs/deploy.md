# Versioned deploy

The site is published one directory per version, with a `versions.json` and a
default alias, and a version selector that switches between them. This is the
mike layout; the version selector in Zensical's theme reads it natively.

## Model

| Context | URL | Driven by |
|---|---|---|
| Staging | `dyalog.github.io/documentation/<ver>/` | mike push to `gh-pages` |
| Production | `docs.dyalog.com/<ver>/` | Dyalog Jenkins, pulling from `gh-pages` |

`gh-pages` is the single source; production is a separate Jenkins step outside
this repository. A deploy here only ever writes `gh-pages`.

## Tooling

Zensical has no standalone versioning command, but the `squidfunk/mike` fork
builds with `zensical build` instead of `mkdocs build` and produces the
`gh-pages` layout. It is pinned in `tools/requirements-deploy.txt` (GitHub-only,
a bridge until Zensical ships native versioning).

Run from this repository, with the source monorepo checked out alongside it as
`../documentation` (that is where the pinned Zensical build stack lives during
the migration):

```
pip install -r ../documentation/tools/requirements-docs.txt   # Zensical + build stack
pip install -e tools/                                         # the caption extension (dyalog_caption)
pip install -r tools/requirements-deploy.txt                  # the mike fork
```

## Deploy

Run from inside the generated project, with `zensical` on PATH (the fork calls
it as a bare command):

```
cd zensical/
mike deploy --push --update-aliases 21.0 latest   # build 21.0, tag it latest
mike set-default --push latest                     # root redirects to latest
```

`mike deploy` sets `MIKE_DOCS_VERSION`, so Zensical prefixes `site_url`
(`https://docs.dyalog.com/`, set in `zensical.toml`) with the version, giving
`docs.dyalog.com/21.0/` canonicals. Internal links are relative, so the same
build also serves correctly under the staging path prefix.

## Prerequisites and notes

- `site_url` must be set in `zensical.toml` (it is, via the conversion script):
  version-prefixing only happens when it is set. Setting it also activates
  `navigation.instant`, so MathJax re-typesets on client-side navigation.
- Staging or test builds served from a different host (for example a personal
  GitHub Pages account) should override `site_url` to that host so canonicals
  match where the site is served.
- CI automation of this deploy is issue #30; this document is the manual
  runbook the CI encodes.
