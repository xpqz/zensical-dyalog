# Dyalog v{{ version_majmin }}

Welcome to the documentation for Dyalog v21.0.

<!--!!! Info "Information"
    The documentation for Dyalog v21.0 is currently being developed and will not be finalised until nearer the release of Dyalog v21.0.-->

This documentation site is a new project, and we are continuing to add documents from the full documentation set (which is available at the [Dyalog v21.0 Documentation Centre](https://www.dyalog.com/documentation_210.htm)).

!!! tip "Hints and Recommendations"
    New to APL? See [Getting started](https://www.dyalog.com/getting-started.htm).

## Help us improve this documentation

If you discover an error on this site or would like to request an enhancement, [email us](mailto:docs@dyalog.com) your error report or enhancement request.

Alternatively, if you have a GitHub account, you can click the appropriate button below. We also welcome [direct content contributions](https://github.com/Dyalog/documentation/blob/main/CONTRIBUTE.md).

<div class="grid cards" markdown>

-   ![](documentation-assetsz/images/icon-gitissue-content-error.svg){ style="height:2em" } **Content error**

    ---

    For example: typos, broken links, inaccurate information, example doesn't work, images are too small

    [Report a content error](https://github.com/Dyalog/documentation/issues/new?assignees=FionaDyalog&labels=for-triage&template=content_error.md&title=)

-   ![](documentation-assetsz/images/icon-gitissue-technical-error.svg){ style="height:2em" } **Technical error**

    ---

    For example: content not wrapping correctly, APL font not displaying, images failing with screen reader

    [Report a technical error](https://github.com/Dyalog/documentation/issues/new?assignees=FionaDyalog&labels=for-triage&template=technical_error.md&title=)

-   ![](documentation-assetsz/images/icon-gitissue-content-enhancement.svg){ style="height:2em" } **Content enhancement**

    ---

    For example: additional examples for a primitive function, more screenshots of a process

    [Suggest a content enhancement](https://github.com/Dyalog/documentation/issues/new?assignees=FionaDyalog&labels=for-triage&template=content_enhancement.md&title=)

-   ![](documentation-assetsz/images/icon-gitissue-technical-enhancement.svg){ style="height:2em" } **Technical enhancement**

    ---

    For example: enhance search features, add ability to "bookmark" pages

    [Suggest a technical enhancement](https://github.com/Dyalog/documentation/issues/new?assignees=FionaDyalog&labels=for-triage&template=technical_enhancement.md&title=)

</div>

<script>
[...document.querySelectorAll(".grid a[href*=error]")].forEach(e=>
  fetch(
    e.href.replace(
      /github.*template=/,"raw.githubusercontent.com/Dyalog/documentation/refs/heads/main/.github/ISSUE_TEMPLATE/"
    ).replace(/&.*/,"")
  ).then(d=>d.text()).then(
    d=>e.href+="&body="+encodeURIComponent(
      d.slice(d.indexOf("*")).replace(/^.*\w+:\w+/m,document.querySelector(".copy").innerText)
    )
  )
)
</script>
