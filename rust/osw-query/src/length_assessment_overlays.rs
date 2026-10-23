//! Compose only complete, independently bound length admissions over old tables.
use crate::Bundle;
use serde_json::Value;

pub(crate) fn expected(bundle: &Bundle, previous: &Value) -> Result<Value, String> {
    let mut result = previous.clone();
    for overlay in [crate::labrador_latitude_bound::verified_assessment_overlay(
        bundle,
    )?]
    .into_iter()
    .flatten()
    {
        let rows = result
            .as_array_mut()
            .ok_or("Invalid historical length table")?;
        let indices: Vec<_> = rows
            .iter()
            .enumerate()
            .filter(|(_, row)| row["entity_id"] == overlay["entity_id"])
            .map(|(index, _)| index)
            .collect();
        if indices.len() != 1 {
            return Err("Ambiguous historical length overlay owner".into());
        }
        rows[indices[0]] = overlay;
    }
    Ok(result)
}
