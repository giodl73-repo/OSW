//! Source-defined Nordic sections preserve alternate operators and identity scope.
use serde_json::{Value, json};
use sha2::{Digest, Sha256};

pub const NOR_PATH: &str = "research/norwegian-fer-2020-gimsoy-width-scope-audit.json";
pub const NOR_RAW: &str =
    include_str!("../../../research/norwegian-fer-2020-gimsoy-width-scope-audit.json");
pub const WSC_PATH: &str =
    "research/west-spitsbergen-kolas-2018-stream-tube-width-scope-audit.json";
pub const WSC_RAW: &str = include_str!(
    "../../../research/west-spitsbergen-kolas-2018-stream-tube-width-scope-audit.json"
);
const OLD_PATH: &str = "research/norwegian-atlantic-branch-width-scope-audit.json";
const OLD_RAW: &str =
    include_str!("../../../research/norwegian-atlantic-branch-width-scope-audit.json");
const SOURCES: &[(&str, &str, &str)] = &[
    ("norwegian-atlantic-slope", NOR_PATH, NOR_RAW),
    ("west-spitsbergen", WSC_PATH, WSC_RAW),
];

fn expected(path: &str, raw: &str) -> Vec<Value> {
    let audit: Value = serde_json::from_str(raw).expect("reviewed Nordic source");
    audit["measurements"]
        .as_array()
        .unwrap()
        .iter()
        .enumerate()
        .map(|(i, r)| {
            let mut row = r.clone();
            let context = if path == WSC_PATH {
                "stream_tube_context"
            } else {
                "original_regional_context"
            };
            row[context]["audit_file"] = json!(path);
            row[context]["audit_sha256"] = json!(format!("{:x}", Sha256::digest(raw.as_bytes())));
            if path == NOR_PATH {
                row[context]["audit_pointer"] = json!(format!("/measurements/{i}"));
                row["source_file"] = json!(path);
                row["source_pointer"] = json!(format!("/measurements/{i}"));
            }
            row
        })
        .collect()
}

fn proposed_rows() -> Vec<Value> {
    let doc: Value = serde_json::from_str(OLD_RAW).unwrap();
    let mut rows = doc["measurements"].as_array().unwrap().clone();
    for (i, r) in rows.iter_mut().enumerate() {
        r["source_file"] = json!(OLD_PATH);
        r["source_pointer"] = json!(format!("/measurements/{i}"));
    }
    rows.extend(expected(NOR_PATH, NOR_RAW));
    rows
}
pub fn validate(bundle: &crate::Bundle) -> Result<(), String> {
    let wanted = proposed_rows();
    if bundle
        .collections
        .get("widths")
        .into_iter()
        .flatten()
        .any(|r| wanted.iter().any(|p| p["id"] == r["id"]))
    {
        return Err("Proposed branch width transferred to canonical inventory".into());
    }
    if bundle.manifest["input_sha256"].get(NOR_PATH).is_none()
        && !bundle.collections.contains_key("proposed_widths")
    {
        return Ok(());
    }
    for (path, raw) in [(NOR_PATH, NOR_RAW), (OLD_PATH, OLD_RAW)] {
        if bundle.manifest["input_sha256"][path] != format!("{:x}", Sha256::digest(raw.as_bytes()))
        {
            return Err("Proposed branch source definition changed".into());
        }
    }
    let rows = bundle
        .collections
        .get("proposed_widths")
        .ok_or("Missing proposed branch widths")?;
    let previous: Vec<_> = rows
        .iter()
        .filter(|r| !crate::nwasc_mean_core::owns(r))
        .collect();
    if json!(previous) != json!(wanted) {
        return Err("Proposed branch width records changed".into());
    }
    let receipt = &bundle.manifest["atlas_receipts"]["research/ocean-current-inventory-expansion-candidates.json"];
    let doc: Value = serde_json::from_str(
        receipt["source_json"]
            .as_str()
            .ok_or("Missing proposed identity receipt")?,
    )
    .map_err(|e| e.to_string())?;
    let proposal = doc["entries"]
        .as_array()
        .into_iter()
        .flatten()
        .find(|r| r["proposed_id"] == "norwegian-atlantic-slope")
        .ok_or("Missing proposed slope identity")?;
    if proposal["section_width_evidence"] != json!(expected(NOR_PATH, NOR_RAW))
        || proposal["section_width_scope_audit"]
            != json!({"file":NOR_PATH,"sha256":format!("{:x}",Sha256::digest(NOR_RAW.as_bytes()))})
    {
        return Err("Proposed section width owner binding changed".into());
    }
    Ok(())
}

pub fn scene(matches: &[&Value], corpus: &[Value]) -> Value {
    let mut panels = vec![];
    for (owner, path, raw) in SOURCES {
        let source = expected(path, raw);
        if !matches
            .iter()
            .any(|r| source.iter().any(|s| r["id"] == s["id"]))
        {
            continue;
        }
        let rows: Vec<_> = source
            .iter()
            .filter_map(|r| corpus.iter().find(|s| s["id"] == r["id"]))
            .collect();
        let wsc = *owner == "west-spitsbergen";
        let height = if wsc { 535 } else { 300 };
        let title = if wsc {
            "West Spitsbergen Current · source-defined section widths"
        } else {
            "Proposed Norwegian Atlantic Slope Current · Gimsøy section span"
        };
        let subtitle = if wsc {
            "August 2015 · 3 sections × 2 methods; no annual width range"
        } else {
            "Four occupations, 2016–2017 · characteristic range; no midpoint or annual extrema"
        };
        let mut marks = String::new();
        for (i, row) in rows.iter().enumerate() {
            let y = 110 + i * 52;
            let context = if wsc {
                json!({"section":row["stream_tube_context"]["section_id"],"tube":row["stream_tube_context"]["stream_tube"]})
            } else {
                row["original_regional_context"].clone()
            };
            let range = if wsc && context["tube"] == 1 {
                let mut values = vec![row["approximate_width_km"].as_i64().unwrap()];
                values.extend(
                    row["stream_tube_context"]["threshold_sensitivity_cases"]
                        .as_array()
                        .unwrap()
                        .iter()
                        .map(|r| r["width_km"].as_i64().unwrap()),
                );
                json!([
                    values.iter().copied().fold(i64::MAX, i64::min),
                    values.iter().copied().fold(i64::MIN, i64::max)
                ])
            } else {
                row["width_range_km"].clone()
            };
            let label = if wsc {
                format!(
                    "{} · {}",
                    context["section"].as_str().unwrap(),
                    if context["tube"] == 1 {
                        "threshold tube 1"
                    } else {
                        "transport tube 2"
                    }
                )
            } else {
                "20% relative-geostrophic span".into()
            };
            let matching = matches.iter().any(|r| r["id"] == row["id"]);
            let opacity = if matching { 1.0 } else { 0.35 };
            marks.push_str(&format!(
                "<g opacity='{opacity}'><text x='20' y='{}' font-size='15'>{label}</text>",
                y + 5
            ));
            let x = |v: f64| 260. + v * 7.;
            if let Some(range) = range.as_array() {
                let a = range[0].as_f64().unwrap();
                let b = range[1].as_f64().unwrap();
                marks.push_str(&format!("<path d='M{:.2} {y}H{:.2} M{:.2} {}v18 M{:.2} {}v18' fill='none' stroke='#08798b' stroke-width='3' stroke-dasharray='5 3'/>",x(a),x(b),x(a),y-9,x(b),y-9));
            }
            if let Some(value) = row["approximate_width_km"].as_f64() {
                let px = x(value);
                if context["tube"] == 2 {
                    marks.push_str(&format!(
                        "<rect x='{:.2}' y='{}' width='12' height='12' fill='#8c5e20'/>",
                        px - 6.,
                        y - 6
                    ));
                } else {
                    marks.push_str(&format!(
                        "<circle cx='{px:.2}' cy='{y}' r='6' fill='#08798b'/>"
                    ));
                }
            }
            let caption = if let Some(range) = range.as_array() {
                if let Some(value) = row["approximate_width_km"].as_i64() {
                    format!("{value} km [{}–{}]", range[0], range[1])
                } else {
                    format!("{}–{} km", range[0], range[1])
                }
            } else {
                format!("{} km", row["approximate_width_km"])
            };
            let edge = range[1]
                .as_f64()
                .or(row["approximate_width_km"].as_f64())
                .unwrap();
            marks.push_str(&format!(
                "<text x='{:.2}' y='{}'>{caption}</text></g>",
                x(edge) + 14.,
                y + 5
            ));
        }
        let axis_y = if wsc { 425 } else { 165 };
        let ticks: String = (0..=7)
            .map(|i| {
                format!(
                    "<text x='{}' y='{}' text-anchor='middle'>{}</text>",
                    260 + i * 70,
                    axis_y + 24,
                    i * 10
                )
            })
            .collect();
        let note = if wsc {
            "Circles: primary 0.04 m/s. Dashed spans: 0.02–0.08 m/s sensitivity, not errors."
        } else {
            "Surface-pressure reference; exact width integration depth limits unspecified."
        };
        let extra = if wsc {
            "Squares: alternate ~1.3 Sv tube. Its 10% flux tolerance is not width uncertainty."
        } else {
            "20.1 km effective transport width and its assumed 4 km error are separate quantities."
        };
        let footer = if wsc {
            "Kolås &amp; Fer (2018), Table 2, p1611 · CC BY 4.0 · independent OSW plot"
        } else {
            "Fer et al. (2020), p692 · CC BY 4.0 · proposed slope branch; no canonical transfer"
        };
        let svg = format!(
            "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 900 {height}' role='img' aria-label='{title}. {subtitle}. {note} {extra}'><rect width='900' height='{height}' fill='#f7faf9'/><g font-family='sans-serif' font-size='17' fill='#123541'><text x='20' y='32' font-size='23'>{title}</text><text x='20' y='62'>{subtitle}</text>{marks}<path d='M260 {axis_y}H750' stroke='#9badb3'/>{ticks}<text x='785' y='{}'>km</text><text x='20' y='{}' font-size='16'>{note}</text><text x='20' y='{}' font-size='16'>{extra}</text><text x='20' y='{}' font-size='14'>{footer}</text></g></svg>",
            axis_y + 24,
            axis_y + 52,
            axis_y + 77,
            height - 12
        );
        let audit: Value = serde_json::from_str(raw).unwrap();
        let url = audit
            .get("source_url")
            .unwrap_or(&audit["measurements"][0]["source_url"]);
        panels.push(json!({"id":owner,"title":title,"svg":svg,"source_file":path,"source_url":url,
            "collection":if wsc {"widths"} else {"proposed_widths"},
            "rows":rows.iter().map(|r|json!({"id":r["id"],"label":r["phase_label"],
                "source_pointer":format!("/measurements/{}",source.iter().position(|s|s["id"]==r["id"]).unwrap()),
                "matching":matches.iter().any(|s|s["id"]==r["id"])})).collect::<Vec<_>>() }));
    }
    panels.extend(crate::nwasc_mean_core::panels(matches, corpus));
    if panels.is_empty() {
        return Value::Null;
    }
    json!({"kind":"nordic_section_widths","title":"Source-defined Nordic section widths","panels":panels,
        "scope":"WSC comparisons reuse the six existing source records. Norwegian slope widths belong to a proposed identity; no dimensions transfer to ambiguous Norwegian Current, Norwegian Coastal Current or historical Spitsbergen Atlantic Current. Three WSC sections use two alternate operators, not six independent occupations. Each panel preserves its own vertical and temporal support. No geographic edges, numerical width uncertainty or annual extrema inferred. Faded rows preserve source-method context outside the filter."})
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn filtered_wsc_preserves_six_method_rows_and_primary_point() {
        let rows = expected(WSC_PATH, WSC_RAW);
        let scene = scene(&[&rows[2]], &rows);
        assert_eq!(scene["panels"][0]["rows"].as_array().unwrap().len(), 6);
        assert_eq!(scene["panels"][0]["rows"][2]["matching"], true);
        assert_eq!(scene["panels"][0]["rows"][3]["matching"], false);
        assert!(
            scene["panels"][0]["svg"]
                .as_str()
                .unwrap()
                .contains("21 km [11–24]")
        );
        assert!(super::scene(&[], &rows).is_null());
    }
}
