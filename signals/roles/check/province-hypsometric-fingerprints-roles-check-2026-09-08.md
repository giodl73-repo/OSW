---
skill: roles-check
topic: province-hypsometric-fingerprints
date: 2026-09-08
roles_used: [current, sounder, chart, beacon, harbor, keel, logbook, orbit]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Roles check — Province hypsometric fingerprints

**Artifact type:** deterministic scientific classification, interactive
cartography, quantitative passport, and public documentation

**Source commit:** `feb08df`

**Reviewed artifact SHA-256:**

- derivation: `3A091701F858166EF65579C81B5E377C1ED00D841E5F69345CE07EFAA4E7835D`
- research artifact: `86332B886C8A8257844FBC48043AAA7AB7776B80BCAC8D919821660DA676CA89`
- browser data: `8308AE5A693A24346A58B6B968050966F1CEBB058A22639AB3C91E9A92DFEB4E`
- browser logic: `74C1EE64D7D39347DF53BEE03AF3E985C9CF61C3331E62F4B2B1F408FB8CA43B`
- browser HTML: `EBA9C2D5A4FB79AFCB7C448BBF8016F2ED90AA15C7E6C782B3EEF7000A236F87`
- fingerprint tests: `4F201E6363BC149AA070ED62F514671EDAFDE96395CD246D8B0CE10D9B44588C`

## Role selection

All eight OSW roles apply because this stage defines a new complete vocabulary
from scientific data, maps it, exposes it through interaction, and could be
mistaken for geomorphology, habitat, dynamics, or planetary structure.

## Findings

### CURRENT

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Dominant bottom-depth share describes hypsometry, not current structure, water-mass identity, heat content, or transport. | P2 | Scientific meaning | Name it “floor character” and preserve explicit non-mechanism boundaries. **Resolved.** |
| 2 | One dominant band would erase meaningful vertical extent. | P2 | Fingerprint | Keep breadth, hadal presence, and rank shift as independent descriptors. **Resolved.** |
| 3 | A bathymetric fingerprint is time-stable reference geometry under the chosen source editions. | P3 | Temporal scope | Do not interpret differences as transient ocean change. **Accepted.** |

### SOUNDER

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | The derivative must be cryptographically tied to the D53 research payload. | P2 | Lineage | Record source path and SHA-256 and rebuild offline from that exact artifact. **Resolved.** |
| 2 | Dominance and breadth require explicit, reproducible rules. | P2 | Classification method | Store the maximum-area rule, ≥5% threshold, band list, and hadal test in the artifact. **Resolved.** |
| 3 | Rounded fractions and cell-center membership inherit all D52/D53 limitations. | P3 | Data quality | Carry the boundary forward rather than presenting fingerprints as independent observations. **Resolved.** |

### CHART

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Floor-character colors initially made deep and abyssal classes difficult to distinguish. | P2 | Palette | Increase lightness/hue separation while retaining an ordered shallow-to-deep sequence. **Resolved after Edge inspection.** |
| 2 | Only categories present in the 54-state result should occupy primary legend space. | P2 | Legend | Show shelf-led, deep-floor-led, and abyssal-floor-led plus the gold selection edge. **Resolved.** |
| 3 | A dominant class must not suppress the actual five-band area profile. | P3 | Map/profile pairing | Keep the seafloor-reach profile and exact dominant percentage beside the class map. **Resolved.** |

### BEACON

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | “Shelf,” “deep,” and “abyssal” can sound like discovered natural state types. | P2 | Public language | Append “-led,” define the largest-share rule, and call the vocabulary declared and literal. **Resolved.** |
| 2 | The 5% breadth cutoff could be mistaken for a natural threshold. | P2 | Breadth | Print the threshold in the passport, artifact method, and guide. **Resolved.** |
| 3 | KURO’s five-band result is memorable but not evidence of greater importance. | P3 | Highlight | Present it as a fingerprint contrast, not a winner or mechanism. **Accepted.** |

### HARBOR

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Floor character cannot be communicated only by three blue shades. | P2 | Equivalent meaning | Supply a live field label, full text legend, passport label/percentage, and canvas description. **Resolved.** |
| 2 | Six passport facts need a logical reading order and mobile reflow. | P2 | Passport | Use semantic `dl/dt/dd`, three desktop columns, and one mobile column. **Resolved.** |
| 3 | Older-only identities need an explicit unavailable fingerprint rather than stale values. | P3 | Missing state | Reuse the Version 4 unavailable passport branch for NPSE and OCAL. **Resolved.** |

### KEEL

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | A runtime-only classification would leave the new scientific claim weakly governed. | P2 | Artifact contract | Generate a standalone research JSON and byte-equivalent browser bundle. **Resolved.** |
| 2 | Classification drift needs fixed census and named-example tests. | P2 | Regression | Assert 11/19/24 characters, 1/22/17/13/1 breadth counts, and SUND/NADR/SPSG/KURO examples. **Resolved.** |
| 3 | The derivative should require no live provider or optional numerical dependency. | P3 | Rebuild | Use standard-library JSON/hash logic over the committed D53 payload. **Resolved.** |

### LOGBOOK

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | A new classification requires a registered evidence identity. | P2 | Source register | Add D54 as a deterministic D53 derivative with the full result and limitations. **Resolved.** |
| 2 | Browser download links and method commands must expose the new artifact. | P2 | Repository record | Link the research JSON and document derivation and targeted tests. **Resolved.** |
| 3 | No release or remote action follows from this private-preview milestone. | P3 | Publication | Commit locally only after the full gate. **Accepted.** |

### ORBIT

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Seafloor-led categories cannot be copied to gas giants with no comparable solid bathymetric boundary. | P2 | Planetary boundary | Keep D54 Earth-specific. **Resolved.** |
| 2 | Atmospheric pressure-depth breadth is not equivalent to ocean floor-depth breadth. | P2 | Analogy | Require a separately defined pressure/mass coordinate and lower-boundary model. **Accepted.** |
| 3 | A multi-descriptor fingerprint is transferable only as a classification method. | P3 | Method transfer | Transfer explicit rules and uncertainty, not labels or thresholds. **Accepted.** |

## Synthesis

Roles reviewed: 8

P1 blockers: 0 | P2 issues: 16 | P3 notes: 8

**Verdict: APPROVED-WITH-CONDITIONS**

**Top finding:** Floor character must remain a transparent dominant-area
descriptor and never be promoted into geomorphology or dynamics.

**Cross-role consensus:** CURRENT, SOUNDER, CHART, and BEACON agree that the
dominant label is acceptable only with its rule, percentage, full profile, and
independent breadth/hadal/rank-shift descriptors visible.

## Amendments

1. Separate mutually exclusive character from nonexclusive breadth, hadal
   reach, and rank shift. **Applied in the artifact and passport.**
2. Strengthen the ordered palette and retain complete text equivalence.
   **Applied after desktop Edge review.**
3. Bind the derivative to D53 and test exact census, examples, and deterministic
   browser output. **Applied in the offline derivation and tests.**

The fingerprint stage may be committed to the private-preview branch after the
full repository suite. Public promotion, geomorphic naming, and the 54/56
edition decision remain separate gates.
