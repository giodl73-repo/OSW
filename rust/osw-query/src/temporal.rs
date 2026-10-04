//! Exact recorded observation days. No persistence, interpolation or season inference.
use serde::Deserialize;
use serde_json::Value;
#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
pub struct GeometryTime {
    pub from: String,
    pub to: String,
    #[serde(default)]
    pub include_undated: bool,
}
pub fn valid_day(value: &str) -> bool {
    value.len() == 10
        && value.is_ascii()
        && crate::workspace::utc_timestamp(&format!("{value}T00:00:00Z"))
}
impl GeometryTime {
    pub fn validate(&self) -> Result<(), String> {
        if !valid_day(&self.from) || !valid_day(&self.to) || self.from > self.to {
            return Err(
                "Geometry time requires ordered inclusive YYYY-MM-DD calendar dates".into(),
            );
        }
        Ok(())
    }
    pub fn includes(&self, feature: &Value) -> bool {
        match feature.get("observation_date") {
            None | Some(Value::Null) => self.include_undated,
            Some(Value::String(day)) if valid_day(day) => day >= &self.from && day <= &self.to,
            _ => false,
        }
    }
}
#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;
    #[test]
    fn calendar_bounds_and_unknown_times() {
        let mut time = GeometryTime {
            from: "2024-02-29".into(),
            to: "2024-03-01".into(),
            include_undated: false,
        };
        assert!(time.validate().is_ok());
        assert!(time.includes(&json!({"observation_date":"2024-02-29"})));
        assert!(!time.includes(&json!({"observation_date":"2024-03-02"})));
        assert!(!time.includes(&json!({})));
        time.include_undated = true;
        assert!(time.includes(&json!({"observation_date":null})));
        assert!(!time.includes(&json!({"observation_date":"2024-02-30"})));
        assert!(!time.includes(&json!({"observation_date":"winter"})));
        time.from = "2025-02-29".into();
        assert!(time.validate().is_err());
        time.from = "2024-03-02".into();
        assert!(time.validate().is_err());
    }
}
