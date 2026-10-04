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
/// Gregorian day number, used only to space recorded dates on chart axes.
pub fn day_index(value: &str) -> Option<i64> {
    if !valid_day(value) {
        return None;
    }
    let year: i64 = value[..4].parse().ok()?;
    let month: usize = value[5..7].parse().ok()?;
    let day: i64 = value[8..].parse().ok()?;
    let prior = year - 1;
    let leap = year % 4 == 0 && (year % 100 != 0 || year % 400 == 0);
    let months = [
        31,
        if leap { 29 } else { 28 },
        31,
        30,
        31,
        30,
        31,
        31,
        30,
        31,
        30,
        31,
    ];
    Some(
        365 * prior + prior / 4 - prior / 100
            + prior / 400
            + months[..month - 1].iter().sum::<i64>()
            + day
            - 1,
    )
}
pub fn day_label(index: i64) -> Option<String> {
    if index < 0 || index > day_index("9999-12-31")? {
        return None;
    }
    let (mut low, mut high) = (1, 10000);
    while high - low > 1 {
        let middle = (low + high) / 2;
        if day_index(&format!("{middle:04}-01-01"))? <= index {
            low = middle;
        } else {
            high = middle;
        }
    }
    for month in 1..=12 {
        let first = day_index(&format!("{low:04}-{month:02}-01"))?;
        let next = if month == 12 {
            day_index(&format!("{:04}-01-01", low + 1)).unwrap_or(index + 1)
        } else {
            day_index(&format!("{low:04}-{:02}-01", month + 1))?
        };
        if index < next {
            return Some(format!("{low:04}-{month:02}-{:02}", index - first + 1));
        }
    }
    None
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
        assert_eq!(
            day_index("2024-03-01").unwrap() - day_index("2024-02-28").unwrap(),
            2
        );
        assert_eq!(
            day_index("1900-03-01").unwrap() - day_index("1900-02-28").unwrap(),
            1
        );
        assert_eq!(
            day_index("2000-03-01").unwrap() - day_index("2000-02-28").unwrap(),
            2
        );
        assert!(day_index("2025-02-29").is_none());
        for day in [
            "0001-01-01",
            "1900-03-01",
            "2000-02-29",
            "2025-01-15",
            "2026-09-27",
            "9999-12-31",
        ] {
            assert_eq!(day_label(day_index(day).unwrap()).as_deref(), Some(day));
        }
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
