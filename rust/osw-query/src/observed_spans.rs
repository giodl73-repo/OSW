//! Checked local shipboard component spans; not whole-current widths.
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
pub const SOURCE: &str = "research/antilles-ab0505-sadcp-layer-span-diagnostics.json";
const RAW: &str =
    include_str!("../../../research/antilles-ab0505-sadcp-layer-span-diagnostics.json");

pub fn validate(bundle: &crate::Bundle) -> Result<(), String> {
    if bundle.manifest["input_sha256"].get(SOURCE).is_none()
        && !bundle.collections.contains_key("observed_section_spans")
        && !bundle
            .collections
            .get("objects")
            .into_iter()
            .flatten()
            .any(|r| r["id"] == "current:antilles")
    {
        return Ok(());
    }
    let expected: Value = serde_json::from_str(RAW).map_err(|e| e.to_string())?;
    let rows = bundle
        .collections
        .get("observed_section_spans")
        .ok_or("Missing observed section spans")?;
    if bundle.manifest["input_sha256"][SOURCE] != format!("{:x}", Sha256::digest(RAW.as_bytes()))
        || json!(rows) != expected["rows"]
    {
        return Err("Observed shipboard spans or source scope changed".into());
    }
    let owner = bundle
        .collections
        .get("objects")
        .into_iter()
        .flatten()
        .find(|r| r["id"] == "current:antilles")
        .ok_or("Missing shipboard span owner")?;
    if owner["observed_section_span_ids"]
        != json!(rows.iter().map(|r| r["id"].clone()).collect::<Vec<_>>())
    {
        return Err("Observed section span owner binding changed".into());
    }
    Ok(())
}

pub fn scene(matches: &[&Value]) -> Value {
    let panels: Vec<_> = matches.iter().map(|row| {
        let x = |lon: f64| 65.+(lon+76.9)/1.9*690.;
        let values: Vec<f64> = row["profile_bins"].as_array().unwrap().iter().filter_map(|b|b["northward_m_s"].as_f64()).collect();
        let low=values.iter().copied().fold(0.0,f64::min)-0.1;
        let high=values.iter().copied().fold(0.1,f64::max)+0.1;
        let y = |v: f64| 55.+(high-v)/(high-low)*210.;
        let mut path=String::new(); let mut connected=false;
        for b in row["profile_bins"].as_array().unwrap() {
            if let (Some(v),Some(lon))=(b["northward_m_s"].as_f64(),b["coordinates_lon_lat"][0].as_f64()) {
                path.push_str(&format!("{} {:.3},{:.3} ",if connected {"L"} else {"M"},x(lon),y(v)));
                connected=true;
            } else { connected=false; }
        }
        let c=&row["threshold_cases"][1]; let mut markers=String::new();
        if let Some(threshold)=c["threshold_m_s"].as_f64() {
            markers.push_str(&format!("<path d='M65 {:.3}H755' stroke='#a96b10' stroke-dasharray='4 4'/>",y(threshold)));
        }
        for side in ["shoreward_boundary","offshore_boundary"] {
            if let Some(lon)=c[side]["coordinates_lon_lat"][0].as_f64() {
                markers.push_str(&format!("<path d='M{:.3} 55V265' stroke='#a96b10' stroke-dasharray='3 3'/>",x(lon)));
            }
        }
        let depth=row["depth_m"].as_i64().unwrap();
        let value=if let Some(v)=row["half_peak_span_km"].as_f64() {format!("About {v} km local half-peak survey span")} else {"Paired span unresolved; not zero".into()};
        let zero=y(0.);
        let svg=format!("<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 820 325' role='img' aria-label='Northward component profile at {depth} m; gaps remain disconnected, dashed markers are diagnostic threshold crossings, not physical current edges.'><rect width='820' height='325' fill='#f7faf9'/><g font-family='sans-serif' font-size='17' fill='#123541'><text x='30' y='30'>{value}</text><path d='M65 55V265H755 M65 {zero:.3}H755' fill='none' stroke='#9badb3'/><text x='8' y='65'>{high:.1}</text><text x='8' y='265'>{low:.1}</text><text x='8' y='170'>m/s</text><text x='65' y='294'>76.9 W</text><text x='695' y='294'>75.0 W</text><text x='265' y='320'>Longitude; source latitude strip 26.4–26.6 N</text><path d='{path}' fill='none' stroke='#08798b' stroke-width='3'/>{markers}</g></svg>");
        json!({"id":row["id"],"title":row["label"],"svg":svg,
            "depth_m":depth,"source_file":SOURCE,"source_pointer":row["source_pointer"],
            "half_peak_span_km":row["half_peak_span_km"],"threshold_span_range_km":row["threshold_span_range_km"],
            "complete_threshold_envelope":row["complete_threshold_envelope"],
            "valid_sample_period":row["valid_sample_period"],"paired_observation_count":row["paired_observation_count"]})
    }).collect();
    json!({"kind":"observed_section_spans","panels":panels,
        "scope":"Paired local northward-component survey spans of spatial-bin medians. No gap bridging, coast-zero assumption, verified current association, flow-normal/full-current width, confidence error or annual range. Provider clock time zone and tidal correction are unspecified. 16 m native vertical bins; 10 m exported spacing is not native resolution."})
}
