---
skill: discover-websearch
topic: ocean-waves-tides-oscillations
date: 2026-09-05
claims_checked: 5
confirmed: 5
---

# Web grounding — ocean waves, tides, and oscillations

## Claims to ground

| # | Claim | Source | Why it matters |
|---|---|---|---|
| 1 | Wave propagation is not the same as bulk water advection, but real waves can produce residual drift. | guide hypothesis | Prevent both the “wave is a current” and “waves never transport water” errors. |
| 2 | Tide and tidal current are distinct vertical and horizontal expressions of the tidal response. | classification gap | The registry currently contains tide but not tidal current. |
| 3 | Internal waves propagate within stratification and can transfer energy into mixing. | planned guide | Connect layers, topography, waves, and transformation. |
| 4 | Rossby, Kelvin, and inertial motions require rotation-aware identity tests. | planned guide | Visual wavelength alone cannot identify these modes. |
| 5 | Tsunami, storm surge, and seiche require different forcing and geometry labels. | hazard taxonomy | Similar water-level traces can encode different phenomena. |

## Evidence

### Claim 1 — propagation versus material transport

- Query: `NOAA waves transmit energy not water`
  - Source: [NOAA Ocean Service](https://oceanservice.noaa.gov/facts/wavesinocean.html)
  - Direct quote: “Waves transmit energy, not water, across the ocean.”
- Query: `WHOI Stokes drift mass transport velocity`
  - Source: [WHOI wave notes](https://www.whoi.edu/science/PO/people/jprice/class/elreps.pdf)
  - Direct quote: “fluid parcels have a substantial net motion in the direction of the wave propagation.”
- Query: `WaveWatch Stokes volume transport output`
  - Source: [NOAA WaveWatch III manual](https://polar.ncep.noaa.gov/waves/wavewatch/manual.v5.16.pdf)
  - Direct quote: “Stokes volume transport” and “Stokes drift at the sea surface.”
- Verdict: **CONFIRMED WITH QUALIFICATION.** Linear orbital motion is not bulk advection, but finite-amplitude waves can create residual transport.

### Claim 2 — tide is not tidal current

- Query: `NOAA tide tidal current difference vertical horizontal`
  - Source: [NOAA Tides and Currents glossary](https://tidesandcurrents.noaa.gov/glossary.html)
  - Direct quote: “The vertical component ... called tide”; horizontal motion is “tidal current.”
- Query: `NOAA tides rise fall currents ebb flood`
  - Source: [NOAA tides lesson](https://oceanservice.noaa.gov/education/tutorial_tides/lessons/ups_downs.html)
  - Direct quote: “tides rise and fall, while tidal currents ebb ... and flood.”
- Query: `NOAA tidal constituent amplitude phase period`
  - Source: [NOAA Tides and Currents glossary](https://tidesandcurrents.noaa.gov/glossary.html)
  - Direct quote: “Each constituent represents a periodic change ... in the relative positions of the Earth, Moon, and Sun.”
- Verdict: **CONFIRMED.** They share astronomical forcing but require different measured variables and geometry.

### Claim 3 — internal waves connect stratification to mixing

- Query: `NOAA GFDL internal waves stratification mixing`
  - Source: [GFDL Ocean Mixing](https://www.gfdl.noaa.gov/ocean-mixing/)
  - Direct quote: “stable density stratification of the ocean provides the restoring force.”
- Query: `WHOI internal tides transfer energy momentum deep ocean`
  - Source: [WHOI Internal Tides](https://scienceweb.whoi.edu/PO/turbulence/Research/internal_tides.php)
  - Direct quote: “wave motion transfers energy and momentum in the deep interior.”
- Query: `NOAA internal waves density interface topography`
  - Source: [NOAA internal-wave feature class](https://www.fisheries.noaa.gov/inport/item/39341)
  - Direct quote: “occur at the interface between two layers ... of differing densities.”
- Verdict: **CONFIRMED.** Generation, propagation, breaking, and irreversible mixing must remain separate stages.

### Claim 4 — rotation distinguishes planetary modes

- Query: `NOAA ocean Rossby waves rotating fluids`
  - Source: [NOAA Rossby waves](https://oceanservice.noaa.gov/facts/rossby-wave.html)
  - Direct quote: “Rossby waves ... naturally occur in rotating fluids.”
- Query: `UCAR ocean Kelvin wave eastward Rossby westward`
  - Source: [UCAR tropical variability](https://www.meted.ucar.edu/tropical/textbook_2nd_edition/print_4.htm)
  - Direct quote: “oceanic Kelvin waves are trapped along the equator.”
- Query: `NOAA near inertial waves wind ice ocean mixing`
  - Source: [Arctic mixing review](https://repository.library.noaa.gov/view/noaa/14515/noaa_14515_DS1.pdf)
  - Direct quote: “near-inertial waves forced by wind and ice–ocean stresses.”
- Verdict: **CONFIRMED.** Direction, trapping, frequency, latitude, and vertical mode belong in the detection contract.

### Claim 5 — coastal water-level hazards are not synonyms

- Query: `NOAA tsunami sudden displacement not tide`
  - Source: [U.S. Tsunami Warning Centers](https://preview-tsunami8.ncep.noaa.gov/?page=tsunamiFAQ)
  - Direct quote: “waves caused by any large and sudden displacement of the ocean.”
- Query: `NOAA storm surge above astronomical tide`
  - Source: [National Hurricane Center](https://www.nhc.noaa.gov/surge/)
  - Direct quote: “an abnormal water level rise generated by a storm over and above the predicted astronomical tide.”
- Query: `NOAA seiche standing wave enclosed body`
  - Source: [NOAA: What is a seiche?](https://oceanservice.noaa.gov/facts/seiche.html)
  - Direct quote: “a standing wave oscillating in a body of water.”
- Verdict: **CONFIRMED.** Source, propagation/standing behavior, basin geometry, and reference water level distinguish the three.

## Findings

| # | Finding | Verdict | Source |
|---|---|---|---|
| 1 | A propagating wave primarily moves a disturbance and energy. | CONFIRMED | [NOAA](https://oceanservice.noaa.gov/facts/wavesinocean.html) |
| 2 | Finite-amplitude waves can generate residual Stokes drift. | CONFIRMED | [WHOI](https://www.whoi.edu/science/PO/people/jprice/class/elreps.pdf) |
| 3 | Operational wave models expose Stokes drift and volume transport separately. | CONFIRMED | [NOAA](https://polar.ncep.noaa.gov/waves/wavewatch/manual.v5.16.pdf) |
| 4 | Tide is conventionally the vertical component of the tidal response. | CONFIRMED | [NOAA](https://tidesandcurrents.noaa.gov/glossary.html) |
| 5 | Tidal current is the horizontal component. | CONFIRMED | [NOAA](https://oceanservice.noaa.gov/education/tutorial_tides/lessons/ups_downs.html) |
| 6 | Harmonic constituents have declared amplitude, phase, speed, and period. | CONFIRMED | [NOAA](https://tidesandcurrents.noaa.gov/glossary.html) |
| 7 | Density stratification supplies the restoring force for internal waves. | CONFIRMED | [GFDL](https://www.gfdl.noaa.gov/ocean-mixing/) |
| 8 | Internal waves transfer energy and momentum through the ocean interior. | CONFIRMED | [WHOI](https://scienceweb.whoi.edu/PO/turbulence/Research/internal_tides.php) |
| 9 | Internal-wave breaking can contribute to turbulent mixing. | CONFIRMED | [GFDL](https://www.gfdl.noaa.gov/ocean-mixing/) |
| 10 | Rossby waves are rotation-dependent planetary waves. | CONFIRMED | [NOAA](https://oceanservice.noaa.gov/facts/rossby-wave.html) |
| 11 | Equatorial oceanic Kelvin waves are trapped and propagate eastward. | CONFIRMED | [UCAR](https://www.meted.ucar.edu/tropical/textbook_2nd_edition/print_4.htm) |
| 12 | Near-inertial waves can be forced by wind and ice stress. | CONFIRMED | [NOAA Library](https://repository.library.noaa.gov/view/noaa/14515/noaa_14515_DS1.pdf) |
| 13 | Tsunamis arise from large sudden water-column displacement and are not tides. | CONFIRMED | [NOAA](https://preview-tsunami8.ncep.noaa.gov/?page=tsunamiFAQ) |
| 14 | Storm surge is defined relative to the predicted astronomical tide. | CONFIRMED | [NHC](https://www.nhc.noaa.gov/surge/) |
| 15 | A seiche is a standing oscillation favored by enclosed geometry. | CONFIRMED | [NOAA](https://oceanservice.noaa.gov/facts/seiche.html) |

Summary: **5 of 5 claims confirmed, with one important qualification; 0 contradicted; 0 unconfirmed.**

## Ungrounded claims

No claim was ungrounded. This search does not establish universal thresholds
for separating every observed wave mode; those depend on latitude, depth,
stratification, geometry, frequency band, and measurement system.

## Amendments

1. Replace “waves move energy, not water” with a leading-order statement plus
   explicit Stokes-drift and breaking exceptions.
2. Add tidal current as a flow structure separate from tide as an oscillation.
3. Classify hazards by forcing and propagation behavior rather than by the fact
   that all can raise coastal water level.
