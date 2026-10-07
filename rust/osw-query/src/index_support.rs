//! Source reconciliation and display metrics retain their original claim scope.
use crate::index_store::IndexStore;
use serde::Deserialize;
use serde_json::{Value, json};

impl IndexStore {
    fn support_source(&self, path: &str) -> Result<&Value, String> {
        self.documents
            .get(path)
            .ok_or_else(|| format!("Missing index support source {path}"))
    }
    pub fn support_view(&self, bytes: &[u8]) -> Result<Value, String> {
        #[derive(Deserialize)]
        #[serde(deny_unknown_fields)]
        struct Request {
            section: String,
            text: Option<String>,
            filter: Option<String>,
            state_code: Option<String>,
        }
        let r: Request = serde_json::from_slice(bytes).map_err(|e| e.to_string())?;
        let names = self.support_source("research/ocean-current-almanac.json")?["entries"]
            .as_array()
            .ok_or("Missing current ledger")?;
        let resolve = |id: &Value| {
            names
                .iter()
                .find(|v| v["id"] == *id)
                .ok_or_else(|| "Unresolved source current".to_string())
        };
        match r.section.as_str() {
            "reconciliation" => {
                if r.state_code.is_some() {
                    return Err("State selection is not supported for source names".into());
                }
                let filter = r.filter.as_deref().unwrap_or("all");
                if !["all", "matched", "excluded", "candidate_needs_review"].contains(&filter) {
                    return Err("Unknown reconciliation filter".into());
                }
                let text = r.text.unwrap_or_default().trim().to_lowercase();
                let source = "research/marine-regions-current-crosswalk.json";
                let doc = self.support_source(source)?;
                let records = doc["records"].as_array().ok_or("Missing source names")?;
                let mut rows = Vec::new();
                for (index, record) in records.iter().enumerate() {
                    let status = record["join_status"]
                        .as_str()
                        .ok_or("Missing reconciliation status")?;
                    let matched = status.starts_with("matched");
                    let excluded = !matched && status != "candidate_needs_review";
                    let current = if record["osw_current_id"].is_null() {
                        None
                    } else {
                        Some(resolve(&record["osw_current_id"])?)
                    };
                    if (filter == "matched" && !matched)
                        || (filter == "excluded" && !excluded)
                        || (filter == "candidate_needs_review" && status != filter)
                    {
                        continue;
                    }
                    let search = ["name", "source", "join_note", "review_note"]
                        .iter()
                        .map(|k| record[*k].as_str().unwrap_or(""))
                        .collect::<Vec<_>>()
                        .join(" ")
                        .to_lowercase();
                    if !search.contains(&text) {
                        continue;
                    }
                    let label = if matched {
                        if status == "matched_exact_name" {
                            "Exact name match"
                        } else {
                            "Alias to review"
                        }
                    } else if excluded {
                        "Other type"
                    } else {
                        "Needs review"
                    };
                    rows.push(
                        json!({"record":record,"current":current,"status_label":label,
                        "source":source,"source_pointer":format!("/records/{index}")}),
                    );
                }
                Ok(
                    json!({"ok":true,"section":r.section,"rows":rows,"total":doc["source_record_count"],
                    "method":doc["method"],"retrieved_utc":doc["retrieved_utc"]}),
                )
            }
            "illustrated_spans" => {
                if r.text.is_some() || r.filter.is_some() || r.state_code.is_some() {
                    return Err("Illustrated spans do not accept filters".into());
                }
                let source = "research/ocean-current-illustrated-spans.json";
                let doc = self.support_source(source)?;
                let mut rows = Vec::new();
                for (index, record) in doc["entries"]
                    .as_array()
                    .ok_or("Missing illustrated spans")?
                    .iter()
                    .enumerate()
                {
                    let current = resolve(&record["current_id"])?;
                    if record["illustrated_span_rank"].is_null() {
                        continue;
                    }
                    rows.push(json!({"record":record,"current":current,"source":source,
                        "source_pointer":format!("/entries/{index}")}));
                }
                Ok(
                    json!({"ok":true,"section":r.section,"rows":rows,"counts":doc["counts"],
                    "metric":doc["metric"],"ranking_rule":doc["ranking_rule"],"uncertainty":doc["uncertainty"]}),
                )
            }
            "diagnostic_samples" => {
                if r.text.is_some() || r.filter.is_some() {
                    return Err("Diagnostic samples require only a state".into());
                }
                let code = r.state_code.ok_or("Missing diagnostic state")?;
                if self.support_source("research/ocean-motion-state-join.json")?["states"]
                    .get(&code)
                    .is_none()
                {
                    return Err("Unknown diagnostic state".into());
                }
                let mut rows = Vec::new();
                for (year, source) in [
                    ("2025", "research/ocean-current-dated-timeline-2025.json"),
                    ("2026", "research/ocean-current-dated-timeline.json"),
                ] {
                    let doc = self.support_source(source)?;
                    if doc["schema"] != "osw.current-dated-timeline.v1"
                        || doc["current_id"] != "gulf-stream-system"
                    {
                        return Err("Invalid diagnostic sample set".into());
                    }
                    for (index, frame) in doc["frames"]
                        .as_array()
                        .ok_or("Missing diagnostic frames")?
                        .iter()
                        .enumerate()
                    {
                        for (relation_index, relation) in frame["state_relations"]
                            .as_array()
                            .ok_or("Missing diagnostic relations")?
                            .iter()
                            .enumerate()
                        {
                            if relation["state_code"].as_str() != Some(&code) {
                                continue;
                            }
                            rows.push(json!({"year":year,"frame":frame,"relation":relation,"source":source,
                                "source_pointer":format!("/frames/{index}/state_relations/{relation_index}"),
                                "atlas_url":format!("reference-routes.html?atlas-feature=current%3Agulf-stream-system&atlas-series={year}&atlas-date={}#route-atlas",frame["date"].as_str().ok_or("Missing diagnostic date")?)}));
                        }
                    }
                }
                Ok(
                    json!({"ok":true,"section":r.section,"state_code":code,"rows":rows,
                    "scope":"Partial diagnostic line intersections in approximate state shapes; no current footprint, containment, permanent passage or annual extrema."}),
                )
            }
            _ => Err("Unknown index support section".into()),
        }
    }
}
