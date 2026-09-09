---
wave: 2026-09-08-wp001b-first-evidence-adapters
work_package: WP-OSW-001
pulse: 001-B
date: 2026-09-08
amendment: 01
status: ready_at_native_role_fixed_point
decision: pass_with_risk
---

# WP-OSW-001B Entry Amendment 01 — Surface Heat Flux Identity

## Decision

The committed 001-B entry at `29b7c47` cannot truthfully adapt D12's principal
quantity through the 001-A quantity vocabulary. Net downward surface heat flux
is not temperature, heat content, storage tendency, transport, advection,
convergence, transformation, or residual.

This amendment authorizes one additive controlled value only:

`QuantityClass.SURFACE_HEAT_FLUX = "surface_heat_flux"`

It is a registered ocean-quantity extension permitted by IF-OSW-007. No other
identity value, family, adapter, interface, diagnostic, or authority is added.
The amendment preserves all 001-B paths, fixtures, stops, and prohibitions.

## Exact meaning

| Field | Contract |
|---|---|
| Quantity class | `surface_heat_flux` |
| Physical dimension | energy per area per time |
| Typical unit in D12 | W/m² |
| Sign requirement | explicit; D12 is positive downward into the ocean surface |
| Support requirement | explicit time interval and spatial support; vertical support is the air–sea boundary, not a water-column depth |
| Does support | a bounded surface energy-flux quantity under the declared source/method conventions |
| Does not support | temperature change without a separate heat-capacity/depth conversion; storage; horizontal/vertical transport; native model closure; causation |

Mixed-layer-equivalent temperature tendencies within D12 remain distinct
derived quantities with their own units, support, assumptions, and claim
ceilings. The adapter may not use `surface_heat_flux` for those conversions.

## Owned mutation and proof

This amendment adds `surface_heat_flux` to `QuantityClass` in
`analysis/osw_contracts.py` and requires exact positive/negative tests in the
001-B adapter suite. Case, whitespace, alias, or use without explicit sign and
support must fail through the existing identity diagnostics. No existing
quantity meaning changes, and historical source bytes remain read-only.

The implementation review must confirm that D12 surface flux, its slab-
equivalent temperature-rate comparisons, D13 storage, D14 horizontal
advection, and D14 residual remain separate identities. The exact amendment
and its native-role review must be committed before product code changes.

## Boundary retained

This is entry repair, not implementation evidence. It does not pass any VFY or
Validation item; authorize 001-C; admit D12–D14 scientifically; or authorize a
reader, map, scene, release, push, merge, deployment, external contact, or
cross-repository change.

Decision: `pass_with_risk` for this one vocabulary extension within 001-B.

## Source links

- [Controlling 001-B entry](ENTRY.md)
- [IF-OSW-007](../../../docs/vtrace/INTERFACES.md#if-osw-007--quantity-identity-and-claim-ceiling)
- [Amendment roles check](../../../signals/roles/check/wp001b-entry-amendment-01-roles-check-2026-09-08.md)
