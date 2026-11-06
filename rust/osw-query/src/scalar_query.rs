//! Scalar query operations shared by the atlas and small research stores.
//! This module depends only on serde and has no atlas, spatial or chart assets.
use serde::Deserialize;
use serde_json::{Value, json};
use std::collections::{BTreeMap, BTreeSet};

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Filter {
    pub field: String,
    pub op: String,
    pub value: Value,
}
#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Sort {
    pub field: String,
    #[serde(default = "asc")]
    pub direction: String,
}
fn asc() -> String {
    "asc".into()
}
fn objects() -> String {
    "objects".into()
}

// Keep the atlas request field names. Physical selections are opaque here and
// are rejected by the research scope before any scalar query is executed.
#[derive(Deserialize, Default)]
#[serde(deny_unknown_fields)]
pub(crate) struct Query {
    #[serde(default = "objects")]
    pub collection: String,
    pub text: Option<String>,
    pub record_type: Option<String>,
    pub state_code: Option<String>,
    pub evidence: Option<String>,
    pub spatial: Option<Value>,
    pub geometry_time: Option<Value>,
    pub seasonal: Option<Value>,
    pub network_path: Option<Value>,
    pub taxonomy: Option<Value>,
    #[serde(default)]
    pub filters: Vec<Filter>,
    pub sort: Option<Sort>,
    pub limit: Option<u32>,
    #[serde(default)]
    pub offset: u32,
}

pub(crate) fn field<'a>(record: &'a Value, path: &str) -> Option<&'a Value> {
    path.split('.')
        .try_fold(record, |value, key| value.as_object()?.get(key))
}
pub(crate) fn collect_fields(value: &Value, prefix: &str, fields: &mut BTreeSet<String>) {
    if let Some(object) = value.as_object() {
        for (key, child) in object {
            let path = if prefix.is_empty() {
                key.clone()
            } else {
                format!("{prefix}.{key}")
            };
            fields.insert(path.clone());
            collect_fields(child, &path, fields);
        }
    }
}
pub(crate) fn present(value: Option<&Value>) -> bool {
    value.is_some_and(|v| !v.is_null())
}

// Preserve exact integer/float equality without rounding integers into f64.
pub(crate) fn filter_equal(a: &Value, b: &Value) -> bool {
    if a == b {
        return true;
    }
    let (Some(a), Some(b)) = (a.as_number(), b.as_number()) else {
        return false;
    };
    let (integer, float) = match (a.is_f64(), b.is_f64()) {
        (false, true) => (a, b.as_f64().unwrap()),
        (true, false) => (b, a.as_f64().unwrap()),
        _ => return false,
    };
    if float.fract() != 0.0 {
        return false;
    }
    if let Some(value) = integer.as_i64() {
        float >= -9223372036854775808.0 && float < 9223372036854775808.0 && float as i64 == value
    } else if let Some(value) = integer.as_u64() {
        float >= 0.0 && float < 18446744073709551616.0 && float as u64 == value
    } else {
        false
    }
}
pub(crate) fn compare(a: &Value, b: &Value) -> std::cmp::Ordering {
    match (a.as_f64(), b.as_f64()) {
        (Some(a), Some(b)) => a.total_cmp(&b),
        _ => a
            .as_str()
            .unwrap_or("")
            .to_lowercase()
            .cmp(&b.as_str().unwrap_or("").to_lowercase()),
    }
}
pub(crate) fn matches_filter(row: &Value, filter: &Filter) -> bool {
    let actual = field(row, &filter.field).unwrap_or(&Value::Null);
    match filter.op.as_str() {
        "eq" => filter_equal(actual, &filter.value),
        "ne" => !filter_equal(actual, &filter.value),
        "exists" => filter
            .value
            .as_bool()
            .is_some_and(|v| present(field(row, &filter.field)) == v),
        "contains" => {
            if let (Some(text), Some(needle)) = (actual.as_str(), filter.value.as_str()) {
                text.to_lowercase().contains(&needle.to_lowercase())
            } else if let Some(array) = actual.as_array() {
                array.iter().any(|v| v == &filter.value)
            } else {
                false
            }
        }
        "gt" => actual
            .as_f64()
            .zip(filter.value.as_f64())
            .is_some_and(|(a, b)| a > b),
        "lt" => actual
            .as_f64()
            .zip(filter.value.as_f64())
            .is_some_and(|(a, b)| a < b),
        _ => false,
    }
}
pub(crate) fn sort_rows(rows: &mut Vec<&Value>, sort: Option<(&str, bool)>) {
    if let Some((key, descending)) = sort {
        rows.sort_by(|a, b| {
            let av = field(a, key);
            let bv = field(b, key);
            let order = match (present(av), present(bv)) {
                (false, true) => std::cmp::Ordering::Greater,
                (true, false) => std::cmp::Ordering::Less,
                (false, false) => std::cmp::Ordering::Equal,
                _ => {
                    let result = compare(av.unwrap(), bv.unwrap());
                    if descending { result.reverse() } else { result }
                }
            };
            order.then_with(|| a["id"].as_str().cmp(&b["id"].as_str()))
        });
    } else {
        rows.sort_by(|a, b| a["id"].as_str().cmp(&b["id"].as_str()));
    }
}

pub(crate) struct ScalarStore {
    pub collections: BTreeMap<String, Vec<Value>>,
    pub fields: BTreeMap<String, BTreeSet<String>>,
    ids: BTreeMap<String, BTreeMap<String, usize>>,
}
impl ScalarStore {
    pub fn new(collections: BTreeMap<String, Vec<Value>>) -> Result<Self, String> {
        let mut ids = BTreeMap::new();
        let mut fields = BTreeMap::new();
        for (name, rows) in &collections {
            let mut index = BTreeMap::new();
            let mut keys = BTreeSet::new();
            for (i, row) in rows.iter().enumerate() {
                let id = row["id"]
                    .as_str()
                    .filter(|s| !s.is_empty())
                    .ok_or("Missing local-extent ID")?;
                if index.insert(id.to_owned(), i).is_some() {
                    return Err("Duplicate local-extent ID".into());
                }
                collect_fields(row, "", &mut keys);
            }
            ids.insert(name.clone(), index);
            fields.insert(name.clone(), keys);
        }
        Ok(Self {
            collections,
            fields,
            ids,
        })
    }
    fn known_field(&self, collection: &str, name: &str) -> Result<(), String> {
        if !self.fields[collection].contains(name) {
            return Err(format!("Unknown field {name} in {collection}"));
        }
        Ok(())
    }
    pub fn query(&self, query: Query) -> Result<Value, String> {
        if query.record_type.is_some()
            || query.state_code.is_some()
            || query.evidence.is_some()
            || query.spatial.is_some()
            || query.geometry_time.is_some()
            || query.seasonal.is_some()
            || query.network_path.is_some()
            || query.taxonomy.is_some()
        {
            return Err("Scalar stores do not support physical or atlas selections".into());
        }
        let records = self
            .collections
            .get(&query.collection)
            .ok_or_else(|| format!("Unknown collection {}", query.collection))?;
        let limit = query.limit.unwrap_or(100);
        if !(1..=500).contains(&limit) {
            return Err("Limit must be 1..500".into());
        }
        if query.filters.len() > 20 || query.text.as_ref().is_some_and(|s| s.len() > 1000) {
            return Err("Query exceeds input limits".into());
        }
        for filter in &query.filters {
            self.known_field(&query.collection, &filter.field)?;
            if !["eq", "ne", "contains", "exists", "gt", "lt"].contains(&filter.op.as_str()) {
                return Err(format!("Unsupported operator {}", filter.op));
            }
            if ["gt", "lt"].contains(&filter.op.as_str()) && !filter.value.is_number() {
                return Err("Numeric comparison requires a number".into());
            }
            if filter.op == "contains" && !filter.value.is_string() {
                return Err("Contains requires text".into());
            }
            if filter.op == "exists" && !filter.value.is_boolean() {
                return Err("Exists requires true or false".into());
            }
        }
        if let Some(sort) = &query.sort {
            self.known_field(&query.collection, &sort.field)?;
            if !["asc", "desc"].contains(&sort.direction.as_str()) {
                return Err("Sort direction must be asc or desc".into());
            }
            if records
                .iter()
                .filter_map(|r| field(r, &sort.field))
                .any(|v| !v.is_null() && !v.is_string() && !v.is_number())
            {
                return Err("Sort field must be text or numeric".into());
            }
        }
        let text = query.text.as_ref().map(|s| s.trim().to_lowercase());
        let mut matches: Vec<_> = records
            .iter()
            .filter(|r| {
                !text.as_ref().is_some_and(|text| {
                    !text.is_empty() && !r.to_string().to_lowercase().contains(text)
                }) && query.filters.iter().all(|f| matches_filter(r, f))
            })
            .collect();
        sort_rows(
            &mut matches,
            query
                .sort
                .as_ref()
                .map(|s| (s.field.as_str(), s.direction == "desc")),
        );
        let total = matches.len();
        let rows: Vec<_> = matches
            .into_iter()
            .skip(query.offset as usize)
            .take(limit as usize)
            .cloned()
            .collect();
        Ok(
            json!({"taxonomy_scope":null,"network_paths":null,"ok":true,"engine":"rust-osw-query-v1",
            "collection":query.collection,"total":total,"offset":query.offset,"limit":limit,"rows":rows,
            "map_scene":null,"chart_scene":null,"spatial_scope":null}),
        )
    }
    pub fn record(&self, collection: &str, id: &str) -> Result<Value, String> {
        let index = self
            .ids
            .get(collection)
            .and_then(|ids| ids.get(id))
            .ok_or_else(|| format!("Record not found: {collection}/{id}"))?;
        Ok(
            json!({"ok":true,"collection":collection,"record":self.collections[collection][*index],"taxonomy_context":null}),
        )
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn integer_equality_never_rounds_a_large_integer_into_another_value() {
        assert!(filter_equal(&json!(5), &json!(5.0)));
        assert!(!filter_equal(
            &json!(9007199254740993u64),
            &json!(9007199254740992.0)
        ));
        assert!(!filter_equal(
            &json!(u64::MAX),
            &json!(18446744073709551616.0)
        ));
        assert!(!filter_equal(&Value::Null, &json!(0)));
    }
    #[test]
    fn nulls_stay_last_in_both_sort_directions_with_stable_id_ties() {
        let values = [
            json!({"id":"c","value":null}),
            json!({"id":"b","value":2}),
            json!({"id":"a","value":2}),
        ];
        for descending in [false, true] {
            let mut rows = values.iter().collect();
            sort_rows(&mut rows, Some(("value", descending)));
            assert_eq!(
                rows.iter()
                    .map(|r| r["id"].as_str().unwrap())
                    .collect::<Vec<_>>(),
                vec!["a", "b", "c"]
            );
        }
    }
    #[test]
    fn nested_fields_null_existence_arrays_and_case_insensitive_text_match() {
        let row = json!({"id":"x","meta":{"value":null},"tags":["Source"],"label":"Ocean"});
        for filter in [
            json!({"field":"meta.value","op":"exists","value":false}),
            json!({"field":"tags","op":"contains","value":"Source"}),
            json!({"field":"label","op":"contains","value":"OCE"}),
        ] {
            assert!(matches_filter(
                &row,
                &serde_json::from_value(filter).unwrap()
            ));
        }
    }

    #[test]
    fn pagination_counts_have_the_same_width_on_native_and_wasm() {
        let query: Query =
            serde_json::from_value(json!({"collection":"x","offset":4294967295u64})).unwrap();
        assert_eq!(query.offset, u32::MAX);
        for field in ["offset", "limit"] {
            let mut request = json!({"collection":"x"});
            request[field] = json!(4294967296u64);
            assert!(serde_json::from_value::<Query>(request).is_err());
        }
    }
}
