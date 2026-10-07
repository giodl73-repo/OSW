//! Provider detection display only; no metric dimensions or containment inferred.
use serde_json::{Value, json};
pub fn scene(geometry: &Value, center: &Value) -> Value {
    fitted(geometry, center, false)
}
pub fn named_scene(geometry: &Value) -> Value {
    fitted(geometry, &Value::Null, true)
}
fn fitted(geometry: &Value, center: &Value, named: bool) -> Value {
    let (label, kind, role, width, span_x, span_y, mid_y) = if named {
        (
            "Figure-derived contour candidate",
            "named_eddy",
            "figure_digitized_instantaneous_ssh_contour_proxy",
            500,
            430.,
            255.,
            162.5,
        )
    } else {
        (
            "Provider detection",
            "operational_eddy_detection",
            "dated_operational_eddy_polygon",
            600,
            480.,
            250.,
            165.,
        )
    };
    let mut record = json!({"id":geometry["entity_id"],"label":label,"type":kind,
      "map_features":[{"geometry":geometry["geometry"],"role":role,"observation_date":geometry["observation_date"]}]});
    if !center.is_null() {
        record["map_features"].as_array_mut().unwrap().push(
            json!({"geometry":{"type":"Point","coordinates":center},"role":"provider_center"}),
        );
    }
    let scene = crate::map::scene(&[&record]);
    let polygon = scene["features"]
        .as_array()
        .and_then(|fs| fs.iter().find(|f| f["primitive"]["kind"] == "polygon"));
    let Some(polygon) = polygon else {
        return json!({"available":false,"omitted_features":scene["omitted_features"],"reason":"Source polygon cannot be drawn without unsupported or invalid geometry."});
    };
    let points: Vec<_> = geometry["geometry"]["coordinates"]
        .as_array()
        .into_iter()
        .flatten()
        .flat_map(|r| r.as_array().into_iter().flatten())
        .collect();
    let west = points
        .iter()
        .filter_map(|p| p[0].as_f64())
        .fold(f64::INFINITY, f64::min);
    let east = points
        .iter()
        .filter_map(|p| p[0].as_f64())
        .fold(f64::NEG_INFINITY, f64::max);
    let south = points
        .iter()
        .filter_map(|p| p[1].as_f64())
        .fold(f64::INFINITY, f64::min);
    let north = points
        .iter()
        .filter_map(|p| p[1].as_f64())
        .fold(f64::NEG_INFINITY, f64::max);
    if east <= west || north <= south {
        return json!({"available":false,"reason":"Source polygon has no finite two-dimensional display extent.","omitted_features":scene["omitted_features"]});
    }
    let scale = (span_x / (east - west)).min(span_y / (north - south));
    let tx = width as f64 / 2. - ((west + east) / 2. + 180.) * scale;
    let ty = mid_y - (90. - (south + north) / 2.) * scale;
    let marker = scene["features"]
        .as_array()
        .and_then(|fs| fs.iter().find(|f| f["primitive"]["kind"] == "point"))
        .map(|f| {
            let x = tx + f["primitive"]["x"].as_f64().unwrap() * scale;
            let y = ty + f["primitive"]["y"].as_f64().unwrap() * scale;
            format!("M{},{}h10 M{},{}v10", x - 5., y, x, y - 5.)
        });
    let date = geometry["observation_date"]
        .as_str()
        .unwrap_or("date unresolved");
    let aria = if named {
        format!(
            "Figure-derived SSH contour candidate for {date}. Longitude {west:.2} to {east:.2}, latitude {south:.2} to {north:.2}. State assessments follow in text."
        )
    } else {
        format!(
            "NAVO dated polygon, {date}. Longitude {west:.3} to {east:.3} degrees; latitude {south:.3} to {north:.3} degrees. Exact datum unspecified. State containment is described in the text below."
        )
    };
    json!({"available":true,"projection":scene["projection"],"view_box":[0,0,width,350],"geographic_bounds":[west,south,east,north],
  "polygon_d":polygon["primitive"]["d"],"display_transform":format!("translate({tx} {ty}) scale({scale})"),"center_d":marker,
  "observation_date":date,"title":if named {format!("{date} · Figure-derived SSH contour candidate")} else {format!("{date} · full source polygon")},"longitude_label":format!("{west:.3}° to {east:.3}° longitude"),
  "latitude_label":format!("{south:.3}° to {north:.3}° latitude · north is up"),
  "aria_label":aria,
  "coordinate_label":format!("Longitude {west:.3} to {east:.3} degrees; latitude {south:.3} to {north:.3} degrees. North is up. Equal angular longitude/latitude plot; no coastline or state boundary is drawn."),
  "omitted_features":scene["omitted_features"],"scope":if named {"Figure-derived instantaneous SSH contour proxy; scientific claim review pending. No coastline or state boundary is drawn; whole-ring containment remains unresolved."} else {"Equal angular longitude/latitude plot. Outline: provider polygon; cross: provider center. No coastline or state boundary is drawn. Exact datum and positional uncertainty are unspecified; this is not a permanent eddy extent."}})
}
#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn source_plot_omits_seams_and_degenerate_extents() {
        let geo = |coords| json!({"entity_id":"detection:example","observation_date":"2026-09-25","geometry":{"type":"Polygon","coordinates":[coords]}});
        let square = scene(
            &geo(json!([[1., 1.], [3., 1.], [3., 3.], [1., 1.]])),
            &json!([2., 2.]),
        );
        assert_eq!(square["geographic_bounds"], json!([1., 1., 3., 3.]));
        assert!(square["center_d"].is_string());
        assert!(square["available"].as_bool().unwrap());
        let no_center = scene(
            &geo(json!([[1., 1.], [3., 1.], [3., 3.], [1., 1.]])),
            &Value::Null,
        );
        assert!(no_center["center_d"].is_null());
        assert!(no_center["omitted_features"].as_array().unwrap().is_empty());
        let named = named_scene(&geo(json!([[1., 1.], [3., 1.], [3., 3.], [1., 1.]])));
        assert_eq!(named["view_box"], json!([0, 0, 500, 350]));
        assert!(named["center_d"].is_null());
        assert!(named["aria_label"].as_str().unwrap().contains("candidate"));
        assert_eq!(
            named_scene(&geo(json!([
                [179., 1.],
                [-179., 1.],
                [-179., 3.],
                [179., 1.]
            ])))["available"],
            false
        );
        assert_eq!(
            scene(
                &geo(json!([[179., 1.], [-179., 1.], [-179., 3.], [179., 1.]])),
                &Value::Null
            )["available"],
            false
        );
        assert_eq!(
            scene(
                &geo(json!([[1., 1.], [1., 2.], [1., 3.], [1., 1.]])),
                &Value::Null
            )["available"],
            false
        );
    }
}
