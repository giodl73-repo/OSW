//! Three-way migration of proposed records with explicit conflict decisions.
use super::*;
use serde::{Deserialize, Serialize};
use workspace::{Journal, Operation, Transaction, WorkingRecord};
#[derive(Clone, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Origin {
    pub source_bundle_sha256: String,
    pub source_journal_sha256: String,
    pub source_revision: usize,
    pub decisions: BTreeMap<String, String>,
}
#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Request {
    pub journal: Journal,
    pub base_revision: u64,
    pub transaction_id: String,
    pub created_at: String,
    #[serde(default)]
    pub resolutions: BTreeMap<String, String>,
}
fn escaped(key: &str) -> String {
    key.replace('~', "~0").replace('/', "~1")
}
fn merge(
    base: Option<&Value>,
    proposed: Option<&Value>,
    source: Option<&Value>,
    path: &str,
    record: &str,
    resolutions: &BTreeMap<String, String>,
    conflicts: &mut Vec<Value>,
) -> Option<Value> {
    if proposed == base {
        return source.cloned();
    }
    if source == base || proposed == source {
        return proposed.cloned();
    }
    if let (Some(Value::Object(b)), Some(Value::Object(p)), Some(Value::Object(s))) =
        (base, proposed, source)
    {
        let keys: BTreeSet<_> = b.keys().chain(p.keys()).chain(s.keys()).collect();
        let mut result = serde_json::Map::new();
        for key in keys {
            if let Some(value) = merge(
                b.get(key),
                p.get(key),
                s.get(key),
                &format!("{path}/{}", escaped(key)),
                record,
                resolutions,
                conflicts,
            ) {
                result.insert(key.clone(), value);
            }
        }
        return Some(Value::Object(result));
    }
    let id = format!(
        "conflict:{:x}",
        Sha256::digest(json!([record, path, "field"]).to_string().as_bytes())
    );
    let choice = resolutions.get(&id);
    conflicts.push(json!({"id":id,"record_id":record,"path":path,"kind":"source_field_conflict","choice":choice,
        "old_source":{"present":base.is_some(),"value":base},"proposed":{"present":proposed.is_some(),"value":proposed},"new_source":{"present":source.is_some(),"value":source}}));
    match choice.map(String::as_str) {
        Some("source") => source.cloned(),
        _ => proposed.cloned(),
    }
}
impl Store {
    pub fn workspace_rebase(
        &self,
        old: &Store,
        bytes: &[u8],
        prepare: bool,
    ) -> Result<Value, String> {
        if bytes.len() > 8_000_000 {
            return Err("Rebase request exceeds 8 MB".into());
        }
        let request: Request =
            serde_json::from_slice(bytes).map_err(|e| format!("Invalid rebase request: {e}"))?;
        if request.base_revision != self.workspace.events.len() as u64 {
            return Err("Workspace revision conflict; reload and preview rebase again".into());
        }
        if request.journal.bundle_sha256 == self.workspace.bundle_sha256 {
            return Err("Rebase requires different source snapshots".into());
        }
        let old_records = request.journal.replay(old)?;
        let mut conflicts = Vec::new();
        let mut records = Vec::new();
        let mut omitted = Vec::new();
        let mut allowed = BTreeSet::new();
        for row in old_records {
            let mut record: WorkingRecord =
                serde_json::from_value(row).map_err(|e| e.to_string())?;
            let omit = format!("omit:{}", record.id);
            allowed.insert(omit.clone());
            if request.resolutions.get(&omit).map(String::as_str) == Some("omit") {
                omitted.push(record.id);
                continue;
            }
            let old_source =
                old.record(&record.target.collection, &record.target.id)?["record"].clone();
            let Ok(current) = self.record(&record.target.collection, &record.target.id) else {
                conflicts.push(json!({"id":omit,"kind":"missing_source_record","record_id":record.id,"path":"","choice":null,"target":record.target}));
                continue;
            };
            record.proposed_data = merge(
                Some(&old_source),
                Some(&record.proposed_data),
                Some(&current["record"]),
                "",
                &record.id,
                &request.resolutions,
                &mut conflicts,
            )
            .ok_or("Rebase removed entire proposed record")?;
            if let Ok(existing) = self.record("working_records", &record.id) {
                if existing["record"] != json!(record) {
                    let id = format!(
                        "conflict:{:x}",
                        Sha256::digest(json!([record.id, "destination"]).to_string().as_bytes())
                    );
                    let choice = request.resolutions.get(&id);
                    conflicts.push(json!({"id":id,"kind":"destination_working_record_conflict","record_id":record.id,"path":"","choice":choice,"proposed":json!(record),"new_source":existing["record"]}));
                    if choice.map(String::as_str) == Some("source") {
                        continue;
                    }
                } else {
                    continue;
                }
            }
            records.push(record);
        }
        for conflict in &conflicts {
            allowed.insert(conflict["id"].as_str().unwrap().to_owned());
        }
        for (key, choice) in &request.resolutions {
            if !allowed.contains(key)
                || !(if key.starts_with("omit:") {
                    choice == "omit"
                } else {
                    ["source", "proposed"].contains(&choice.as_str())
                })
            {
                return Err("Unknown or invalid rebase resolution".into());
            }
        }
        let unresolved = conflicts.iter().filter(|c| c["choice"].is_null()).count();
        let ready = unresolved == 0 && !records.is_empty();
        if !prepare {
            return Ok(
                json!({"ok":true,"ready":ready,"unresolved":unresolved,"conflicts":conflicts,"records":records,"omitted_record_ids":omitted,
            "base_revision":request.base_revision,"source_bundle_sha256":old.workspace.bundle_sha256,"destination_bundle_sha256":self.workspace.bundle_sha256,
            "scope":"Proposed-record migration only; review all changed scientific fields before admission. Arrays are atomic; omitted proposals remain in their original journal."}),
            );
        }
        if !ready {
            return Err(if unresolved > 0 {
                "Resolve every conflict before saving a rebase"
            } else {
                "No proposed records require rebasing"
            }
            .into());
        }
        if request.transaction_id.is_empty() || request.transaction_id.len() > 100 {
            return Err("Invalid rebase transaction ID".into());
        }
        let origin = Origin {
            source_bundle_sha256: request.journal.bundle_sha256.clone(),
            source_journal_sha256: format!(
                "{:x}",
                Sha256::digest(serde_json::to_vec(&request.journal).unwrap())
            ),
            source_revision: request.journal.events.len(),
            decisions: request.resolutions,
        };
        let mut journal = self.workspace.clone();
        journal.schema = "osw.workspace-journal.v2".into();
        for (batch, chunk) in records.chunks(50).enumerate() {
            journal.events.push(Transaction {
                base_revision: journal.events.len() as u64,
                transaction_id: format!("{}:{batch}", request.transaction_id),
                created_at: request.created_at.clone(),
                operations: chunk
                    .iter()
                    .cloned()
                    .map(|record| Operation::Upsert { record })
                    .collect(),
                rebase: Some(origin.clone()),
            });
        }
        let records = journal.replay(self)?;
        if serde_json::to_vec(&journal).unwrap().len() > 8_000_000 {
            return Err("Rebased journal exceeds 8 MB".into());
        }
        Ok(
            json!({"ok":true,"revision":journal.events.len(),"record_count":records.len(),"journal":journal}),
        )
    }
}
#[cfg(test)]
mod tests {
    use super::*;
    fn store(length: i32, extra: bool) -> Store {
        let row = if extra {
            json!({"id":"a","length":length,"new":true,"nullable":null,"array":[1,2]})
        } else {
            json!({"id":"a","length":length,"nullable":null,"array":[1]})
        };
        Store::load(
            json!({"schema":"osw.query-bundle.v1","manifest":{},"collections":{"objects":[row]}})
                .to_string()
                .as_bytes(),
        )
        .unwrap()
    }
    fn request(old: &Store) -> Value {
        let tx = json!({"base_revision":0,"transaction_id":"old-tx","created_at":"2026-10-04T12:00:00Z","operations":[{"op":"upsert","record":{"id":"draft:a","label":"A","summary":"Change length pending review","target":{"collection":"objects","id":"a"},"status":"proposed","proposed_data":{"id":"a","length":20,"nullable":null,"array":[1]}}}]});
        let journal = old.workspace_prepare(tx.to_string().as_bytes()).unwrap()["journal"].clone();
        json!({"journal":journal,"base_revision":0,"transaction_id":"rebase-tx","created_at":"2026-10-04T13:00:00Z","resolutions":{}})
    }
    #[test]
    fn three_way_conflicts_and_source_changes() {
        let old = store(10, false);
        let mut new = store(30, true);
        let mut req = request(&old);
        let plan = new
            .workspace_rebase(&old, req.to_string().as_bytes(), false)
            .unwrap();
        assert_eq!(plan["unresolved"], 1);
        assert_eq!(plan["records"][0]["proposed_data"]["array"], json!([1, 2]));
        assert_eq!(plan["records"][0]["proposed_data"]["new"], true);
        assert!(
            new.workspace_rebase(&old, req.to_string().as_bytes(), true)
                .is_err()
        );
        assert_eq!(new.workspace_export()["revision"], 0);
        req["resolutions"] = json!({plan["conflicts"][0]["id"].as_str().unwrap():"proposed"});
        let prepared = new
            .workspace_rebase(&old, req.to_string().as_bytes(), true)
            .unwrap();
        new.workspace_import(prepared["journal"].to_string().as_bytes())
            .unwrap();
        assert_eq!(
            new.record("working_records", "draft:a").unwrap()["record"]["proposed_data"]["length"],
            20
        );
        assert_eq!(new.record("objects", "a").unwrap()["record"]["length"], 30);
        assert_eq!(
            new.workspace_export()["journal"]["schema"],
            "osw.workspace-journal.v2"
        );
    }
    #[test]
    fn missing_null_arrays_and_bad_inputs() {
        let mut conflicts = vec![];
        let r = BTreeMap::new();
        let old = json!({"a":null,"b":1,"arr":[1]});
        let proposed = json!({"b":2,"arr":[1,3]});
        let source = json!({"a":null,"b":1,"arr":[1,2],"c":4});
        let value = merge(
            Some(&old),
            Some(&proposed),
            Some(&source),
            "",
            "draft:a",
            &r,
            &mut conflicts,
        )
        .unwrap();
        assert!(value.get("a").is_none());
        assert_eq!(value["c"], 4);
        assert_eq!(conflicts.len(), 1);
        assert_eq!(conflicts[0]["path"], "/arr");
        let old = store(10, false);
        let new = store(30, true);
        let mut req = request(&old);
        req["resolutions"] = json!({"fake":"source"});
        assert!(
            new.workspace_rebase(&old, req.to_string().as_bytes(), false)
                .is_err()
        );
        req["resolutions"] = json!({});
        req["journal"]["bundle_sha256"] = json!("fake");
        assert!(
            new.workspace_rebase(&old, req.to_string().as_bytes(), false)
                .is_err()
        );
    }
    #[test]
    fn missing_targets_and_destination_conflicts() {
        let old = store(10, false);
        let missing = Store::load(
            br#"{"schema":"osw.query-bundle.v1","manifest":{},"collections":{"objects":[]}}"#,
        )
        .unwrap();
        let mut req = request(&old);
        let plan = missing
            .workspace_rebase(&old, req.to_string().as_bytes(), false)
            .unwrap();
        assert_eq!(plan["conflicts"][0]["kind"], "missing_source_record");
        req["resolutions"] = json!({"omit:draft:a":"omit"});
        let plan = missing
            .workspace_rebase(&old, req.to_string().as_bytes(), false)
            .unwrap();
        assert_eq!(plan["unresolved"], 0);
        assert!(!plan["ready"].as_bool().unwrap());
        assert_eq!(plan["omitted_record_ids"], json!(["draft:a"]));
        let mut new = store(10, true);
        req = request(&old);
        let mut tx = req["journal"]["events"][0].clone();
        tx["transaction_id"] = json!("destination-tx");
        tx["operations"][0]["record"]["summary"] = json!("Existing destination edit");
        tx["operations"][0]["record"]["proposed_data"]["length"] = json!(25);
        let prepared = new.workspace_prepare(tx.to_string().as_bytes()).unwrap();
        new.workspace_import(prepared["journal"].to_string().as_bytes())
            .unwrap();
        req["base_revision"] = json!(1);
        let plan = new
            .workspace_rebase(&old, req.to_string().as_bytes(), false)
            .unwrap();
        let conflict = &plan["conflicts"][0];
        assert_eq!(conflict["kind"], "destination_working_record_conflict");
        req["resolutions"] = json!({conflict["id"].as_str().unwrap():"proposed"});
        let prepared = new
            .workspace_rebase(&old, req.to_string().as_bytes(), true)
            .unwrap();
        assert_eq!(prepared["revision"], 2);
        assert_eq!(
            prepared["journal"]["events"][0],
            new.workspace_export()["journal"]["events"][0]
        );
    }
    #[test]
    fn inventory_sized_rebase_batches_are_atomic() {
        let rows: Vec<_> = (0..51)
            .map(|i| json!({"id":format!("a{i}"),"value":1}))
            .collect();
        let old_bytes =
            json!({"schema":"osw.query-bundle.v1","manifest":{},"collections":{"objects":rows}})
                .to_string();
        let mut old = Store::load(old_bytes.as_bytes()).unwrap();
        for (batch, chunk) in rows.chunks(50).enumerate() {
            let operations:Vec<_>=chunk.iter().map(|r|json!({"op":"upsert","record":{"id":format!("draft:{}",r["id"].as_str().unwrap()),"label":"Proposed","summary":"Inventory batch","status":"proposed","target":{"collection":"objects","id":r["id"]},"proposed_data":{"id":r["id"],"value":2}}})).collect();
            let tx = json!({"base_revision":batch,"transaction_id":format!("tx{batch}"),"created_at":"2026-10-04T12:00:00Z","operations":operations});
            let saved = old.workspace_prepare(tx.to_string().as_bytes()).unwrap();
            old.workspace_import(saved["journal"].to_string().as_bytes())
                .unwrap();
        }
        let new_rows: Vec<_> = rows
            .iter()
            .map(|r| json!({"id":r["id"],"value":1,"added":true}))
            .collect();
        let mut new=Store::load(json!({"schema":"osw.query-bundle.v1","manifest":{},"collections":{"objects":new_rows}}).to_string().as_bytes()).unwrap();
        let req = json!({"journal":old.workspace_export()["journal"],"base_revision":0,"transaction_id":"full-rebase","created_at":"2026-10-04T13:00:00Z"});
        let prepared = new
            .workspace_rebase(&old, req.to_string().as_bytes(), true)
            .unwrap();
        assert_eq!(prepared["record_count"], 51);
        assert_eq!(prepared["revision"], 2);
        assert_eq!(new.workspace_export()["revision"], 0);
        new.workspace_import(prepared["journal"].to_string().as_bytes())
            .unwrap();
        assert_eq!(new.workspace_export()["record_count"], 51);
    }
}
