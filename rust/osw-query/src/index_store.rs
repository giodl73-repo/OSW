//! Independently pinned index sources, queried without importing the main store.
use serde::Deserialize;
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
use std::collections::BTreeMap;

const CATALOG: &str = include_str!("../../../almanac/index-catalog.json");
#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct Bundle {
    schema: String,
    documents: BTreeMap<String, String>,
}
pub struct IndexStore {
    pub(crate) documents: BTreeMap<String, Value>,
    catalog: Value,
}
#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct Request {
    document: String,
    #[serde(default)]
    pointer: String,
    text: Option<String>,
    #[serde(default)]
    filters: Vec<crate::Filter>,
    sort: Option<crate::Sort>,
    limit: Option<usize>,
    #[serde(default)]
    offset: usize,
}
fn escaped(key: &str) -> String {
    key.replace('~', "~0").replace('/', "~1")
}
fn filtered(row: &Value, filter: &crate::Filter) -> Result<bool, String> {
    let value = crate::field(row, &filter.field);
    Ok(match filter.op.as_str() {
        "eq" => value == Some(&filter.value),
        "ne" => value != Some(&filter.value),
        "is_null" => value.is_none_or(Value::is_null),
        "not_null" => value.is_some_and(|v| !v.is_null()),
        "contains" => value.is_some_and(|v| {
            if let Some(a) = v.as_array() {
                a.contains(&filter.value)
            } else {
                v.as_str()
                    .zip(filter.value.as_str())
                    .is_some_and(|(a, b)| a.to_lowercase().contains(&b.to_lowercase()))
            }
        }),
        "gt" | "gte" | "lt" | "lte" => value
            .and_then(Value::as_f64)
            .zip(filter.value.as_f64())
            .is_some_and(|(a, b)| match filter.op.as_str() {
                "gt" => a > b,
                "gte" => a >= b,
                "lt" => a < b,
                _ => a <= b,
            }),
        _ => return Err("Unsupported index filter operator".into()),
    })
}
impl IndexStore {
    pub fn state_context_view(&self, bytes: &[u8]) -> Result<Value, String> {
        #[derive(Deserialize)]
        #[serde(deny_unknown_fields)]
        struct Selection {
            state_code: Option<String>,
            state_codes: Option<Vec<String>>,
            date: Option<String>,
        }
        let selection: Selection = serde_json::from_slice(bytes).map_err(|e| e.to_string())?;
        if selection.state_code.is_some() && selection.state_codes.is_some() {
            return Err("Choose one state selection form".into());
        }
        let get = |path: &str| {
            self.documents
                .get(path)
                .ok_or_else(|| format!("Missing state context source {path}"))
        };
        let states = &get("research/ocean-motion-state-join.json")?["states"];
        let seasons = get("research/noaa-munster-eddy-seasonal-manifest-2021-2023.json")?;
        let date = selection.date.unwrap_or("2023-06-01".into());
        if !seasons["snapshots"]
            .as_array()
            .ok_or("Missing dated source selection")?
            .iter()
            .any(|r| r["date"] == date)
        {
            return Err("Unknown state context sample date".into());
        }
        let codes = selection.state_codes.unwrap_or_else(|| {
            selection
                .state_code
                .filter(|s| !s.is_empty())
                .into_iter()
                .collect()
        });
        if codes.len() > 56
            || codes
                .iter()
                .collect::<std::collections::BTreeSet<_>>()
                .len()
                != codes.len()
            || codes.iter().any(|code| states.get(code).is_none())
        {
            return Err("Unknown or duplicate state selection".into());
        }
        let front = get("research/gulf-stream-navo-state-snapshot-20260928.json")?;
        let diagnosed = get(
            "almanac/release/v0.1.0/source-ledgers/gulf-stream-geostrophic-path-20260925.json",
        )?;
        let local = get("almanac/release/v0.1.0/named_current_source_observations.json")?;
        let operational = get("almanac/release/v0.1.0/operational_eddy_state_observations.json")?;
        let currents = get("research/ocean-current-almanac.json")?;
        let geography = get("research/named-eddy-geography-join.json")?;
        let names = get("research/named-eddy-geography.json")?;
        let loops = get("research/named-loop-eddy-nasa-context.json")?;
        let movies = get("research/nasa-perpetual-ocean-state-tile-join.json")?;
        let timeline = get("research/nasa-perpetual-ocean-crop-timeline.json")?;
        let routes = self
            .documents
            .get("research/ocean-current-reference-route-state-join.json");
        let lookup = |rows: &Value, id: &Value| -> Result<Value, String> {
            rows.as_array()
                .ok_or("Missing context ledger")?
                .iter()
                .find(|r| r["id"] == *id)
                .cloned()
                .ok_or("Unresolved context source identity".into())
        };
        let mut views = vec![];
        for code in codes {
            let state_id = format!("state:{code}");
            let mut observations = vec![];
            for row in local
                .as_array()
                .ok_or("Missing local source observations")?
                .iter()
                .filter(|r| r["state_id"] == state_id)
            {
                let id = row["entity_id"]
                    .as_str()
                    .and_then(|s| s.strip_prefix("current:"))
                    .ok_or("Invalid observation owner")?;
                observations
                    .push(json!({"record":row,"current":lookup(&currents["entries"],&json!(id))?}));
            }
            let mut positions = vec![];
            for visit in geography["states_with_additional_observed_positions"][&code]
                .as_array()
                .ok_or("Missing named-eddy position inventory")?
            {
                positions.push(
                    json!({"record":visit,"eddy":lookup(&names["entries"],&visit["eddy_id"])?}),
                );
            }
            let loop_rows = |key: &str| -> Result<Vec<Value>, String> {
                loops[key]
                    .get(&code)
                    .and_then(Value::as_array)
                    .map(|ids| ids.iter().map(|id| lookup(&loops["entries"], id)).collect())
                    .unwrap_or_else(|| Ok(vec![]))
            };
            let movie = movies["states"]
                .get(&code)
                .ok_or("Missing state movie selection")?;
            let match_tile = |id: &Value| -> Result<Value, String> {
                movie["matches"]
                    .as_array()
                    .ok_or("Missing state crop matches")?
                    .iter()
                    .find(|r| r["tile_id"] == *id)
                    .cloned()
                    .ok_or("Unresolved state crop selection".into())
            };
            let recommended: Vec<Value> = movie["recommended_regional_tiles"]
                .as_array()
                .ok_or("Missing regional crop IDs")?
                .iter()
                .map(match_tile)
                .collect::<Result<_, _>>()?;
            let diagnosis = diagnosed["state_relations"]
                .as_array()
                .ok_or("Missing diagnostic state relations")?
                .iter()
                .find(|r| r["state_code"] == code);
            views.push(json!({"state_code":code,"date":date,
                "reference_routes":routes.and_then(|r|r["states"].get(&code)),
                "front":front["states"][&code],"front_date":front["date"],"front_source_url":front["source_url"],"front_claim_limit":front["claim_limit"],
                "diagnosed_relation":diagnosis,"diagnosed_date":diagnosed["observation_date"],"diagnosed_length_km":diagnosed["representative"]["segment_length_km"],"diagnosed_product_page":diagnosed["product_page"],"diagnosed_physical_limit":diagnosed["physical_limit"],
                "current_observations":observations,
                "operational_eddy_observations":operational.as_array().ok_or("Missing operational observation inventory")?.iter().filter(|r|r["state_id"]==state_id).collect::<Vec<_>>(),
                "named_eddy_positions":positions,"loop_region_names":loop_rows("states")?,"published_loop_positions":loop_rows("states_with_published_positions")?,
                "movie_selection":movie,"recommended_movies":recommended,"overview_movie":match_tile(&movie["overview_tile"])?}));
        }
        Ok(
            json!({"ok":true,"date":date,"views":views,"movie_seek":timeline["dates"].get(&date),
            "movie_alignment_status":timeline["alignment_status"],"movie_time_limit":timeline["limit"],"movie_evidence_limit":movies["evidence_limit"],
            "named_eddy_position_limit":geography["evidence_limit"],"loop_position_limit":loops["evidence_limit"],"scope":self.catalog["scope"]}),
        )
    }
    pub fn state_membership_view(&self, bytes: &[u8]) -> Result<Value, String> {
        #[derive(Deserialize)]
        #[serde(deny_unknown_fields)]
        struct Selection {
            state_code: Option<String>,
            state_codes: Option<Vec<String>>,
        }
        let selection: Selection = serde_json::from_slice(bytes).map_err(|e| e.to_string())?;
        if selection.state_code.is_some() && selection.state_codes.is_some() {
            return Err("Choose one state selection form".into());
        }
        let get = |path: &str| {
            self.documents
                .get(path)
                .ok_or_else(|| format!("Missing state membership source {path}"))
        };
        let join = get("research/ocean-motion-state-join.json")?;
        let cartographic = get("research/cartographic-ocean-current-state-join.json")?;
        let crosswalk = get("research/nasa-ocean-object-state-crosswalk.json")?;
        let nasa_matrix = get("research/nasa-object-state-relation-matrix.json")?;
        let current_matrix = get("research/ocean-current-state-relation-matrix.json")?;
        let geography = get("research/named-eddy-geography-join.json")?;
        let currents = get("research/ocean-current-almanac.json")?;
        let nasa = get("research/nasa-perpetual-ocean-objects.json")?;
        let names = get("research/named-eddy-geography.json")?;
        let states = join["states"]
            .as_object()
            .ok_or("Missing state inventory")?;
        let mut catalog: Vec<Value> = states
            .iter()
            .map(|(code, state)| json!({"code":code,"name":state["name"]}))
            .collect();
        catalog.sort_by(|a, b| a["name"].as_str().cmp(&b["name"].as_str()));
        let codes = selection.state_codes.unwrap_or_else(|| {
            selection
                .state_code
                .filter(|s| !s.is_empty())
                .into_iter()
                .collect()
        });
        if codes.len() > states.len()
            || codes
                .iter()
                .collect::<std::collections::BTreeSet<_>>()
                .len()
                != codes.len()
            || codes.iter().any(|code| !states.contains_key(code))
        {
            return Err("Unknown or duplicate state selection".into());
        }
        let named = |ids: &Value,
                     prefix: &str,
                     arrows: Option<&str>,
                     code: &str|
         -> Result<Vec<Value>, String> {
            let records = match prefix {
                "current" => &currents["entries"],
                "nasa" => &nasa["objects"],
                _ => &names["entries"],
            };
            ids.as_array().ok_or("Missing state member IDs")?.iter().map(|id| {
                let record=records.as_array().ok_or("Missing member ledger")?.iter().find(|r|r["id"]==*id).ok_or("Unresolved state member identity")?;
                let arrow_ids=if let Some(kind)=arrows {let key=id.as_str().ok_or("Invalid state member ID")?;
                    if prefix=="nasa"{nasa_matrix["states"][code]["objects"][key]["cartographic_source_arrow_ids"][kind].clone()}
                    else{current_matrix["states"][code]["currents"][key]["cartographic_source_arrow_ids"][kind].clone()}
                }else{json!([])};
                if !arrow_ids.is_array(){return Err("Missing state source arrow inventory".into());}
                Ok(json!({"id":id,"name":record["name"],"record":record,"source_arrow_ids":arrow_ids}))
            }).collect()
        };
        let definitions = [
            (
                "Schematic current lines crossing",
                "schematic_current_centerline_crossings",
                "current",
                0,
                None,
                "No drawn current line crosses this state.",
            ),
            (
                "Cartographic current arrows crossing · four widths",
                "stable_cartographic_current_crossings",
                "current",
                1,
                Some("stable"),
                "No mapped current arrow crosses this state at all four source widths.",
            ),
            (
                "Width-sensitive cartographic contacts",
                "width_sensitive_cartographic_contacts",
                "current",
                1,
                Some("width_sensitive"),
                "No source-arrow contacts change across the four display widths.",
            ),
            (
                "NASA-named current sketch crossing",
                "editorial_nasa_current_line_crossings",
                "current",
                0,
                None,
                "No additional NASA-named current sketch crosses this state.",
            ),
            (
                "Editorial named continuation sketch crossing",
                "editorial_named_current_line_crossings",
                "current",
                0,
                None,
                "No independently named continuation sketch crosses this state.",
            ),
            (
                "NASA-identified current · mapped arrow crossing",
                "cartographic_current_crossings",
                "nasa",
                2,
                Some("stable"),
                "No NASA-identified current has a mapped arrow crossing this state.",
            ),
            (
                "NASA-identified current · width-sensitive map contact",
                "width_sensitive_cartographic_contacts",
                "nasa",
                2,
                Some("width_sensitive"),
                "No NASA-identified current has a width-sensitive map contact here.",
            ),
            (
                "NASA-identified current · schematic line crossing",
                "schematic_current_crossings",
                "nasa",
                2,
                None,
                "No NASA-identified current has a schematic line crossing here.",
            ),
            (
                "NASA-identified object · OSW schematic gate crossing",
                "schematic_object_crossings",
                "nasa",
                2,
                None,
                "No NASA-identified object has an OSW gate line crossing here.",
            ),
            (
                "NASA-identified current · editorial line crossing",
                "editorial_current_line_crossings",
                "nasa",
                2,
                None,
                "No NASA-identified current has an editorial line crossing here.",
            ),
            (
                "Named current locators inside",
                "current_locator_candidates",
                "current",
                0,
                None,
                "No current locator in this state.",
            ),
            (
                "NASA object locators inside",
                "nasa_object_locator_candidates",
                "nasa",
                0,
                None,
                "No NASA object locator in this state.",
            ),
            (
                "Named eddy locators or sample sites inside",
                "locators",
                "eddy-geography",
                3,
                None,
                "No separately named eddy locator or sample site in this state.",
            ),
        ];
        let mut views = vec![];
        for code in codes {
            let mut groups = vec![];
            for (title, key, prefix, source, arrows, fallback) in definitions {
                let ids = match source {
                    0 => &join["states"][&code][key],
                    1 => &cartographic["states"][&code][key],
                    2 => &crosswalk["states"][&code][key],
                    _ => &geography["states"][&code],
                };
                groups.push(json!({"title":title,"kind":key,"prefix":prefix,"fallback":fallback,"members":named(ids,prefix,arrows,&code)?}));
            }
            let relations = nasa_matrix["states"][&code]["objects"]
                .as_object()
                .ok_or("Missing NASA state matrix")?;
            let mut contexts = vec![];
            let mut unresolved = vec![];
            let nasa_records = nasa["objects"]
                .as_array()
                .ok_or("Missing NASA member ledger")?;
            if relations.len() != nasa_records.len() {
                return Err("Incomplete NASA state pair inventory".into());
            }
            for record in nasa_records {
                let id = record["id"].as_str().ok_or("Missing NASA member ID")?;
                let relation = relations.get(id).ok_or("Unresolved NASA state pair")?;
                if relation["atlas_relation"] == "unresolved" {
                    let mut member = named(&json!([id]), "nasa", None, &code)?.remove(0);
                    member["relation"] = relation.clone();
                    unresolved.push(member);
                }
                let members = relation["contextual_members"]
                    .as_array()
                    .ok_or("Missing contextual members")?;
                if !members.is_empty() {
                    let mut resolved = vec![];
                    for member in members {
                        let mut entry =
                            named(&json!([member["object_id"]]), "nasa", None, &code)?.remove(0);
                        entry["relation"] = member.clone();
                        resolved.push(entry);
                    }
                    contexts.push(json!({"object":named(&json!([id]),"nasa",None,&code)?.remove(0),"relation":relation,"members":resolved}));
                }
            }
            views.push(json!({"state_code":code,"state":join["states"][&code],"groups":groups,"contextual_classes":contexts,"unresolved_nasa":unresolved,
                "current_count":current_matrix["current_count"],"atlas_linked_current_count":current_matrix["states"][&code]["atlas_linked_current_count"],
                "nasa_object_count":nasa_matrix["object_count"],"atlas_linked_object_count":nasa_matrix["states"][&code]["atlas_linked_object_count"]}));
        }
        Ok(
            json!({"ok":true,"states":catalog,"views":views,"state_count":states.len(),"scope":self.catalog["scope"],
            "current_claim_limit":current_matrix["claim_limit"],"nasa_claim_limit":nasa_matrix["claim_limit"]}),
        )
    }
    pub fn release_media_view(&self, bytes: &[u8]) -> Result<Value, String> {
        #[derive(Deserialize)]
        #[serde(deny_unknown_fields)]
        struct Selection {}
        let _: Selection = serde_json::from_slice(bytes).map_err(|e| e.to_string())?;
        let get = |path: &str| {
            self.documents
                .get(path)
                .ok_or_else(|| format!("Missing release media source {path}"))
        };
        let catalog = get("research/nasa-perpetual-ocean-release-media.json")?;
        let audit = get("research/nasa-perpetual-ocean-source-audit.json")?;
        let nasa = get("research/nasa-perpetual-ocean-objects.json")?;
        let crosswalk = get("research/nasa-ocean-object-state-crosswalk.json")?;
        let registry = get("almanac/release/v0.1.0/sources.json")?;
        let lookup = |items: &Value, id: &Value| -> Result<Value, String> {
            items
                .as_array()
                .ok_or("Missing release join rows")?
                .iter()
                .find(|v| v["id"] == *id)
                .cloned()
                .ok_or("Unresolved release source relation".into())
        };
        let mut rows = vec![];
        let mut movie_count = 0;
        for (ordinal, release) in catalog["releases"]
            .as_array()
            .ok_or("Missing release catalog")?
            .iter()
            .enumerate()
        {
            let id = release["release_id"].as_str().ok_or("Missing release ID")?;
            let reviewed = lookup(&audit["releases"], &release["release_id"])?;
            // Preserve the frozen registry's last URL record, as in the source UI.
            let source = registry
                .as_array()
                .ok_or("Missing source registry")?
                .iter()
                .rev()
                .find(|r| r["url"] == release["source_page"])
                .ok_or("Missing NASA page citation")?;
            if source["preferred_citation"]
                .as_str()
                .is_none_or(str::is_empty)
                || source["credit_text"].as_str().is_none_or(str::is_empty)
            {
                return Err("Incomplete NASA page citation".into());
            }
            let objects: Vec<Value> = reviewed["object_ids"]
                .as_array()
                .ok_or("Missing release object inventory")?
                .iter()
                .map(|object_id| {
                    let key = object_id.as_str().ok_or("Invalid release object ID")?;
                    let evidence = crosswalk["objects"][key]["release_evidence"]
                        .get(id)
                        .ok_or("Missing release-specific object evidence")?;
                    Ok(json!({"record":lookup(&nasa["objects"],object_id)?,"evidence":evidence}))
                })
                .collect::<Result<_, String>>()?;
            movie_count += release["movies"]
                .as_array()
                .ok_or("Missing movie inventory")?
                .len();
            rows.push(json!({"record":release,"source_pointer":format!("/releases/{ordinal}"),"audit":reviewed,"source":source,"objects":objects}));
        }
        if catalog["release_count"] != rows.len() || catalog["movie_listing_count"] != movie_count {
            return Err("Changed release/movie inventory counts".into());
        }
        Ok(
            json!({"ok":true,"rows":rows,"release_count":catalog["release_count"],"movie_listing_count":catalog["movie_listing_count"],
            "method":catalog["method"],"scope":self.catalog["scope"]}),
        )
    }
    pub fn nasa_view(&self, bytes: &[u8]) -> Result<Value, String> {
        #[derive(Deserialize)]
        #[serde(deny_unknown_fields)]
        struct Selection {
            #[serde(default)]
            text: String,
        }
        let selection: Selection = serde_json::from_slice(bytes).map_err(|e| e.to_string())?;
        let get = |path: &str| {
            self.documents
                .get(path)
                .ok_or_else(|| format!("Missing NASA source {path}"))
        };
        let data = get("research/nasa-perpetual-ocean-objects.json")?;
        let crosswalk = get("research/nasa-ocean-object-state-crosswalk.json")?;
        let media = get("research/nasa-perpetual-ocean-object-media.json")?;
        let forms = get("research/nasa-perpetual-ocean-motion-forms.json")?;
        let crops = get("research/nasa-current-cartographic-crop-join.json")?;
        let variants = get("research/nasa-object-movie-variant-join.json")?;
        let catalog = get("research/nasa-perpetual-ocean-atlas-catalog.json")?;
        let currents = get("research/ocean-current-almanac.json")?;
        let lookup = |items: &Value, id: &Value| -> Result<Value, String> {
            items
                .as_array()
                .ok_or("Missing NASA join rows")?
                .iter()
                .find(|v| v["id"] == *id)
                .cloned()
                .ok_or("Unresolved NASA source relation".into())
        };
        let entries = data["objects"].as_array().ok_or("Missing NASA objects")?;
        let query = selection.text.trim().to_lowercase();
        let mut rows = vec![];
        let release_evidence_count: usize = crosswalk["objects"]
            .as_object()
            .ok_or("Missing NASA crosswalk objects")?
            .values()
            .map(|record| {
                record["release_evidence"]
                    .as_object()
                    .map_or(0, |v| v.len())
            })
            .sum();
        for (ordinal, item) in entries.iter().enumerate() {
            let id = item["id"].as_str().ok_or("Missing NASA ID")?;
            let form = forms["objects"].get(id).ok_or("Missing NASA form")?;
            let haystack = [&item["name"], &item["support"], form, &item["description"]]
                .iter()
                .map(|v| v.as_str().unwrap_or(""))
                .collect::<Vec<_>>()
                .join(" ")
                .to_lowercase();
            if !haystack.contains(&query) {
                continue;
            }
            let relation = crosswalk["objects"]
                .get(id)
                .ok_or("Missing NASA crosswalk")?;
            let related_array = |key: &str, target: &str| -> Result<Vec<Value>, String> {
                relation[key]
                    .as_array()
                    .ok_or("Missing NASA relation array")?
                    .iter()
                    .map(|r| {
                        Ok(json!({"relation":r,"record":lookup(&data["objects"],&r[target])?}))
                    })
                    .collect()
            };
            let mut releases = vec![];
            for release_id in item["nasa_sources"]
                .as_array()
                .ok_or("Missing NASA release IDs")?
            {
                let evidence = relation["release_evidence"]
                    .get(release_id.as_str().ok_or("Invalid release ID")?)
                    .ok_or("Missing NASA release evidence")?;
                releases.push(
                    json!({"record":lookup(&data["releases"],release_id)?,"evidence":evidence}),
                );
            }
            let mut movies = vec![];
            for movie in variants["entries"]
                .as_array()
                .ok_or("Missing movie variants")?
            {
                for edge in movie["direct_object_relations"]
                    .as_array()
                    .ok_or("Missing movie relation rows")?
                {
                    if edge["object_id"] == item["id"] {
                        movies.push(json!({"movie":movie,"relation":edge,"release":lookup(&data["releases"],&movie["release_id"])?}));
                    }
                }
            }
            let external: Vec<Value> = relation["external_current_context"].as_array().ok_or("Missing external current context")?.iter().map(|r|Ok(json!({"relation":r,"record":lookup(&currents["entries"],&r["current_id"])?}))).collect::<Result<_,String>>()?;
            let examples: Vec<Value> = relation["example_object_ids"]
                .as_array()
                .ok_or("Missing NASA examples")?
                .iter()
                .map(|id| lookup(&data["objects"], id))
                .collect::<Result<_, _>>()?;
            let assets: Vec<Value> = relation["feature_media_ids"]
                .as_array()
                .ok_or("Missing media IDs")?
                .iter()
                .map(|id| lookup(&media["assets"], id))
                .collect::<Result<_, _>>()?;
            let catalog_record = catalog["records"]
                .as_array()
                .ok_or("Missing NASA catalog")?
                .iter()
                .find(|r| r["id"] == item["id"])
                .ok_or("Missing NASA catalog record")?;
            let crop_record = crops["records"]
                .as_array()
                .ok_or("Missing crop records")?
                .iter()
                .find(|r| r["nasa_object_id"] == item["id"]);
            rows.push(json!({"record":item,"source_pointer":format!("/objects/{ordinal}"),"form":form,"crosswalk":relation,
                "parent":if item["parent_id"].is_null(){Value::Null}else{lookup(&data["objects"],&item["parent_id"])?},
                "external_currents":external,"examples":examples,"systems":related_array("system_context","system_id")?,
                "class_parent":if relation["class_parent"].is_null(){Value::Null}else{lookup(&data["objects"],&relation["class_parent"]["parent_id"])?},
                "class_children":related_array("class_children","child_id")?,"catalog":catalog_record,
                "releases":releases,"feature_media":assets,"cartographic_crops":crop_record,"variants":movies,
                "narrated_release":if item["narrated_start_s"].is_null(){Value::Null}else{lookup(&data["releases"],&json!("po2-narrated"))?}}));
        }
        Ok(
            json!({"ok":true,"text":selection.text,"rows":rows,"total":entries.len(),"release_evidence_count":release_evidence_count,"form_definitions":forms["forms"],
            "class_relation_rule":forms["class_relation_rule"],"crop_claim_limit":crops["claim_limit"],"movie_variant_rule":variants["rule"],
            "scope":self.catalog["scope"]}),
        )
    }
    pub fn eddy_view(&self, bytes: &[u8]) -> Result<Value, String> {
        #[derive(Deserialize)]
        #[serde(deny_unknown_fields)]
        struct Selection {
            section: String,
            #[serde(default)]
            text: String,
        }
        fn text(v: &Value) -> String {
            match v {
                Value::String(s) => s.clone(),
                Value::Number(n) => n.to_string(),
                _ => String::new(),
            }
        }
        let selection: Selection = serde_json::from_slice(bytes).map_err(|e| e.to_string())?;
        let get = |path: &str| {
            self.documents
                .get(path)
                .ok_or_else(|| format!("Missing eddy view source {path}"))
        };
        let (data, context) = match selection.section.as_str() {
            "loop" => (
                get("research/named-loop-current-eddy-identities.json")?,
                Some(get("research/named-loop-eddy-nasa-context.json")?),
            ),
            "geography" => (
                get("research/named-eddy-geography.json")?,
                Some(get("research/named-eddy-geography-join.json")?),
            ),
            "inventory" => (get("research/ocean-eddy-name-inventory.json")?, None),
            _ => return Err("Unknown eddy view section".into()),
        };
        let entries = data["entries"].as_array().ok_or("Missing eddy entries")?;
        let query = selection.text.trim().to_lowercase();
        let lookup = |values: &Value, id: &Value| -> Result<Value, String> {
            values
                .as_array()
                .ok_or("Missing eddy join rows")?
                .iter()
                .find(|v| v["id"] == *id)
                .cloned()
                .ok_or("Unresolved source-specific eddy relation".into())
        };
        let mut rows = vec![];
        for (ordinal, item) in entries.iter().enumerate() {
            let fields: Vec<&Value> = match selection.section.as_str() {
                "loop" => vec![
                    &item["name"],
                    &item["initial_separation"],
                    &item["role"],
                    &item["source_number"],
                ],
                "geography" => vec![
                    &item["name"],
                    &item["basin"],
                    &item["identity_level"],
                    &item["event_year"],
                ],
                _ => vec![
                    &item["name"],
                    &item["basin"],
                    &item["identity_level"],
                    &item["source_event_date"],
                    &item["event_year"],
                    &item["date_evidence"]["observation_start"],
                ],
            };
            if selection.section == "inventory" && query.is_empty()
                || !fields
                    .into_iter()
                    .map(text)
                    .collect::<Vec<_>>()
                    .join(" ")
                    .to_lowercase()
                    .contains(&query)
            {
                continue;
            }
            let mut row = json!({"record":item,"source_pointer":format!("/entries/{ordinal}")});
            match selection.section.as_str() {
                "loop" => {
                    row["relation"] = lookup(&context.unwrap()["entries"], &item["id"])?;
                    row["parent"] = if item["related_primary_id"].is_null() {
                        Value::Null
                    } else {
                        lookup(&data["entries"], &item["related_primary_id"])?
                    };
                }
                "geography" => {
                    row["relation"] = context.unwrap()["entries"]
                        .get(text(&item["id"]))
                        .cloned()
                        .ok_or("Unresolved geography source join")?;
                    row["parent"] = if item["member_of"].is_null() {
                        Value::Null
                    } else {
                        lookup(&data["entries"], &item["member_of"])?
                    };
                    row["related_current"] = if item["related_current_id"].is_null() {
                        Value::Null
                    } else {
                        lookup(
                            &get("research/ocean-current-almanac.json")?["entries"],
                            &item["related_current_id"],
                        )?
                    };
                }
                _ => {
                    row["source_label"] = match item["source_collection"].as_str() {
                        Some("horizon_loop_current") => json!("Loop register"),
                        Some("published_loop_current") => json!("Published study"),
                        _ => item["basin"].clone(),
                    };
                    row["date_label"] = [
                        item["date_evidence"]["observation_start"].clone(),
                        item["source_event_date"].clone(),
                        item["event_year"].clone(),
                        item["identity_level"].clone(),
                    ]
                    .into_iter()
                    .find(|v| !text(v).is_empty())
                    .unwrap_or(Value::Null);
                }
            }
            rows.push(row);
        }
        Ok(
            json!({"ok":true,"section":selection.section,"text":selection.text,"rows":rows,"total":entries.len(),
            "retrieved_date":data["retrieved_date"],"numbered_event_count":data["numbered_event_count"],
            "horizon_numbered_event_count":data["horizon_numbered_event_count"],"sources":data["sources"],
            "scope":self.catalog["scope"],"claim_limit":data["claim_limit"]}),
        )
    }
    pub fn current_view(&self, bytes: &[u8]) -> Result<Value, String> {
        #[derive(Deserialize)]
        #[serde(deny_unknown_fields)]
        struct Selection {
            #[serde(default)]
            text: String,
            #[serde(default = "all")]
            setting: String,
            #[serde(default = "all")]
            length_status: String,
            #[serde(default = "all")]
            nasa_status: String,
        }
        fn all() -> String {
            "all".into()
        }
        fn label(v: &Value) -> Result<&str, String> {
            v.as_str().ok_or("Missing current source field".into())
        }
        let selection: Selection = serde_json::from_slice(bytes).map_err(|e| e.to_string())?;
        let get = |path: &str| {
            self.documents
                .get(path)
                .ok_or_else(|| format!("Missing current view source {path}"))
        };
        let data = get("research/ocean-current-almanac.json")?;
        let atlas = get("research/ocean-current-atlas-index.json")?;
        let taxonomy = get("research/ocean-motion-taxonomy.json")?;
        let lengths = get("research/ocean-current-length-evidence.json")?;
        let nasa = get("research/ocean-current-nasa-crosswalk.json")?;
        let tiles = get("research/nasa-perpetual-ocean-tile-join.json")?;
        let entries = data["entries"].as_array().ok_or("Missing currents")?;
        let lookup = |values: &Value, key: &str| -> Result<BTreeMap<String, Value>, String> {
            let mut out = BTreeMap::new();
            for item in values.as_array().ok_or("Missing current join records")? {
                if out
                    .insert(label(&item[key])?.into(), item.clone())
                    .is_some()
                {
                    return Err("Duplicate current join identity".into());
                }
            }
            Ok(out)
        };
        let by_id = lookup(&data["entries"], "id")?;
        let length_by_id = lookup(&lengths["entries"], "current_id")?;
        let nasa_by_id = lookup(&nasa["entries"], "current_id")?;
        let mut settings = std::collections::BTreeSet::new();
        for item in entries {
            settings.insert(label(&atlas["entries"][label(&item["id"])?]["setting"])?.to_string());
        }
        if selection.setting != "all" && !settings.contains(&selection.setting)
            || selection.length_status != "all"
                && lengths["status_definitions"]
                    .get(&selection.length_status)
                    .is_none()
            || selection.nasa_status != "all"
                && nasa["status_definitions"]
                    .get(&selection.nasa_status)
                    .is_none()
        {
            return Err("Unknown current view facet".into());
        }
        let mut ordered: Vec<_> = entries.iter().collect();
        ordered.sort_by(|a, b| {
            b["length_km"]
                .as_f64()
                .unwrap_or(-1.)
                .total_cmp(&a["length_km"].as_f64().unwrap_or(-1.))
                .then_with(|| a["name"].as_str().cmp(&b["name"].as_str()))
        });
        let named = |id: &Value| -> Result<Value, String> {
            let id = label(id)?;
            let item = by_id
                .get(id)
                .ok_or_else(|| format!("Unresolved related current {id}"))?;
            Ok(json!({"id":id,"name":item["name"]}))
        };
        let named_array = |ids: &Value| -> Result<Vec<Value>, String> {
            ids.as_array()
                .map(|ids| ids.iter().map(named).collect())
                .unwrap_or_else(|| Ok(vec![]))
        };
        let mut rows = vec![];
        let mut measured = 0;
        let mut rank = 0;
        let mut previous = None;
        let text = selection.text.trim().to_lowercase();
        for item in ordered {
            let id = label(&item["id"])?;
            let classification = atlas["entries"]
                .get(id)
                .ok_or("Missing current classification")?;
            let length = length_by_id
                .get(id)
                .ok_or("Missing current length assessment")?;
            let relation = nasa_by_id
                .get(id)
                .ok_or("Missing current NASA assessment")?;
            let value = item["length_km"].as_f64();
            if let Some(value) = value {
                measured += 1;
                if previous != Some(value) {
                    rank = measured;
                }
                previous = Some(value);
            }
            let components = named_array(&item["component_current_ids"])?;
            let parent = if item["part_of_system"].is_null() {
                None
            } else {
                Some(named(&item["part_of_system"])?)
            };
            let related_names = parent
                .iter()
                .chain(components.iter())
                .map(|v| v["name"].as_str().unwrap_or(""))
                .collect::<Vec<_>>()
                .join(" ");
            let haystack = format!(
                "{} {} {} {} {} {}",
                label(&item["name"])?,
                label(&item["basin"])?,
                label(&item["kind"])?,
                related_names,
                label(&classification["identity_level"])?.replace('_', " "),
                label(&classification["setting"])?.replace('_', " ")
            )
            .to_lowercase();
            if !haystack.contains(&text)
                || selection.setting != "all" && classification["setting"] != selection.setting
                || selection.length_status != "all" && length["status"] != selection.length_status
                || selection.nasa_status != "all" && relation["status"] != selection.nasa_status
            {
                continue;
            }
            let nasa_links = item["related_nasa_object_ids"]
                .as_array()
                .map(|ids| {
                    ids.iter()
                        .map(|id| {
                            let upstream =
                                relation["object_relations"].as_array().is_some_and(|rels| {
                                    rels.iter().any(|r| {
                                        r["nasa_object_id"] == *id
                                            && r["relation"]
                                                == "independently_named_upstream_feeder"
                                    })
                                });
                            json!({"id":id,"upstream_feeder":upstream})
                        })
                        .collect::<Vec<_>>()
                })
                .unwrap_or_default();
            rows.push(json!({"record":item,"classification":classification,"length_evidence":length,"nasa_relation":relation,
                "rank":if value.is_some(){Some(rank)}else{None},
                "linked_currents":if let Some(parent)=parent {vec![parent]} else {components},
                "identity_related":if item["identity_review"]["related_current_id"].is_null(){Value::Null}else{named(&item["identity_review"]["related_current_id"])?},
                "related_currents":named_array(&item["related_current_ids"])?,"nasa_links":nasa_links,
                "scene_url":atlas["nasa_current_scene_urls"][id],
                "crop_url":tiles["current_joins"][id][0]["url"]}));
        }
        Ok(
            json!({"ok":true,"rows":rows,"total":entries.len(),"settings":settings,
            "length_definitions":lengths["status_definitions"],"length_counts":lengths["counts"],
            "nasa_definitions":nasa["status_definitions"],"nasa_counts":nasa["counts"],
            "sources":data["sources"],"taxonomy_axes":taxonomy["axes"],"scope":self.catalog["scope"]}),
        )
    }
    pub fn load(bytes: &[u8]) -> Result<Self, String> {
        let catalog: Value =
            serde_json::from_str(CATALOG).map_err(|_| "Invalid compiled index catalog")?;
        if catalog["schema"] != "osw.almanac-index-catalog.v1"
            || catalog["status"] != "source_snapshot_not_new_scientific_admission"
            || catalog["bundle_sha256"] != format!("{:x}", Sha256::digest(bytes))
        {
            return Err("Changed index bundle or compiled catalog".into());
        }
        let bundle: Bundle =
            serde_json::from_slice(bytes).map_err(|_| "Invalid index bundle JSON")?;
        let descriptors = catalog["documents"]
            .as_array()
            .ok_or("Missing index catalog inventory")?;
        if bundle.schema != "osw.almanac-index-bundle.v1"
            || bundle.documents.len() != descriptors.len()
        {
            return Err("Incomplete index source inventory".into());
        }
        let mut documents = BTreeMap::new();
        for descriptor in descriptors {
            let path = descriptor["path"]
                .as_str()
                .ok_or("Missing index source path")?;
            let raw = bundle
                .documents
                .get(path)
                .ok_or("Missing index source bytes")?;
            let doc: Value = serde_json::from_str(raw).map_err(|_| "Invalid index source JSON")?;
            if descriptor["source_sha256"] != format!("{:x}", Sha256::digest(raw.as_bytes()))
                || descriptor["source_bytes"] != raw.len()
                || (descriptor["root_kind"] == "array" && !doc.is_array())
                || (descriptor["root_kind"] == "object" && !doc.is_object())
                || doc["schema"] != descriptor["source_schema"]
                || documents.insert(path.to_string(), doc).is_some()
            {
                return Err("Index source hash, shape, schema or identity mismatch".into());
            }
        }
        if let Some(doc) =
            documents.get("research/ocean-current-inventory-expansion-candidates.json")
        {
            crate::proposed_widths::validate_proposals(doc)?;
        }
        if let Some(doc) =
            documents.get("research/norwegian-atlantic-branch-width-scope-audit.json")
        {
            crate::proposed_widths::validate_audit(doc)?;
        }
        Ok(Self { documents, catalog })
    }
    pub fn metadata(&self) -> Value {
        json!({"ok":true,"engine":"rust-osw-query-v1","catalog":self.catalog,
            "source_count":self.documents.len(),"scope":self.catalog["scope"]})
    }
    pub fn document(&self, bytes: &[u8]) -> Result<Value, String> {
        #[derive(Deserialize)]
        #[serde(deny_unknown_fields)]
        struct Selection {
            document: String,
        }
        let r: Selection = serde_json::from_slice(bytes).map_err(|e| e.to_string())?;
        let value = self
            .documents
            .get(&r.document)
            .ok_or("Unknown index source document")?;
        Ok(json!({"ok":true,"document":r.document,"value":value}))
    }
    pub fn query(&self, bytes: &[u8]) -> Result<Value, String> {
        let r: Request = serde_json::from_slice(bytes).map_err(|e| e.to_string())?;
        let limit = r.limit.unwrap_or(50);
        if limit == 0 || limit > 500 {
            return Err("Index query limit must be 1 through 500".into());
        }
        if !r.pointer.is_empty() && !r.pointer.starts_with('/') {
            return Err("Invalid index JSON pointer".into());
        }
        let document = self
            .documents
            .get(&r.document)
            .ok_or("Unknown index source document")?;
        let selected = document
            .pointer(&r.pointer)
            .ok_or("Unknown index source pointer")?;
        let mut rows: Vec<Value> = match selected {
            Value::Array(items) => items.iter().enumerate().map(|(i,v)|json!({
                "source_pointer":format!("{}/{i}",r.pointer),"source_key":i.to_string(),"record":v})).collect(),
            Value::Object(items) => items.iter().map(|(key,v)|json!({
                "source_pointer":format!("{}/{}",r.pointer,escaped(key)),"source_key":key,"record":v})).collect(),
            _ => return Err("Index query pointer must select an array or object".into())
        };
        if let Some(text) = r.text {
            let text = text.to_lowercase();
            rows.retain(|row| row.to_string().to_lowercase().contains(&text));
        }
        for filter in &r.filters {
            // Validate even an empty selection, then evaluate source fields only.
            filtered(&Value::Null, filter)?;
            rows = rows
                .into_iter()
                .map(|row| filtered(&row, filter).map(|keep| (row, keep)))
                .collect::<Result<Vec<_>, _>>()?
                .into_iter()
                .filter_map(|(row, keep)| keep.then_some(row))
                .collect();
        }
        if let Some(sort) = r.sort {
            if !["asc", "desc"].contains(&sort.direction.as_str()) {
                return Err("Invalid index sort direction".into());
            }
            rows.sort_by(|a, b| {
                match (crate::field(a, &sort.field), crate::field(b, &sort.field)) {
                    (Some(a), Some(b)) if !a.is_null() && !b.is_null() => {
                        let order = crate::compare(a, b);
                        if sort.direction == "desc" {
                            order.reverse()
                        } else {
                            order
                        }
                    }
                    (Some(a), _) if !a.is_null() => std::cmp::Ordering::Less,
                    (_, Some(b)) if !b.is_null() => std::cmp::Ordering::Greater,
                    _ => std::cmp::Ordering::Equal,
                }
            });
        }
        let total = rows.len();
        let descriptor = self.catalog["documents"]
            .as_array()
            .unwrap()
            .iter()
            .find(|d| d["path"] == r.document)
            .unwrap();
        Ok(
            json!({"ok":true,"document":r.document,"pointer":r.pointer,"source_sha256":descriptor["source_sha256"],
            "total":total,"offset":r.offset,"limit":limit,"rows":rows.into_iter().skip(r.offset).take(limit).collect::<Vec<_>>(),
            "scope":self.catalog["scope"]}),
        )
    }
}
#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn source_field_queries_keep_nulls_numeric_values_and_pointer_addresses_distinct() {
        let row = json!({"record":{"name":"São eddy","value":null,"radius":0,"states":["CAMR"]}});
        let run = |op: &str, field: &str, value: Value| {
            filtered(
                &row,
                &crate::Filter {
                    op: op.into(),
                    field: field.into(),
                    value,
                },
            )
            .unwrap()
        };
        assert!(run("is_null", "record.value", Value::Null));
        assert!(!run("is_null", "record.radius", Value::Null));
        assert!(run("contains", "record.states", json!("CAMR")));
        assert!(run("contains", "record.name", json!("SÃO")));
        assert!(!run("gt", "record.value", json!(0)));
        assert_eq!(escaped("a/b~c"), "a~1b~0c");
    }
}
