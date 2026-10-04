//! Source-defined seasonal route phases; never exact-date observations.
use serde::Deserialize;
use serde_json::Value;
use std::collections::BTreeMap;

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
pub struct SeasonalSelection {
    pub month: Option<u8>,
    pub phase_id: Option<String>,
}
impl SeasonalSelection {
    pub fn validate(&self, collections: &BTreeMap<String, Vec<Value>>) -> Result<(), String> {
        if self.month.is_some() == self.phase_id.is_some() {
            return Err("Select exactly one seasonal month or phase_id".into());
        }
        if self.month.is_some_and(|m| !(1..=12).contains(&m)) {
            return Err("Seasonal month must be 1..12".into());
        }
        if let Some(id) = &self.phase_id {
            if !collections
                .get("seasonal_routes")
                .is_some_and(|rs| rs.iter().any(|r| r["id"].as_str() == Some(id)))
            {
                return Err(format!("Unknown seasonal phase {id}"));
            }
        }
        Ok(())
    }
    pub fn includes(&self, feature: &Value) -> bool {
        if feature["phase_id"].as_str().is_none() {
            return false;
        }
        if let Some(id) = &self.phase_id {
            return feature["phase_id"].as_str() == Some(id);
        }
        feature["calendar_months"]
            .as_array()
            .is_some_and(|ms| ms.iter().any(|m| m.as_u64() == self.month.map(u64::from)))
    }
}

pub fn validate_features(collections: &BTreeMap<String, Vec<Value>>) -> Result<(), String> {
    for phase in collections.get("seasonal_routes").into_iter().flatten() {
        if let Some(months) = phase.get("calendar_months").filter(|v| !v.is_null()) {
            let months = months.as_array().ok_or("Invalid seasonal calendar")?;
            let unique: std::collections::BTreeSet<_> =
                months.iter().filter_map(Value::as_u64).collect();
            if months.is_empty()
                || unique.len() != months.len()
                || unique.iter().any(|m| !(1..=12).contains(m))
            {
                return Err("Invalid seasonal calendar".into());
            }
        } else if phase.get("calendar_months").is_none() {
            return Err("Missing seasonal calendar support".into());
        }
        if phase["comparability"]["annual_extrema_eligible"] != false
            || !phase["comparability"]["annual_length_range_km"].is_null()
            || !phase["comparability"]["annual_width_range_km"].is_null()
        {
            return Err("Seasonal regional phases cannot define annual extrema".into());
        }
    }
    for object in &collections["objects"] {
        for feature in object["map_features"].as_array().into_iter().flatten() {
            if let Some(id) = feature.get("phase_id") {
                let phase = collections
                    .get("seasonal_routes")
                    .and_then(|rs| rs.iter().find(|r| r["id"] == *id))
                    .ok_or("Unresolved seasonal map phase")?;
                if feature["geometry"]["type"] != "LineString"
                    || phase["entity_id"] != object["id"]
                    || phase["coordinates_lon_lat"] != feature["geometry"]["coordinates"]
                    || !feature["observation_date"].is_null()
                {
                    return Err("Seasonal phase geometry/owner/date mismatch".into());
                }
                for (a, b) in [
                    ("geometry_role", "role"),
                    ("calendar_months", "calendar_months"),
                    ("phase_label", "phase_label"),
                    ("flow_direction", "flow_direction"),
                    ("source_url", "source_url"),
                    ("source_locator", "source_locator"),
                    ("time_convention", "time_convention"),
                    ("layer", "layer"),
                    ("route_candidate_sha256", "route_candidate_sha256"),
                    ("seasonal_inventory_sha256", "seasonal_inventory_sha256"),
                    ("comparability", "comparability"),
                ] {
                    if phase[a] != feature[b] {
                        return Err(format!("Seasonal phase {id} differs in {a}"));
                    }
                }
            }
        }
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;
    #[test]
    fn month_support_and_named_unknown_phase() {
        let month = SeasonalSelection {
            month: Some(1),
            phase_id: None,
        };
        assert!(month.includes(&json!({"phase_id":"winter","calendar_months":[12,1,2]})));
        assert!(!month.includes(&json!({"phase_id":"unknown","calendar_months":null})));
        assert!(!month.includes(&json!({"calendar_months":[1]})));
        let named = SeasonalSelection {
            month: None,
            phase_id: Some("unknown".into()),
        };
        assert!(named.includes(&json!({"phase_id":"unknown","calendar_months":null})));
        for bad in [
            json!({}),
            json!({"month":0}),
            json!({"month":13}),
            json!({"month":1,"phase_id":"unknown"}),
        ] {
            let selection: SeasonalSelection = serde_json::from_value(bad).unwrap();
            assert!(selection.validate(&BTreeMap::new()).is_err());
        }
    }
    #[test]
    fn bound_source_phase_rejects_geometry_calendar_and_date_tampering() {
        let phase = json!({"id":"p","entity_id":"a","geometry_role":"osw_editorial_reference_route","calendar_months":[12,1,2],"coordinates_lon_lat":[[0,0],[1,1]],"source_url":"https://example.org/source","comparability":{"annual_extrema_eligible":false,"annual_length_range_km":null,"annual_width_range_km":null}});
        let mut feature = phase.clone();
        feature["phase_id"] = json!("p");
        feature["role"] = phase["geometry_role"].clone();
        feature["geometry"] =
            json!({"type":"LineString","coordinates":phase["coordinates_lon_lat"]});
        let original = json!({"schema":"osw.query-bundle.v1","manifest":{},"collections":{"objects":[{"id":"a","seasonal_route_ids":["p"],"map_features":[feature]}],"states":[],"seasonal_routes":[phase]}});
        assert!(crate::Store::load(original.to_string().as_bytes()).is_ok());
        for (path, value) in [
            (
                "/collections/objects/0/map_features/0/observation_date",
                json!("2025-01-15"),
            ),
            (
                "/collections/objects/0/map_features/0/geometry/type",
                json!("Point"),
            ),
            (
                "/collections/objects/0/map_features/0/source_url",
                json!("changed"),
            ),
            ("/collections/seasonal_routes/0/calendar_months", json!([0])),
            ("/collections/seasonal_routes/0/entity_id", json!("other")),
        ] {
            let mut bad = original.clone();
            if path.ends_with("observation_date") {
                bad["collections"]["objects"][0]["map_features"][0]["observation_date"] = value;
            } else {
                *bad.pointer_mut(path).unwrap() = value;
            }
            assert!(
                crate::Store::load(bad.to_string().as_bytes()).is_err(),
                "{path}"
            );
        }
        let store = crate::Store::load(original.to_string().as_bytes()).unwrap();
        assert_eq!(store.execute(br#"{"seasonal":{"month":1}}"#)["total"], 1);
        assert_eq!(store.execute(br#"{"seasonal":{"month":4}}"#)["total"], 0);
    }
}
