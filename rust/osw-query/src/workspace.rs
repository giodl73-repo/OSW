//! Snapshot-bound proposed records and replayable, optimistic transactions.
use super::*;
use serde::{Deserialize, Serialize};

#[derive(Clone, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Target {
    pub collection: String,
    pub id: String,
}
#[derive(Clone, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct WorkingRecord {
    pub id: String,
    pub label: String,
    pub summary: String,
    pub target: Target,
    pub proposed_data: Value,
    pub status: String,
}
#[derive(Clone, Serialize, Deserialize)]
#[serde(tag = "op", rename_all = "snake_case", deny_unknown_fields)]
pub enum Operation {
    Upsert { record: WorkingRecord },
    Delete { id: String },
}
#[derive(Clone, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Transaction {
    pub base_revision: u64,
    pub transaction_id: String,
    pub created_at: String,
    pub operations: Vec<Operation>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub rebase: Option<super::rebase::Origin>,
}
#[derive(Clone, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Journal {
    pub schema: String,
    pub bundle_sha256: String,
    pub events: Vec<Transaction>,
}
pub(crate) fn utc_timestamp(value: &str) -> bool {
    if !value.is_ascii() || value.len() < 20 || value.len() > 40 || !value.ends_with('Z') {
        return false;
    }
    let bytes = value.as_bytes();
    if bytes[4] != b'-'
        || bytes[7] != b'-'
        || bytes[10] != b'T'
        || bytes[13] != b':'
        || bytes[16] != b':'
    {
        return false;
    }
    let number = |a: usize, b: usize| {
        if value.as_bytes()[a..b].iter().all(u8::is_ascii_digit) {
            value[a..b].parse::<u32>().ok()
        } else {
            None
        }
    };
    let (Some(year), Some(month), Some(day), Some(hour), Some(minute), Some(second)) = (
        number(0, 4),
        number(5, 7),
        number(8, 10),
        number(11, 13),
        number(14, 16),
        number(17, 19),
    ) else {
        return false;
    };
    let leap = year % 4 == 0 && (year % 100 != 0 || year % 400 == 0);
    let days = match month {
        1 | 3 | 5 | 7 | 8 | 10 | 12 => 31,
        4 | 6 | 9 | 11 => 30,
        2 => {
            if leap {
                29
            } else {
                28
            }
        }
        _ => 0,
    };
    if year == 0 || day == 0 || day > days || hour > 23 || minute > 59 || second > 59 {
        return false;
    }
    value.len() == 20
        || (bytes[19] == b'.'
            && value.len() > 21
            && bytes[20..value.len() - 1].iter().all(u8::is_ascii_digit))
}

impl Journal {
    pub fn empty(hash: String) -> Self {
        Self {
            schema: "osw.workspace-journal.v1".into(),
            bundle_sha256: hash,
            events: vec![],
        }
    }
    pub fn replay(&self, store: &Store) -> Result<Vec<Value>, String> {
        if !["osw.workspace-journal.v1", "osw.workspace-journal.v2"].contains(&self.schema.as_str())
        {
            return Err("Unsupported workspace schema".into());
        }
        if self.bundle_sha256 != store.workspace.bundle_sha256 {
            return Err(
                "Workspace belongs to another source snapshot; explicit rebase is required".into(),
            );
        }
        if self.events.len() > 1000 {
            return Err("Workspace exceeds 1000 revisions".into());
        }
        let mut ids = BTreeSet::new();
        let mut records = BTreeMap::new();
        for (revision, event) in self.events.iter().enumerate() {
            if let Some(origin) = &event.rebase {
                if self.schema != "osw.workspace-journal.v2"
                    || origin.source_bundle_sha256.len() != 64
                    || origin.source_journal_sha256.len() != 64
                    || !origin
                        .source_bundle_sha256
                        .bytes()
                        .chain(origin.source_journal_sha256.bytes())
                        .all(|b| b.is_ascii_hexdigit())
                {
                    return Err("Invalid rebase provenance".into());
                }
            }
            if event.base_revision != revision as u64 {
                return Err("Non-contiguous workspace revision".into());
            }
            if event.transaction_id.is_empty()
                || event.transaction_id.len() > 128
                || !ids.insert(&event.transaction_id)
            {
                return Err("Invalid or duplicate transaction ID".into());
            }
            if !utc_timestamp(&event.created_at) {
                return Err("Workspace requires a valid ISO UTC timestamp".into());
            }
            if event.operations.is_empty() || event.operations.len() > 50 {
                return Err("Transaction requires 1..50 operations".into());
            }
            let mut changed = BTreeSet::new();
            for operation in &event.operations {
                let id = match operation {
                    Operation::Upsert { record } => &record.id,
                    Operation::Delete { id } => id,
                };
                if !id.starts_with("draft:") || id.len() > 300 || !changed.insert(id) {
                    return Err("Invalid or repeated working record ID".into());
                }
                match operation {
                    Operation::Upsert { record } => {
                        if record.status != "proposed"
                            || record.label.trim().is_empty()
                            || record.label.len() > 300
                            || record.summary.trim().is_empty()
                            || record.summary.len() > 4000
                        {
                            return Err(
                                "Proposed record requires label, summary and proposed status"
                                    .into(),
                            );
                        }
                        if record.target.collection == "working_records" {
                            return Err(
                                "A working record must reference an imported source record".into(),
                            );
                        }
                        store.record(&record.target.collection, &record.target.id)?;
                        if !record.proposed_data.is_object()
                            || record.proposed_data["id"] != record.target.id
                        {
                            return Err("Proposed data must retain its source record ID".into());
                        }
                        if let Some(old) = records.get(id) {
                            let old: &Value = old;
                            if old["target"] != json!(record.target) {
                                return Err("A working record cannot change source identity".into());
                            }
                        }
                        records.insert(id.clone(), json!(record));
                    }
                    Operation::Delete { id } => {
                        if records.remove(id).is_none() {
                            return Err("Cannot delete a missing working record".into());
                        }
                    }
                }
            }
        }
        Ok(records.into_values().collect())
    }
}

impl Store {
    pub fn workspace_check(&self, bytes: &[u8]) -> Result<Value, String> {
        if bytes.len() > 8_000_000 {
            return Err("Workspace journal exceeds 8 MB".into());
        }
        let journal: Journal =
            serde_json::from_slice(bytes).map_err(|e| format!("Invalid workspace journal: {e}"))?;
        let records = journal.replay(self)?;
        Ok(
            json!({"ok":true,"revision":journal.events.len(),"journal":journal,"record_count":records.len()}),
        )
    }
    pub fn workspace_export(&self) -> Value {
        json!({"ok":true,"revision":self.workspace.events.len(),"journal":self.workspace,"record_count":self.bundle.collections["working_records"].len()})
    }
    pub fn workspace_prepare(&self, bytes: &[u8]) -> Result<Value, String> {
        if bytes.len() > 2_000_000 {
            return Err("Transaction exceeds 2 MB".into());
        }
        let transaction: Transaction =
            serde_json::from_slice(bytes).map_err(|e| format!("Invalid transaction: {e}"))?;
        if transaction.rebase.is_some() {
            return Err("Use the explicit rebase operation for migration provenance".into());
        }
        if transaction.base_revision != self.workspace.events.len() as u64 {
            return Err("Workspace revision conflict; reload working records".into());
        }
        let mut journal = self.workspace.clone();
        journal.events.push(transaction);
        let records = journal.replay(self)?;
        if serde_json::to_vec(&journal).unwrap().len() > 8_000_000 {
            return Err("Workspace journal exceeds 8 MB".into());
        }
        Ok(
            json!({"ok":true,"revision":journal.events.len(),"journal":journal,"record_count":records.len()}),
        )
    }
    pub fn workspace_import(&mut self, bytes: &[u8]) -> Result<Value, String> {
        if bytes.len() > 8_000_000 {
            return Err("Workspace journal exceeds 8 MB".into());
        }
        let journal: Journal =
            serde_json::from_slice(bytes).map_err(|e| format!("Invalid workspace journal: {e}"))?;
        let records = journal.replay(self)?;
        let mut fields = BTreeSet::from([
            "id".into(),
            "label".into(),
            "summary".into(),
            "status".into(),
            "target.collection".into(),
            "target.id".into(),
        ]);
        let mut ids = BTreeMap::new();
        for (i, record) in records.iter().enumerate() {
            collect_fields(record, "", &mut fields);
            ids.insert(record["id"].as_str().unwrap().to_owned(), i);
        }
        self.fields.insert("working_records".into(), fields);
        self.ids.insert("working_records".into(), ids);
        self.bundle
            .collections
            .insert("working_records".into(), records);
        self.workspace = journal;
        Ok(self.workspace_export())
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    fn store() -> Store {
        Store::load(br#"{"schema":"osw.query-bundle.v1","manifest":{},"collections":{"objects":[{"id":"a","label":"Alpha","published_length_km":null}]}}"#).unwrap()
    }
    fn transaction() -> Value {
        json!({"base_revision":0,"transaction_id":"tx-1","created_at":"2026-10-04T12:00:00Z","operations":[{"op":"upsert","record":{"id":"draft:a","label":"Alpha proposal","summary":"Review a new source","status":"proposed","target":{"collection":"objects","id":"a"},"proposed_data":{"id":"a","label":"Alpha","published_length_km":25}}}]})
    }
    #[test]
    fn durable_replay_and_atomic_validation() {
        let mut s = store();
        let tx = transaction();
        let prepared = s.workspace_prepare(tx.to_string().as_bytes()).unwrap();
        assert_eq!(s.workspace_export()["revision"], 0);
        s.workspace_import(prepared["journal"].to_string().as_bytes())
            .unwrap();
        assert_eq!(
            s.execute(br#"{"collection":"working_records"}"#)["total"],
            1
        );
        assert!(s.record("objects", "a").unwrap()["record"]["published_length_km"].is_null());
        let mut reloaded = store();
        reloaded
            .workspace_import(prepared["journal"].to_string().as_bytes())
            .unwrap();
        assert_eq!(s.workspace_export(), reloaded.workspace_export());
        assert!(
            s.workspace_prepare(tx.to_string().as_bytes())
                .unwrap_err()
                .contains("conflict")
        );
        let mut invalid = transaction();
        invalid["base_revision"] = json!(1);
        invalid["transaction_id"] = json!("tx-2");
        invalid["operations"]
            .as_array_mut()
            .unwrap()
            .push(json!({"op":"delete","id":"draft:missing"}));
        assert!(s.workspace_prepare(invalid.to_string().as_bytes()).is_err());
        assert_eq!(s.workspace_export()["journal"], prepared["journal"]);
    }
    #[test]
    fn journal_identity_and_history_validation() {
        let s = store();
        let journal = s
            .workspace_prepare(transaction().to_string().as_bytes())
            .unwrap()["journal"]
            .clone();
        for variant in ["hash", "schema", "history", "target", "status", "id"] {
            let mut bad = journal.clone();
            match variant {
                "hash" => bad["bundle_sha256"] = json!("fake"),
                "schema" => bad["schema"] = json!("v99"),
                "history" => bad["events"][0]["base_revision"] = json!(8),
                "target" => {
                    bad["events"][0]["operations"][0]["record"]["target"]["id"] = json!("missing")
                }
                "status" => {
                    bad["events"][0]["operations"][0]["record"]["status"] = json!("published")
                }
                _ => {
                    bad["events"][0]["operations"][0]["record"]["proposed_data"]["id"] =
                        json!("different")
                }
            }
            let mut s = store();
            assert!(
                s.workspace_import(bad.to_string().as_bytes()).is_err(),
                "{variant}"
            );
            assert_eq!(s.workspace_export()["revision"], 0);
        }
    }
    #[test]
    fn utc_dates_and_archived_history() {
        for value in [
            "2026-02-30T12:00:00Z",
            "2026-10-04T99:00:00Z",
            "+026-10-04T12:00:00Z",
            "2026-10-04T12:00:00+01:00",
            "xxxxxxxxxxxxxxxxxxxZ",
        ] {
            assert!(!utc_timestamp(value));
        }
        assert!(utc_timestamp("2024-02-29T12:00:00.123Z"));
        let mut s = store();
        let saved = s
            .workspace_prepare(transaction().to_string().as_bytes())
            .unwrap();
        s.workspace_import(saved["journal"].to_string().as_bytes())
            .unwrap();
        let archive = json!({"base_revision":1,"transaction_id":"archive-1","created_at":"2026-10-04T12:01:00Z","operations":[{"op":"delete","id":"draft:a"}]});
        let saved = s.workspace_prepare(archive.to_string().as_bytes()).unwrap();
        s.workspace_import(saved["journal"].to_string().as_bytes())
            .unwrap();
        assert_eq!(s.workspace_export()["record_count"], 0);
        assert_eq!(
            s.workspace_export()["journal"]["events"]
                .as_array()
                .unwrap()
                .len(),
            2
        );
        assert_eq!(
            s.execute(br#"{"collection":"working_records"}"#)["total"],
            0
        );
    }
}
