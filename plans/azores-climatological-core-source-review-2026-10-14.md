# Azores seasonal model-core evidence

Continues the same current gap branch and PR83. This research stage supplies
two reviewed source values, their scope, a reported model-climatological range,
and an independent comparison figure. Inventory/native/WASM integration is
the next required stage; live inventory counts remain unchanged in this commit.

Carracedo et al. (2014), doi:10.1016/j.pocean.2013.12.005, section 3.1.1.1,
printed p122 / PDF p7, reports an Azores Current core about **240 km** wide
in spring and **400 km** in autumn, using velocities greater than **2 cm/s**.
The paper identifies these as its narrowest and broadest seasonal core
extents. Preserve 240–400 km as an approximate **regional inverse-model
climatological core range**. This is not a whole-current annual physical
range, a confidence interval, a fixed-depth width or a 2009 occupation.

Source context: western WOA-Box section at 19.5 W; 1-degree WOA09 input,
33 depth levels, five averaged temperature/salinity climatologies spanning
1955–2006 with unequal final period length, and oxygen/nutrients with all
available years. No single observation period assigned. The finer 1 dbar /
0.01-degree integration grid does not improve native observational resolution.
Approximate maximum core depths of 790/1100 m are retained as reported
vertical context, not width-measurement layers. Width errors remain unknown;
transport errors cannot be relabeled as width errors.

NOAA WOA09 Volume 1 Introduction, printed p1 / PDF p13, explicitly defines
spring as April–June and fall as October–December. These quarter definitions
are retained; meteorological month windows are not substituted. Winter/summer
widths and monthly widths are not numerically reported in the inspected prose.
No monthly interpolation, mapped width band or current-axis geometry follows.
The existing 110 km 2009 Azores section remains a separate scope and metric.

Original NORA article: 3,967,121 bytes, SHA256
`ea9ca0c5f5fde1b3234518aca1810a2421c556090aee9531ff46797f37eec7e8`.
Original NOAA documentation: 349,881 bytes, SHA256
`8f5046eeea5e4bb405f60dc526baf46143cc4ca1a2724f21203d9777277034da`.
Both exact originals verified locally and relevant pages visually inspected.
Original PDFs/page pixels remain outside Git; acquisition receipts are public.
No velocity field, published curve or figure digitized.

Reproduce the independently drawn comparison:
`python analysis/build_azores_climatological_core_width_figure.py`.
Add `--verify-originals` to verify both retained review originals. Default
figure generation validates the frozen source-extraction JSON, not private
PDF availability or the underlying scientific analysis. Four focused tests
and six subtests passed. The SVG was rendered and visually inspected.
An initial direct-SVG screenshot timed out; rendering the same SVG in an HTML
wrapper completed. No full-suite or live-UI integration result is claimed
for this research-only change.

Separate lead: Carracedo et al. (2012) cites a 100–250 km Azores Countercurrent
width at 33 W from Alves et al. (2002). The 2012 original was read at pp278–279
and visually inspected; the 2002 underlying full analysis has not been acquired.
This secondary number is not added as another primary current measurement.
The countercurrent's intermittent/reversing and depth-dependent interpretation
remains relevant to its unfilled axis and length gates.

Next: integrate the two model-core records with exact source bindings into
the width inventory, source index, seasonal inspector and native/WASM query;
preserve the scoped range, atlas quarters and all unknown physical dimensions;
run affected browser and full offline gates. Independent scientific admission
and the broader core-data goal remain open. PR83 remains the single draft PR.
