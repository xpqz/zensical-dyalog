# Zensical asset switch — change record and remaining decisions

Ground rules (agreed 2026-09-04): every deviation from stock Zensical must
justify itself, because we maintain it across Zensical updates. Fonts, colours,
and logo are exempt. Where a house class needed styling, the content was
changed so the class disappears. Accessibility must not regress. All changes
are uncommitted in the working tree.

## Config (zensical/zensical.toml)

- Stark-style near-default config: classic variant, custom light/dark
  palettes, orange wordmark + cube favicon, `font = false` (self-hosted),
  single stylesheet `documentation-assetsz/css/dyalog.css`, Zensical copyright
  with the copy-build-info button.
- `plugins = [search, macros]` — privacy and minify are MkDocs plugins
  Zensical does not implement.
- Prev/next footer bar removed by dropping the opt-in `navigation.footer`
  feature. `content.code.copy` added (feature flag, zero maintenance).
- MathJax deleted entirely (extra_javascript, arithmatex extension,
  docs/javascripts/mathjax.js): a rendered-site scan found zero `arithmatex`
  output across ~3,050 pages. This also disposes of the privacy-plugin
  question — no external requests remain.

## dyalog.css (the whole maintained style delta beyond fonts/palette)

- `--md-code-font: "APL387", monospace` token: all code is APL-first,
  matching the old site (which put the APL face on every code element).
  Consequence: the old APL-vs-non-APL font distinction (`nonAPL`/`other`
  fence languages, `<code class="language-nonAPL">` in 56 files) is inert but
  harmless; restoring it would be one rule + JetBrains Mono @font-faces
  (already shipped in documentation-assetsz).
- `pre > code.language-apl { display: block; line-height: 1.2 }` — boxing.
  1.2 matches the old rule; display:block stops the pre's taller line-height
  strut from spacing the lines. Hairline gaps remain between box glyphs at
  1.2 (they did on the old site too); line-height 1.0 closes them further if
  ever wanted.
- `.apl` class (APL font for non-code elements) — used by two raw-HTML glyph
  tables (see below).
- Copyright build-stamp button styling (keyboard-accessible stamp) and three
  header cosmetics (logo size needed for the wordmark; box-shadow/padding and
  search-button background are taste — deletable if we go stricter).

## Content transforms applied (3,019 files changed)

1. **Title banners removed** (3,009 h1s): `{: .heading}` + spans stripped.
   - 1,694 name-only → plain `# Name`.
   - 615 name+command → `# Name` with the calling syntax in an ```apl block
     directly below the h1 (`<br/>` → two lines; escapes/entities unescaped).
   - 700 name+right (Event/Method numbers) → plain line below the h1.
   - Nested/suffixed variants → inline code in the h1 (e.g. `# ⎕NA under
     UNIX`). One extra attr preserved (`negate.md` keeps `{: #negative}`).
   Cleaner h1s for search results and screen readers.
2. **Example headings** (700): `<h2-5 class="example">…</h*>` → real `##`
   headings. They now appear in "On this page" and get anchors — noisy on
   Example-heavy pages (e.g. ⎕JSON); if unwanted, the alternative is bold
   text instead of headings. Five `<p class="example">` labels and one broken
   `<h* class="example">` → `**Example**`.
3. **Admonitions** normalised to types the theme ships: `Hint` → `tip` (15),
   `Legacy` → `note` (12), `windows|unix|linux|macos` → `info` (21 — the
   titles already name the OS). `Info`/`Warning` work as-is (the extension
   lowercases). The front page's two are covered.
4. **Front page cards** rebuilt on the stock grid-cards pattern (icon + bold
   title, divider, description, distinct link text per card) instead of
   whole cards wrapped in `.md-button` — this was the "boxes look bad". The
   issue-prefill script still works. The stale "add a dark mode option"
   example text was dropped (dark mode exists now).
5. **`.shaded` default markers** (37 cells, 10 files): shading replaced by a
   literal `` `value` (default)`` — the semantics are now in text, not
   colour (an accessibility win). The fchk prose "highlighted thus…" removed
   as redundant.
6. **binding-strength.md**: `flex-between`/`text-left`/`text-right` cells
   collapsed to `strength: result` text; dead `table-bordered`/`no-border`
   classes removed (a class-less table gets the theme's table styling).
7. **Toolbar sprite** (2 tracer pages): all 24 icon references sliced from
   trace-theme-sprite-16.png into `windows-ui-guide/img/tbt-*.png` as real
   images with alt text (the spans had none). Named from the row's Name
   column, or the Description for the 7 nameless rows.
8. **Glyph tables**: `class="Dyalog"` → `class="apl"` in
   language-elements.md and format-datetime.md (raw-HTML tables keeping the
   compact grid).
9. **gitissue icons** copied into documentation-assetsz/images and the front
   page repointed, so content no longer needs the old submodule.

## Verified

- Build: exactly the 20 known-issues.txt entries (9 line numbers updated in
  the baseline for the inserted syntax blocks — content unchanged).
- Screenshots (light + dark): front page cards, reference pages (Depth,
  ⎕JSON, ⎕FCHK), binding-strength table, tracer toolbar tables, glyph index,
  list-nested admonition, box-drawing output.

## Remaining / structural

- The old `documentation-assets` submodule is no longer referenced by
  content or config. Dropping it (git rm + .gitmodules + the CI `.git`-strip
  step from #44) is a separate structural change. The sprite source lives
  there; the sliced PNGs are now content-owned.
- convert.py regenerates this repo from the monorepo (ported 2026-09-16):
  the transforms live in tools/transforms.py, the toml header is
  tools/zensical.toml.template, and the hand-reworked front page and the
  sliced toolbar PNGs are a content overlay in tools/content/. Against the
  July source the regenerated tree matches the tree described above except
  where the port deliberately goes further: `<h1 class="example">` is
  demoted to `##` rather than kept as a second h1 (7 pages); a classifier in
  the command position (`Event 525`, `Method 838`) becomes a plain line, not
  an ```apl block (13 pages); the remaining `{ .shaded }` cells and
  "highlighted thus" legends are converted too; the standalone breakpoint
  icon reuses tbt-reset.png (the slices were byte-identical). Against the
  September source it also handles what the monorepo changed since July:
  Markdown titles with bare spans and `{{key}}` (the key macro becomes a
  relative "Key to notation" text link under the syntax block, since its
  white SVG icon is invisible off the old banner), caption ids
  (`Table: ... { #id }`) and empty `[](#id)` table references, and the two
  .NET guides mounted at their live-site aliases.
- 151 pages use adjacent input/output code blocks the old CSS merged; the
  default two-block rendering is accepted (honest structure, copy button per
  block). Revisit only if it reads badly.
- requirements-build.txt pins zensical==0.0.48; validated here on 0.0.57.
  `pip install -e tools/` fails on Python 3.10 (dyalog-caption wants ≥3.11);
  build with `PYTHONPATH=tools`.
- Versioned-deploy banner (overrides/main.html + mike provider) unverified
  locally.
- Light-mode logo contrast (2.87:1) is the documented identity-over-WCAG
  choice; dark mode ≈5.7:1.
