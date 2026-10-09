//! Historical float subsets preserve their own errors and sampling limitations.
use crate::Bundle;
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
const SOURCE: &str = "research/dwbc-richardson-1993-upper-core-width-scope-audit.json";
const RAW: &str =
    include_str!("../../../research/dwbc-richardson-1993-upper-core-width-scope-audit.json");
const ID: &str = "deep-western-boundary-richardson-1993-upper-core-zero-width";
pub(crate) fn validate(bundle: &Bundle) -> Result<(), String> {
    let empty = vec![];
    let rows = bundle.collections.get("widths").unwrap_or(&empty);
    if bundle.manifest["input_sha256"][SOURCE].is_null() && !rows.iter().any(|r| r["id"] == ID) {
        return Ok(());
    }
    if bundle.manifest["input_sha256"][SOURCE] != format!("{:x}", Sha256::digest(RAW.as_bytes())) {
        return Err("DWBC float composite audit mismatch".into());
    }
    if rows.iter().filter(|r| r["id"] == ID).count() != 1 {
        return Err("DWBC float composite inventory incomplete".into());
    }
    Ok(())
}
pub(crate) fn scene(matches: &[&Value], corpus: &[Value]) -> Value {
    if !matches.iter().any(|r| r["id"] == ID) {
        return Value::Null;
    }
    let Some(row) = corpus.iter().find(|r| r["id"] == ID) else {
        return Value::Null;
    };
    let c = &row["original_regional_context"];
    let extent = c["source_figure_view_extent_lon_lat"].as_array().unwrap();
    let project = |lon: f64, lat: f64| {
        crate::cartography::root(crate::map::point(&json!([lon, lat])).unwrap())
    };
    let (left, top) = project(extent[0].as_f64().unwrap(), extent[3].as_f64().unwrap());
    let (right, bottom) = project(extent[2].as_f64().unwrap(), extent[1].as_f64().unwrap());
    let latitudes: Vec<_> = [-5, 0, 5, 10, 15]
        .iter()
        .map(|lat| json!({"latitude":lat,"y":project(-55.0,*lat as f64).1}))
        .collect();
    let longitudes: Vec<_> = [-55, -45, -35, -25, -10]
        .iter()
        .map(|lon| json!({"longitude":lon,"x":project(*lon as f64,0.0).0}))
        .collect();
    let source = c["source_table_rows"]
        .as_array()
        .expect("reviewed source table");
    let panels:Vec<_>=[("maximum_bin_average_velocity_cm_s","maximum_bin_average_standard_error_cm_s",50.0,"Maximum 10 km bin-average speed","cm/s"),
        ("transport_per_unit_depth_10_3_m2_s","transport_per_unit_depth_standard_error_10_3_m2_s",30.0,"Transport per unit depth","10^3 m2/s")]
        .iter().map(|(key,error,max,title,unit)|{
            let points:Vec<_>=source.iter().enumerate().map(|(i,r)|{
                let v=r[*key].as_f64().unwrap();let e=r[*error].as_f64().unwrap();
                json!({"source_row":i,"label":r["period_label"],"value":v,"standard_error":e,"x":270.0+v/max*420.0,"x_low":270.0+(v-e)/max*420.0,"x_high":270.0+(v+e)/max*420.0,"y":48+i*50})
            }).collect();
            json!({"title":title,"unit":unit,"axis_max":max,"view_box":[0,0,760,280],"points":points,"ticks":[0.0,max/2.0,*max]})
        }).collect();
    json!({"kind":"dwbc_float_composite","title":"DWBC upper-core float composite",
        "scope":"Historical, nonuniform Lagrangian sampling at nominal drifting 1800 m. One composite overlaps three unequal subsets; this is not a seasonal cycle or an annual width range.",
        "width_view_box":[0,0,760,115],"width_point":{"x":60.0+640.0/150.0*100.0,"y":44,"value_km":row["approximate_width_km"]},"width_ticks":[0,50,100,150],
        "width_caption":c["display_caption"],"panels":panels,"table":source,"record":row,
        "geographic_view":{"view_box":[left,top,right-left,bottom-top],"extent_lon_lat":extent,"projection":"OSW equirectangular display","role":c["geographic_view_role"],"latitudes":latitudes,"longitudes":longitudes,"caption":"Tropical float-study geography, using the longitude/latitude frame of source Figure 2 and the OSW basemap. No float trajectories, current axis or width boundaries reconstructed. A view frame is not a physical current footprint. The existing North Atlantic reference reach is separate."},
        "uncertainty_note":"Whiskers below are the published standard errors of maximum bin-average speed and transport per unit depth. They are not width errors or confidence intervals. Individual float peak speeds are separate table values.",
        "depth_note":"Active depth control and pressure/temperature reporting failed. Nominal 1800 m floats were estimated to sink about 230 m over 21 months; no fixed depth layer is admitted.",
        "sampling_notes":[c["source_scope_discrepancy_note"],c["subset_count_discrepancy_note"],c["source_sampling_gap_label"],c["first_subset_sampling_qualification"]],
        "transport_note":"Table 2 rounds composite transport per unit depth to 14 +/-3; prose gives 13.8 and an alternative subset-based standard error about 4. Total volume transport 15 Sv rounds a 14.7 Sv construction that couples floats with an independent mooring, an assumed elliptical shape and 900-2800 m integration. These are not width-layer bounds; no subset total Sv values supplied.",
        "source_url":row["source_url"],"source_citation":row["source_citation"],"audit_file":SOURCE})
}
pub(crate) fn full(corpus: &[Value]) -> Value {
    let matches: Vec<_> = corpus.iter().filter(|r| r["id"] == ID).collect();
    scene(&matches, corpus)
}
#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn source_errors_and_unequal_subsets_do_not_become_width_uncertainty() {
        let audit: Value = serde_json::from_str(RAW).unwrap();
        let rows = vec![audit["measurement"].clone()];
        let s = full(&rows);
        assert_eq!(s["table"].as_array().unwrap().len(), 4);
        assert_eq!(s["width_point"]["value_km"], 100);
        assert_eq!(s["panels"][0]["points"][1]["value"], 39.0);
        assert_eq!(s["panels"][1]["points"][1]["standard_error"], 4.0);
        assert_eq!(s["record"]["uncertainty_km"], Value::Null);
        assert_eq!(
            s["record"]["original_regional_context"]["subset_observation_count_sum"],
            489
        );
        assert!(full(&[]).is_null());
    }
}
