# Province Atlas shape system

Date: 2026-08-29  
Status: next-stage design contract; no public promotion authorized

## Goal

Make the 56 provinces as memorable as a national state map without allowing a
beautiful cartogram to impersonate measured geography.

## The hook

> **One ocean. 56 provinces. Two truths.**
>
> **Equal voice** gives every province a recognizable puzzle piece.  
> **True footprint** returns every province to defensible geographic geometry.

The strongest eventual interaction is a morph or paired comparison that keeps
each province's code and biome color stable between the two views.

## What Version 1 does

- Covers the classic 56-code vocabulary.
- Gives every province a visible label target.
- Groups provinces by ocean basin and broad north-to-south reading order.
- Uses real Natural Earth coastlines as horizontally compressed orientation
  fingerprints occupying only narrow seams.
- Does not preserve area, exact shape, distance, direction, complete adjacency,
  or exact contact with land.

## Version 2 — varied puzzle cartogram

The next visual iteration should replace the repeated row cells with unique
shared boundaries while retaining readable labels.

Required invariants:

1. Exactly 56 pieces, with no overlaps or unassigned holes inside the schematic
   ocean body.
2. Pacific, Indian, Atlantic, Arctic, and Southern grouping remains obvious.
3. Shared edges are generated once and reused by both neighboring provinces so
   the result reads as a real puzzle rather than 56 floating badges.
4. Coast-facing provinces touch the appropriate compressed continental seam
   only when that relationship is part of the declared schematic topology.
5. Shape and size variation is aesthetic/topological until a quantitative area
   rule is declared; it must not imply measured footprint.
6. Codes remain readable without hover, and full names remain available without
   color or pointer through the 56-row directory.

Preferred grammar:

- fewer right angles and no repeated bevel formula;
- long coastal pieces, broad gyre interiors, narrow current/front pieces, and
  circumpolar bands where the classification supports those identities;
- restrained coastline seams occupying roughly 8–12% of total map width;
- the existing four-biome palette retained across every view.

## Version 3 — true geographic reference

Do not obtain geographic truth by tracing a copyrighted map or importing a
noncommercial boundary product into the MIT repository.

Admission paths:

1. a boundary source whose license is compatible with repository distribution;
2. written permission covering redistribution and derived display artifacts; or
3. an independently specified, reproducible construction from published
   coordinate/method facts, with source and transformation receipts.

The geographic view must state its Longhurst edition, coordinate system,
feature count, source license, source checksum, simplification tolerance, and
whether boundaries are static means or dynamically diagnosed.

## Crossing-feature silhouette contract

The 36 selectable waters, flows, edges, seafloor features, life zones, and
events are not map pins or badges. Even while schematic, every object must have
enough geographic character to be recognized as a different kind of ocean
place.

Required invariants:

1. Every object has a distinct silhouette signature; repeated circles,
   capsules, diamonds, and rounded quadrilaterals are not an acceptable system.
2. Area objects show a plausible relationship to their source, basin, coast,
   latitude belt, or spreading direction without claiming observed extent.
3. Mechanism is legible in topology: water masses have source necks and
   spreading tongues; gyres have asymmetric directional loops; fronts have
   meandering paired seams; gates have section or passage geometry; relief uses
   ridge, trench, or plateau conventions; anomalies remain visibly transient.
4. Family identity survives without color through fill, hatching, dash rhythm,
   line construction, or conventional map marks.
5. Thin paths retain a generous invisible hit area, and every multi-part object
   remains one keyboard-focusable selectable group.

These are interpretive index shapes, not measured footprints, boundaries,
transport sections, or water-mass analyses. The fluid-geography map and
HEATPLATES are the quality precedent for their silhouette language.

## Version 4 — moving provinces

The scientific destination is not a prettier fixed border. A later observed
layer can estimate province membership or transition probability from declared
environmental fields. Reygondeau et al. (2013) used bathymetry, chlorophyll,
sea-surface temperature, and sea-surface salinity to demonstrate that province
locations, extents, and overlaps change through time:
https://doi.org/10.1002/gbc.20089

## Acceptance sequence

1. Owner chooses whether the coastline-fingerprint revision improves the hook.
2. Produce at least two varied puzzle grammars without removing Version 1.
3. Run native cartography, science, accessibility, provenance, and repository
   reviews on the selected puzzle grammar.
4. Resolve a legally compatible source path before implementing true footprints.
5. Only then prototype the Equal voice ↔ True footprint transition.
