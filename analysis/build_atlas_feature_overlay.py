"""Build selectable schematic feature shapes for the interactive Atlas.

The first twelve geometries preserve the established fluid-geography artwork.
The remaining records receive geographically placed, mechanism-specific shapes
instead of generic symbols. Water masses use source-fed tongues, gyres use
asymmetric directional loops, fronts use paired seams, gates use section marks,
and relief uses conventional ridge, trench, or plateau texture. They are
conceptual index geometry, not observations.
"""

from __future__ import annotations

import argparse
import html
from pathlib import Path
import xml.etree.ElementTree as ET


FEATURES = [
    ("indo-pacific-warm-pool", "Indo-Pacific Warm Pool", "waters", '<path class="area warm" d="M1090 438Q1114 399 1162 391L1194 398Q1216 368 1256 374L1285 359Q1324 348 1357 370Q1394 353 1428 373L1460 367Q1504 380 1540 410L1540 500Q1504 520 1466 506L1432 513Q1401 519 1378 499Q1342 525 1300 507L1268 495Q1232 512 1203 490Q1160 500 1128 476L1104 466Q1084 454 1090 438Z M60 410Q95 390 130 394L159 386Q195 386 218 405L241 421Q261 441 248 464Q235 489 198 497L166 496Q139 515 108 504L82 507Q66 506 60 495Z"/>'),
    ("western-hemisphere-warm-pool", "Western Hemisphere Warm Pool", "waters", '<path class="area warm" d="M304 445Q325 416 365 410L401 414Q426 380 465 384L493 372Q524 373 546 391Q582 380 612 399L636 416Q661 440 646 465L623 480Q595 508 557 500L525 506Q500 505 479 488Q443 505 407 489L376 477Q343 479 318 462Q302 454 304 445Z"/>'),
    ("northeast-pacific-blob", "Northeast Pacific Blob", "events", '<path class="area event" d="M78 279Q91 222 153 207Q218 181 278 213Q341 239 333 295Q327 343 270 366Q209 389 148 357Q90 344 78 279Z"/><path class="event-core" d="M132 273Q151 233 203 229Q261 224 292 263Q306 303 266 327Q211 350 162 326Q126 311 132 273Z"/>'),
    ("el-nino-tongue", "El Niño Tongue", "events", '<path class="area event" d="M60 444C145 422 250 428 365 451C435 465 485 478 540 500C460 520 375 515 288 493C195 470 121 473 60 480Z"/>'),
    ("gulf-stream", "Gulf Stream", "flows", '<path class="hit" d="M470 390C480 353 506 332 540 315C578 296 620 275 658 250"/><path class="flow" d="M470 390C480 353 506 332 540 315C578 296 620 275 658 250"/>'),
    ("kuroshio", "Kuroshio", "flows", '<path class="hit" d="M1330 385C1340 350 1360 333 1395 320C1440 303 1480 282 1515 254"/><path class="flow" d="M1330 385C1340 350 1360 333 1395 320C1440 303 1480 282 1515 254"/>'),
    ("agulhas", "Agulhas System", "flows", '<path class="hit" d="M925 520C944 559 946 597 922 626C895 656 850 655 818 633"/><path class="flow" d="M925 520C944 559 946 597 922 626C895 656 850 655 818 633"/>'),
    ("antarctic-circumpolar-current", "Antarctic Circumpolar Current", "flows", '<path class="hit" d="M60 704C280 679 500 710 745 693C1002 675 1260 709 1540 690"/><path class="flow cold-flow" d="M60 704C280 679 500 710 745 693C1002 675 1260 709 1540 690"/>'),
    ("circumpolar-deep-water", "Circumpolar Deep Water", "waters", '<path class="area buried" d="M60 674C280 650 490 679 735 660C970 642 1260 672 1540 652L1540 760C1280 742 1040 756 800 746C530 735 300 760 60 742Z"/>'),
    ("atlantic-water-arctic", "Atlantic Water in the Arctic", "waters", '<path class="area buried" d="M770 126C850 102 980 108 1058 146C1090 162 1078 203 1035 221C955 255 824 241 767 206C733 186 739 141 770 126Z"/>'),
    ("drake-passage", "Drake Passage", "edges", '<path class="hit" d="M493 682Q520 692 547 681"/><path class="gate-section" d="M493 682Q520 692 547 681"/><path class="gate-bank" d="M493 668L493 696M547 667L547 695"/>'),
    ("indonesian-throughflow", "Indonesian Throughflow", "edges", '<path class="hit" d="M1260 462L1304 501"/><path class="gate-section" d="M1260 462L1304 501"/><path class="passage-cut" d="M1268 464L1261 478M1282 476L1274 491M1297 488L1289 503"/>'),
    ("antarctic-bottom-water", "Antarctic Bottom Water", "waters", '<path class="area cold-water abyssal-source" d="M60 769Q250 741 438 768Q612 790 790 763Q972 738 1156 764Q1350 789 1540 755L1540 815Q1327 837 1138 811Q950 792 781 817Q594 841 414 812Q236 791 60 824Z"/><path class="water-branch" d="M604 786Q567 709 590 632Q609 573 650 528"/><path class="water-branch" d="M1028 787Q987 726 1005 662Q1020 608 1060 567"/><path class="water-branch" d="M283 790Q254 736 274 682Q293 638 326 604"/>'),
    ("north-atlantic-deep-water", "North Atlantic Deep Water", "waters", '<path class="area cold-water water-tongue" d="M568 236Q610 206 646 233L660 278Q647 323 674 361Q713 412 700 470Q687 530 708 581Q724 625 691 692L628 681Q647 624 623 574Q595 519 614 466Q635 408 603 363Q570 320 568 236Z"/><path class="water-core" d="M594 247Q616 229 636 246L639 278Q624 298 604 284Z"/><path class="water-branch" d="M667 517Q708 549 742 604"/>'),
    ("antarctic-intermediate-water", "Antarctic Intermediate Water", "waters", '<path class="area cold-water intermediate-arc" d="M278 617Q390 586 493 605Q572 620 646 603L663 644Q573 671 480 650Q387 630 302 664Z"/><path class="area cold-water intermediate-arc" d="M650 610Q760 583 852 615Q945 645 1035 617L1052 658Q948 689 844 654Q757 626 671 663Z"/><path class="area cold-water intermediate-arc" d="M1040 613Q1140 584 1257 610L1291 650Q1162 681 1061 658Z"/>'),
    ("subantarctic-mode-water", "Subantarctic Mode Water", "waters", '<path class="area cold-water mode-water" d="M682 602Q754 570 835 588L871 615Q811 638 736 631Z"/><path class="area cold-water mode-water" d="M886 601Q968 572 1052 593L1093 624Q1018 645 935 632Z"/><path class="area cold-water mode-water" d="M1107 608Q1182 583 1244 610L1265 642Q1194 656 1130 640Z"/>'),
    ("north-pacific-intermediate-water", "North Pacific Intermediate Water", "waters", '<path class="area cold-water intermediate-crescent" d="M1303 228Q1394 185 1497 223Q1534 238 1540 260L1540 321Q1485 283 1408 286Q1353 289 1317 330L1287 298Q1317 258 1360 248Q1325 246 1303 228Z"/><path class="water-core" d="M1320 239Q1362 215 1408 221Q1370 241 1342 268Z"/>'),
    ("labrador-sea-water", "Labrador Sea Water", "waters", '<path class="area cold-water convective-bowl" d="M548 177Q570 144 607 151L631 163Q659 157 674 181L670 207Q689 225 666 250Q641 277 606 266L583 276Q554 260 547 235Q524 211 548 177Z"/><path class="convection-ring" d="M570 190Q596 169 627 184Q650 202 632 227Q608 248 581 229Q561 215 570 190Z"/>'),
    ("mediterranean-outflow-water", "Mediterranean Outflow Water", "waters", '<path class="area salty-water outflow-tongue" d="M891 350Q863 324 827 332L790 341Q762 344 743 362Q765 385 800 388L840 381Q871 384 902 368Z"/><path class="salty-core" d="M872 351Q836 344 799 356Q777 362 758 366"/><path class="meddy" d="M785 382Q772 397 755 384Q743 372 756 359"/>'),
    ("red-sea-water", "Red Sea Water", "waters", '<path class="area salty-water outflow-plume" d="M989 383Q1011 386 1028 404L1041 425Q1070 431 1085 453Q1064 474 1036 460L1017 445Q992 445 977 425Q969 405 989 383Z"/><path class="salty-core" d="M993 393Q1008 411 1019 433Q1043 439 1066 454"/>'),
    ("north-pacific-subtropical-gyre", "North Pacific Subtropical Gyre", "flows", '<path class="hit" d="M92 334C118 269 223 244 307 280C359 303 365 359 326 401C282 448 174 452 112 409C83 388 78 359 92 334Z"/><path class="gyre" d="M92 334C118 269 223 244 307 280C359 303 365 359 326 401C282 448 174 452 112 409C83 388 78 359 92 334Z"/><path class="gyre-spine" d="M112 407Q93 365 108 322"/>'),
    ("south-pacific-subtropical-gyre", "South Pacific Subtropical Gyre", "flows", '<path class="hit" d="M106 565C144 490 275 468 380 509C444 534 458 595 407 644C350 699 215 707 132 655C91 629 87 594 106 565Z"/><path class="gyre" d="M106 565C144 490 275 468 380 509C444 534 458 595 407 644C350 699 215 707 132 655C91 629 87 594 106 565Z"/><path class="gyre-spine" d="M132 653Q102 609 122 551"/>'),
    ("north-atlantic-subtropical-gyre", "North Atlantic Subtropical Gyre", "flows", '<path class="hit" d="M600 333C625 286 694 274 752 300C792 319 798 358 771 394C738 437 660 439 616 406C592 387 586 356 600 333Z"/><path class="gyre" d="M600 333C625 286 694 274 752 300C792 319 798 358 771 394C738 437 660 439 616 406C592 387 586 356 600 333Z"/><path class="gyre-spine" d="M617 405Q596 369 611 327"/>'),
    ("south-atlantic-subtropical-gyre", "South Atlantic Subtropical Gyre", "flows", '<path class="hit" d="M618 556C645 508 719 495 776 526C816 547 819 592 788 628C750 671 670 669 630 632C607 611 603 581 618 556Z"/><path class="gyre" d="M618 556C645 508 719 495 776 526C816 547 819 592 788 628C750 671 670 669 630 632C607 611 603 581 618 556Z"/><path class="gyre-spine" d="M631 631Q611 596 629 548"/>'),
    ("indian-ocean-subtropical-gyre", "Indian Ocean Subtropical Gyre", "flows", '<path class="hit" d="M967 555C1004 502 1104 492 1180 526C1231 549 1239 598 1201 637C1157 683 1049 681 990 641C957 619 947 584 967 555Z"/><path class="gyre" d="M967 555C1004 502 1104 492 1180 526C1231 549 1239 598 1201 637C1157 683 1049 681 990 641C957 619 947 584 967 555Z"/><path class="gyre-spine" d="M991 639Q962 600 982 547"/>'),
    ("antarctic-polar-front", "Antarctic Polar Front", "edges", '<path class="hit" d="M60 720C196 700 342 732 485 712C636 691 775 731 925 709C1080 686 1266 730 1540 707"/><path class="front" d="M60 720C196 700 342 732 485 712C636 691 775 731 925 709C1080 686 1266 730 1540 707"/><path class="front-companion" d="M60 731C204 713 339 741 491 724C638 706 780 742 931 722C1092 701 1277 741 1540 720"/>'),
    ("subantarctic-front", "Subantarctic Front", "edges", '<path class="hit" d="M60 672C210 648 348 686 505 663C656 642 807 681 959 657C1120 633 1280 677 1540 653"/><path class="front" d="M60 672C210 648 348 686 505 663C656 642 807 681 959 657C1120 633 1280 677 1540 653"/><path class="front-companion" d="M60 682C211 661 351 697 509 675C657 655 810 692 963 669C1122 647 1282 689 1540 665"/>'),
    ("equatorial-pacific-divergence", "Equatorial Pacific Divergence", "edges", '<path class="hit" d="M60 459C150 444 229 468 313 451C379 438 439 462 515 452"/><path class="divergence" d="M60 459C150 444 229 468 313 451C379 438 439 462 515 452"/><path class="divergence-arrow" d="M154 454L145 435M154 454L162 474M309 452L300 433M309 452L318 472M430 453L422 434M430 453L439 472"/>'),
    ("mid-atlantic-ridge", "Mid-Atlantic Ridge", "floor", '<path class="hit" d="M760 226L742 273L755 318L731 365L747 411L722 460L744 506L721 558L739 608L713 660L728 735"/><path class="ridge" d="M760 226L742 273L755 318L731 365L747 411L722 460L744 506L721 558L739 608L713 660L728 735"/><path class="ridge-flank" d="M742 273L720 262M755 318L779 307M731 365L708 354M747 411L772 401M722 460L699 449M744 506L768 495M721 558L697 548M739 608L764 598M713 660L691 649"/>'),
    ("east-pacific-rise", "East Pacific Rise", "floor", '<path class="hit" d="M322 397L349 442L334 487L358 530L342 577L370 622L355 673L382 731"/><path class="ridge" d="M322 397L349 442L334 487L358 530L342 577L370 622L355 673L382 731"/><path class="ridge-flank" d="M349 442L372 432M334 487L311 477M358 530L382 520M342 577L319 566M370 622L394 611M355 673L331 662"/>'),
    ("mariana-trench", "Mariana Trench", "floor", '<path class="hit" d="M1425 326Q1482 367 1470 425Q1458 473 1482 522"/><path class="trench" d="M1425 326Q1482 367 1470 425Q1458 473 1482 522"/><path class="trench-teeth" d="M1444 342L1429 351M1461 361L1445 371M1472 383L1454 390M1475 408L1457 411M1470 435L1452 431M1468 461L1450 457M1474 488L1456 493"/>'),
    ("kerguelen-plateau", "Kerguelen Plateau", "floor", '<path class="plateau" d="M1068 650Q1090 622 1122 629L1145 620L1171 642L1166 665L1180 688L1155 708L1128 701L1105 714L1080 694L1085 674Z"/><path class="plateau-contour" d="M1090 657Q1110 640 1132 645L1152 654L1156 677L1137 693L1112 688L1095 676Z"/><path class="plateau-contour inner" d="M1111 658Q1126 651 1140 662L1138 677L1122 682L1110 673Z"/>'),
    ("etnp-oxygen-minimum-zone", "Eastern Tropical North Pacific OMZ", "life", '<path class="area oxygen-zone" d="M250 405Q282 383 327 392L371 414Q404 442 410 474Q372 500 325 484L286 469Q256 449 250 405Z"/><path class="oxygen-core" d="M274 420Q310 404 347 421Q378 437 389 461Q353 477 318 463Q287 451 274 420Z"/>'),
    ("etsp-oxygen-minimum-zone", "Eastern Tropical South Pacific OMZ", "life", '<path class="area oxygen-zone" d="M315 486Q348 467 387 481L419 510Q447 544 443 584Q409 603 371 579L343 554Q319 530 315 486Z"/><path class="oxygen-core" d="M337 500Q368 486 397 508Q423 532 426 559Q400 576 373 555Q347 536 337 500Z"/>'),
    ("arabian-sea-oxygen-minimum-zone", "Arabian Sea OMZ", "life", '<path class="area oxygen-zone" d="M1014 378Q1049 355 1090 369L1123 391Q1134 427 1112 458Q1074 479 1035 458L1014 431Q1001 405 1014 378Z"/><path class="oxygen-core" d="M1036 389Q1067 372 1095 390Q1114 408 1104 436Q1076 454 1048 438Q1028 419 1036 389Z"/>'),
    ("sargasso-sea", "Sargasso Sea", "life", '<path class="area sargasso" d="M600 333Q630 294 678 291L720 302Q757 318 774 354Q777 389 746 416Q706 440 659 423Q618 411 598 378Q585 356 600 333Z"/><path class="sargasso-boundary" d="M610 337Q638 306 680 305Q724 306 753 337Q768 367 745 397Q713 425 672 414Q630 407 610 377Q598 356 610 337Z"/><path class="sargasso-swirl" d="M651 353Q671 330 701 339Q726 349 716 372Q703 394 676 385Q654 378 659 360"/>'),
]

COAST_CLEARANCE_EXEMPT = {
    "drake-passage",
    "indonesian-throughflow",
    "mediterranean-outflow-water",
    "red-sea-water",
}

SEAM_CONTINUATIONS = {
    "indo-pacific-warm-pool": 448,
    "el-nino-tongue": 462,
    "antarctic-circumpolar-current": 690,
    "circumpolar-deep-water": 700,
    "antarctic-bottom-water": 790,
    "antarctic-polar-front": 720,
    "subantarctic-front": 672,
}


def load_land_path(province_map: Path) -> str:
    """Reuse the province ground's exact, checksum-receipted land geometry."""
    root = ET.parse(province_map).getroot()
    for element in root.iter("{http://www.w3.org/2000/svg}path"):
        if element.attrib.get("class") == "land-outline":
            path = element.attrib.get("d")
            if path:
                return path
    raise ValueError(f"No land-outline path found in {province_map}")


def build_svg(land_path: str) -> str:
    groups = []
    exempt_groups = []
    for feature_id, name, lens, geometry in FEATURES:
        seam_y = SEAM_CONTINUATIONS.get(feature_id)
        seam = ""
        seam_attribute = ""
        if seam_y is not None:
            seam_attribute = ' data-seam="antimeridian"'
            seam = f'<path class="seam-continuation" d="M60 {seam_y - 10}L76 {seam_y}L60 {seam_y + 10}M1540 {seam_y - 10}L1524 {seam_y}L1540 {seam_y + 10}"/>'
        group = (
            f'<g id="shape-{feature_id}" class="feature-shape" data-id="{feature_id}" data-lens="{lens}" '
            f'tabindex="0" role="button"{seam_attribute} aria-label="Select {html.escape(name, quote=True)}">'
            f'<title>{html.escape(name)} · schematic {lens} geometry</title>{geometry}{seam}</g>'
        )
        (exempt_groups if feature_id in COAST_CLEARANCE_EXEMPT else groups).append(group)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="1050" viewBox="0 0 1600 1050" role="img" aria-labelledby="title desc">
  <title id="title">OSW selectable fluid feature shapes</title>
  <desc id="desc">Thirty-six schematic, selectable ocean feature shapes aligned to the interactive province map. Shapes indicate geographic form and mechanism but are not observed boundaries, centroids, or measured footprints.</desc>
  <defs>
    <marker id="flow-arrow" viewBox="0 0 12 12" refX="10" refY="6" markerWidth="8" markerHeight="8" orient="auto"><path d="M1 1L11 6L1 11Z" fill="#ffb454"/></marker>
    <pattern id="buried-pattern" width="14" height="14" patternUnits="userSpaceOnUse" patternTransform="rotate(28)"><rect width="14" height="14" fill="#8c7be7" fill-opacity=".19"/><path d="M0 0V14" stroke="#cfc6ff" stroke-width="3" stroke-opacity=".46"/></pattern>
    <pattern id="oxygen-pattern" width="13" height="13" patternUnits="userSpaceOnUse" patternTransform="rotate(-32)"><rect width="13" height="13" fill="#72d389" fill-opacity=".13"/><path d="M0 0V13" stroke="#9bea9f" stroke-width="2.5" stroke-opacity=".42"/></pattern>
    <mask id="feature-ocean-only" maskUnits="userSpaceOnUse" x="0" y="0" width="1600" height="1050">
      <rect x="60" y="90" width="1480" height="740" fill="white"/>
      <path d="{html.escape(land_path, quote=True)}" fill="black" stroke="black" stroke-width="10" stroke-linejoin="round" fill-rule="evenodd"/>
    </mask>
    <mask id="feature-ocean-gates" maskUnits="userSpaceOnUse" x="0" y="0" width="1600" height="1050">
      <rect x="60" y="90" width="1480" height="740" fill="white"/>
      <path d="{html.escape(land_path, quote=True)}" fill="black" fill-rule="evenodd"/>
    </mask>
  </defs>
  <style>
    .feature-shape {{ cursor:pointer; }} .feature-shape:focus {{ outline:none; }}
    .area {{ stroke-width:3; stroke-linejoin:round; }} .warm {{ fill:#ffb454; fill-opacity:.48; stroke:#ffd06b; }}
    .event {{ fill:#ff766c; fill-opacity:.28; stroke:#ff8d84; stroke-dasharray:11 8; }}
    .event-core {{ fill:none; stroke:#ffc0b8; stroke-width:2; stroke-dasharray:5 9; opacity:.72; }}
    .buried {{ fill:url(#buried-pattern); stroke:#b7a7ff; stroke-opacity:.75; stroke-width:2.5; stroke-dasharray:10 7; }}
    .cold-water {{ fill:#75cddd; fill-opacity:.22; stroke:#8eeaf2; }} .salty-water {{ fill:#c4a4ee; fill-opacity:.27; stroke:#d2bbf2; }}
    .hit {{ fill:none; stroke:transparent; stroke-width:28; }} .flow {{ fill:none; stroke:#ffb454; stroke-width:8; stroke-linecap:round; stroke-linejoin:round; marker-end:url(#flow-arrow); }}
    .cold-flow {{ stroke:#8eeaf2; stroke-dasharray:20 11; }}
    .gate-section {{ fill:none; stroke:#67e4da; stroke-width:7; stroke-linecap:round; }} .gate-bank {{ fill:none; stroke:#d6f7f1; stroke-width:3; }} .passage-cut {{ fill:none; stroke:#d6f7f1; stroke-width:4; stroke-linecap:round; }}
    .water-branch {{ fill:none; stroke:#8eeaf2; stroke-width:8; stroke-linecap:round; stroke-dasharray:17 10; opacity:.7; }} .water-core {{ fill:#c9f8fa; fill-opacity:.28; stroke:#d8ffff; stroke-width:2.4; }}
    .intermediate-arc {{ stroke-dasharray:16 8; }} .mode-water {{ fill-opacity:.16; stroke-dasharray:5 7; }} .convection-ring {{ fill:none; stroke:#d8ffff; stroke-width:3; stroke-dasharray:5 6; }}
    .salty-core {{ fill:none; stroke:#ead9ff; stroke-width:3; stroke-dasharray:9 6; }} .meddy {{ fill:none; stroke:#ead9ff; stroke-width:3; }}
    .gyre {{ fill:#ffb454; fill-opacity:.035; stroke:#ffb454; stroke-width:6; stroke-linecap:round; stroke-linejoin:round; stroke-dasharray:22 8; marker-end:url(#flow-arrow); }} .gyre-spine {{ fill:none; stroke:#ffd17b; stroke-width:10; stroke-linecap:round; opacity:.6; }}
    .front {{ fill:none; stroke:#67e4da; stroke-width:5; stroke-dasharray:17 9; }} .front-companion {{ fill:none; stroke:#a6f4ed; stroke-width:2; stroke-dasharray:4 8; opacity:.7; }}
    .divergence {{ fill:none; stroke:#67e4da; stroke-width:5; stroke-dasharray:13 8; }} .divergence-arrow {{ fill:none; stroke:#b8fff7; stroke-width:3; stroke-linecap:round; }}
    .ridge {{ fill:none; stroke:#a8bdba; stroke-width:8; stroke-dasharray:3 7; }} .ridge-flank {{ fill:none; stroke:#d5e0dc; stroke-width:3; opacity:.72; }}
    .trench {{ fill:none; stroke:#93aaa9; stroke-width:7; }} .trench-teeth {{ fill:none; stroke:#d5e0dc; stroke-width:3; stroke-linecap:round; }}
    .plateau {{ fill:#a8bdba; fill-opacity:.22; stroke:#d5e0dc; stroke-width:4; }} .plateau-contour {{ fill:none; stroke:#e3ece8; stroke-width:2.5; opacity:.75; }} .plateau-contour.inner {{ stroke-dasharray:5 5; }}
    .oxygen-zone {{ fill:url(#oxygen-pattern); stroke:#9bea9f; }} .oxygen-core {{ fill:none; stroke:#d0ffd3; stroke-width:2.5; stroke-dasharray:4 7; }}
    .sargasso {{ fill:#72d389; fill-opacity:.16; stroke:#9bea9f; stroke-dasharray:14 8; }} .sargasso-boundary {{ fill:none; stroke:#c1f5bc; stroke-width:2.5; }} .sargasso-swirl {{ fill:none; stroke:#d7ffd2; stroke-width:3; }}
    .seam-continuation {{ fill:none; stroke:#fff4d7; stroke-width:4; stroke-linecap:round; stroke-linejoin:round; opacity:.85; }}
    .feature-shape:hover > :not(title):not(.hit),.feature-shape:focus > :not(title):not(.hit),.feature-shape.selected > :not(title):not(.hit) {{ filter:drop-shadow(0 0 7px #fff4d7); stroke:#fff4d7; }}
    .feature-shape[hidden] {{ display:none; }}
  </style>
  <g aria-label="Selectable conceptual feature shapes" mask="url(#feature-ocean-only)">{''.join(groups)}</g>
  <g aria-label="Coastal gates exempt from visual clearance" mask="url(#feature-ocean-gates)">{''.join(exempt_groups)}</g>
</svg>'''


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parents[1] / "figures" / "osw-atlas-feature-shapes.svg")
    parser.add_argument("--province-map", type=Path, default=Path(__file__).resolve().parents[1] / "figures" / "osw-province-atlas-interactive.svg")
    args = parser.parse_args()
    args.output.write_text(build_svg(load_land_path(args.province_map)), encoding="utf-8", newline="\n")
    print(args.output)


if __name__ == "__main__":
    main()
