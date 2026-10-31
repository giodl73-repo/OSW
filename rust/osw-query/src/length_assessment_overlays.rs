//! Compose only complete, independently bound length admissions over old tables.
use crate::Bundle;
use serde_json::Value;

pub(crate) fn expected(bundle: &Bundle, previous: &Value) -> Result<Value, String> {
    let mut result = previous.clone();
    for overlay in [
        crate::labrador_latitude_bound::verified_assessment_overlay(bundle)?,
        crate::baffin_latitude_bound::verified_assessment_overlay(bundle)?,
        crate::ke_regional_length::verified_assessment_overlay(bundle)?,
    ]
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
    // New identities have their own explicitly unmeasured assessments. Keep
    // the historical table byte-for-value and in order; never recompute ranks.
    for addition in crate::current_gap_admissions::verified_length_assessments(bundle)?
        .into_iter()
        .chain(crate::equatorial_basin_identities::verified_length_assessments(bundle)?)
    {
        let rows = result
            .as_array_mut()
            .ok_or("Invalid historical length table")?;
        if rows
            .iter()
            .any(|row| row["id"] == addition["id"] || row["entity_id"] == addition["entity_id"])
        {
            return Err("Duplicate admitted length assessment owner".into());
        }
        rows.push(addition);
    }
    if let Some(overlay) = crate::indian_sec_model_grid_lengths::verified_assessment_overlay(bundle)? {
        let rows = result.as_array_mut().ok_or("Invalid model-grid length assessment table")?;
        let indices: Vec<_> = rows.iter().enumerate().filter(|(_, row)| row["entity_id"] == overlay["entity_id"]).map(|(index, _)| index).collect();
        if indices.len() != 1 { return Err("Ambiguous regional model-grid length assessment owner".into()); }
        rows[indices[0]] = overlay;
    }
    Ok(result)
}
