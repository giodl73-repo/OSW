# OSW: project messaging and navigation

Date: 2026-11-11

Status: implemented in the local checkout; not deployed

Source baseline: `19148702de6433253dbf412a0a28c0cb4f8e409e`

Review: [eight-role review](../signals/roles/check/project-messaging-and-navigation-roles-check-2026-11-11.md)

## The problem to solve

OSW has grown into a substantial body of work, but its entrances describe
different projects. The README presents a large directory. Atlas emphasizes
fluid geography and heat. Almanac emphasizes motion records. Column emphasizes
vertical addresses. Exchange emphasizes research stages. Their headers offer
different destinations, and several OSW home links return to a Markdown file.

A visitor should understand the whole project, recognize its major areas,
and move between them. Focus means organizing the breadth into a coherent
whole. The next work is editorial and navigational, using what already exists.

The work covers the whole existing atlas. Examples support its major areas;
none becomes a required journey or stands in for the project.

## Which gaps this work fills

| Gap from the initial assessment | This plan's response | What remains after planning |
|---|---|---|
| Unclear overall identity | One headline, one explanation, and three recognizable entrances. | Apply the agreed message to the site and README. |
| Fragmented navigation | Consistent global links, local orientation, and a home for every major collection. | Implement and inspect the navigation across existing pages. |
| Too much competing material | Put the main subjects first; keep tools, guides, history, and methods accessible through supporting links. | Edit the entrances and relocate lengthy directory/history copy without losing useful material. |
| Conflicting status and documentation | Align the visitor-facing availability/preview descriptions on the pages touched by this change. | Correct visible contradictions; broader historical record cleanup can follow separately. |
| Unproven originality | Describe what OSW offers without claiming to be the first or scientifically unique. | A comparative originality assessment remains separate and is not a prerequisite. |
| Scientific validation and maintenance complexity | Preserve current scientific qualifications and reuse the existing implementation. | Independent scientific review and wider technical simplification remain separate work. |

The first four rows define the immediate editorial scope. This plan does not
resolve the final two by changing words. No new evidence infrastructure, case
study, data acquisition, or scientific validation program is needed for this work.

## One project, one explanation

**Name:** Ocean States of the World

**Short name:** OSW / The Ocean States

**Descriptor:** A fluid atlas of the world ocean.

The descriptor identifies the kind of project. The headline invites exploration;
the sentence beneath it explains what people can do. Evidence and methods explain
why a particular view can be trusted, alongside that view or through its sources.
They do not compete with the project message in the opening.

Agreed opening copy:

> **Discover the world within the ocean.**
>
> Explore its places, follow its currents, and see how it changes.

Explain the name in the supporting About copy, linked from the introduction:

> “Ocean states” is our atlas metaphor for the ocean's geography. Reference
> regions help us locate things; currents, water masses, and events can overlap
> those regions and change with depth and time.

The metaphor must not imply political territory, fixed physical compartments,
or a newly established scientific classification. Keep scientific scope beside
the relevant view. Put full provenance and methods one step deeper, where readers
can inspect them without making that machinery the main story.

## Three ways in

Use the same three labels on the homepage and in global navigation. They organize
existing work; they are not new applications or scientific categories.

| Area | Question | Card text | Starting destination |
|---|---|---|---|
| **Explore the ocean** | What is there? | Maps, regions, and depths. | [Atlas](../atlas/index.html) |
| **Follow the currents** | How does it move? | Currents, eddies, and connections. | [Motion almanac](../almanac/index.html) |
| **See what's changing** | How does it change? | Temperature, heat, and events. | [Existing event explorer](../event/index.html), with a revised area introduction |

All three entrances have equal navigational standing. Visitors can begin anywhere;
there is no prescribed sequence and no featured case that stands in for OSW.
The labels are ways to browse, not rigid content silos: a depth view can connect
to heat, and a current can connect to the region it crosses. Give each surface
one primary home and use contextual links for those connections.

“See what's changing” covers dated views, seasonal patterns, and events. It does
not promise a live feed, a forecast, or proof of a long-term trend; identify the
actual time period and type of comparison on arrival.

Use **Learn more** as a secondary entry to the [field guides](../guides/README.md),
with **About OSW** and **Sources & research** in supporting/footer navigation.
Keep explanations alongside what people explore; learning is part of all three
entrances, rather than a fourth department. Methods, downloads, citation, status,
history, and experimental work remain accessible through the supporting links.

## Give every existing surface a recognizable home

| Existing surface or collection | Primary home | Presentation decision |
|---|---|---|
| Atlas and province maps | Explore the ocean | Main geographic overview; distinguish reference regions and physical overlays. |
| Column and depth comparisons | Explore the ocean | Label its entry **Ocean depths**; preserve “Ocean Column” as a descriptive subtitle if useful. |
| Neighbors and bathymetric shape | Explore the ocean | Keep near regions/depths; a shared edge is not a measured flow. |
| Almanac, current atlas, object pages, seasons, dated-current maps | Follow the currents | Organize as views of motion; explain the difference between overview, named-feature detail, and dated views. |
| Query and coverage dashboard | Follow the currents, secondary tools | Keep available under **Search & compare** and **Coverage**; do not make technical tools the first explanation of OSW. |
| Event explorer and temperature/anomaly/depth views | See what's changing | Existing examples support a broad area introduction; identify temperature, anomaly, heat storage, and transport accurately. |
| Exchange Observatory | See what's changing | Describe its contents and exchange comparisons in ordinary language; cross-link back to the selected region under Explore the ocean. |
| HEATMASS and OCEANREALMS | See what's changing, linked from Learn more | Use descriptive link text such as **Heat storage and pathways**; retain the existing titles within the documents. |
| Guide chapters and classification | Learn more | Make topics discoverable by readable names and questions. |
| Projection laboratory | Sources & research: Experiments | Retain as cartographic work; link from Explore the ocean where helpful. |
| OCEANBELTS / planetary comparisons | Learn more: Further explorations | Keep the existing work discoverable with its analogy limits; avoid a second top-level product identity. |
| Receipts, source register, bibliography, research note, release records | Sources & research | Support the whole atlas; retain contextual source links on the relevant pages. |

This editorial map organizes the working site. It does not make every page ready
for public release. An area's description must match the material available in
the target build. Existing source-use and preview labels travel with their pages.

## Homepage hierarchy

1. OSW identity, the agreed headline, and its one-sentence explanation.
2. Three equal entrance cards with the descriptions above.
3. One broad ocean map or existing overview visual, if it helps orientation.
   It supports the overall geography; it does not launch a new visual experiment.
4. A short **How the pieces connect** paragraph:

   > Regions give us places to look. Currents and eddies show movement.
   > Temperature and heat reveal change. Explanations alongside the maps help
   > you understand what you see.

5. A compact project/status note, Learn more, About OSW, and Sources & research
   links. Avoid a large changelog, internal process vocabulary, feature counts,
   or release history competing with the three entrances.

Provide meaningful descriptive links rather than “Open” repeated on every card.
The homepage offers orientation and choices; it does not duplicate the directory
of every artifact. Work within the existing hosting approach and static assets.

## Navigation that holds the project together

- OSW wordmark consistently returns to the project homepage. The README remains
  the repository's concise introduction and contributor entry.
- The global header uses **Explore the ocean · Follow the currents · See what's changing**.
  **Learn more** is secondary; About OSW and Sources & research remain supporting
  links. Show the current area. Do not shorten these back to departmental labels.
- Each area has a short purpose statement and local navigation for its own views.
  Keep filters, modes, evidence downloads, and implementation tools out of the
  global header.
- Major pages identify their area and provide a way back to its overview.
  Deeper pages may use breadcrumbs where the hierarchy helps.
- Contextual links explain the relationship: **Explore this region's depths**,
  **See nearby currents**, or **Understand heat transport**. Preserve selection
  only where an existing compatible URL/state contract supports it.
- Keep existing URLs and deep links working. Change labels and navigation before
  considering directory moves. Reuse existing header/style conventions as far
  as practical; no frontend framework migration.
- Keep the global choices available on small screens and by keyboard, with
  visible focus and accessible current-page state. Collapsing navigation must
  not hide its meaning from assistive technology.

The See what's changing destination needs editorial attention: the event explorer
is currently a specific example. Adapt its entrance to explain the broader area.
Keep the existing guide collection accessible under Learn more. Do not leave a
global label promising a broad section that opens an unexplained narrow tool.
Prefer in-place introductions/index improvements to an extra layer of portals.

## The actual work

Deliver the messaging and navigation as one coherent editorial change:

- Apply the agreed opening copy, three labels, descriptions, and page-to-area mapping
  in this plan; use them consistently rather than inventing labels page by page.
- Shape the existing project entry into the homepage hierarchy above, and shorten
  the README around identity, the three entrances, status, and contributor/research links.
  Move lengthy chronology into the existing history/research surfaces with links.
- Apply consistent global navigation to the major area entrances and the primary
  Column, Exchange, and Event pages. Give almanac subpages a consistent return path;
  retain local task controls.
- Revise entrance headings and introductory copy so visitors understand why each
  area exists and how it relates to OSW. Preserve established names as subtitles
  or local labels where they remain useful.
- Align visitor-facing status on the touched entrances and README. Distinguish
  what is available in this build from experiments and publicly released material.
  Do not repeat a historical version/status claim without checking its current
  record; do not expand this into a repository-wide governance rewrite.
- Check that every major collection above is reachable, area names match their
  destinations, contextual scientific qualifications remain present, and old
  links continue working. Inspect desktop/mobile headers, keyboard use, focus,
  and the text order. Use the existing relevant link/browser checks.

Do not add a new evidence framework, case packet, scientific calculation, large
test program, or mandatory reader-study gate to this editorial task. Existing
release/source controls still apply to publication. If a label would overstate
the present content, fix the label or explanation within this scope.

## What completion looks like

The homepage, shared navigation, entrance copy, README cleanup, and visible
status alignment are implemented in this checkout. The delivery record below
distinguishes the verified local result from publication and broader scientific
validation.

A reader arriving on the homepage can explain what OSW is, see three clear
ways in, and choose an appropriate destination. A reader arriving deep in the site
can identify their area, get back to the whole project, and find another area.
The major body of existing work has a clear home without a wall of equal links.

Review the finished entrances together as one product. Use simple spot checks:
find ocean depths, named currents, a heat-event explanation, a concept guide,
and sources; then return to the homepage from each. Record confusing labels or
dead ends and fix them. These are practical editorial checks, not a claim of
formal usability validation.

Review the homepage, the three area entrances, and the primary depth/exchange
pages together. Completion requires consistent labels, reachable supporting
material, preserved deep links, accurate visible status, and a usable global
header at desktop/mobile sizes and by keyboard. Deliver the changes as one
coherent site revision, with a short list of any remaining limitations.

The distinguishing message is the breadth made intelligible: **one connected
atlas of ocean geography, motion, and change**. Evidence supports that promise
throughout the existing work; it does not need to be the headline or next project.

## Delivery record — 2026-11-11

| Requirement | Delivered result |
|---|---|
| One clear identity | [Homepage](../index.html) uses the agreed headline, explanation, and three equal cards. |
| Whole-project orientation | Shared navigation and supporting links on 22 HTML pages, including every main almanac page; [site.css](../site.css) keeps their presentation consistent. Active area, skip link, home link, keyboard focus, and responsive wrapping are included. |
| Clear subject entrances | Atlas introduces places and structures; almanac introduces currents and eddies; Event now introduces the broader change area before its existing example. Ocean depths and Exchange retain their tools with clearer introductions. |
| Supporting material has a home | [Learn more](../guides/index.html), [About OSW](../about.html), and [Sources & research](../research/index.html) connect guides, methods, downloads, history, planetary comparisons, and projection experiments. Contextual links connect regions, depths, currents, and heat. |
| Less competing material | The README is now a short project/contributor introduction. Its former directory and development notes are preserved in [PROJECT-NOTES.md](../research/PROJECT-NOTES.md); legacy README section anchors remain. Extra section links sit under “Methods and related views.” |
| Truthful visible status | Homepage, README, About, and research entry identify the local working preview. The preview-status document labels its older branch/release statements as historical. No version, citation, hosting target, or scientific admission changed. |
| Regeneration preserves navigation | Both existing Loop Current page builders include shared project navigation. Their generated-page equality check passes. |

Verified locally: 67 focused Atlas/Event/recorded-date/guide tests; 44 Chromium
page/viewport combinations covering all 22 pages at 1440 px and 390 px, with
no runtime errors or horizontal overflow; real transitions into ocean depths
and the Argo view; loaded motion/event/depth content; keyboard navigation,
reduced-motion operation, and navigation with JavaScript disabled. All local
links and unique HTML IDs pass across those pages. Python compilation, JavaScript
syntax checks, and existing almanac page-coverage checks also pass.

A follow-up editorial pass groups all 17 guides by reader questions, replaces
duplicate OSW mastheads with local view labels on six motion pages, and marks
Exchange's parent area correctly for assistive technology. Related-view
disclosures now have visible keyboard focus and 44 px targets. Another 36
page/viewport checks cover the nine adjusted pages at 320, 390, 768, and 1440 px;
all pass, including keyboard operation of the related-view disclosure. About
copy no longer hardcodes the checkout's branch name.

The broader scientific suites were run as well; their source-fixture limitations
are recorded in the [role review](../signals/roles/check/project-messaging-and-navigation-roles-check-2026-11-11.md).
They are not represented as passing. Source originals excluded from Git are not
substituted, and scientific guards have not been relaxed.

Remaining limits: this is a local source delivery, not a deployment. Existing
guide chapters remain Markdown documents linked from their new HTML index.
Frozen screened/release snapshots retain their own navigation and manifests;
the new global navigation covers the working site. Formal user studies,
screen-reader certification, independent scientific review, and an originality
comparison were not performed or claimed by this editorial change.
