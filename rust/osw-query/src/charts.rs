//! Scoped sample charts. Original source domains; no interpolation or gap filling.
use serde_json::{Value, json};
use std::collections::BTreeMap;

pub fn scene(matches: &[&Value], corpus: &[Value]) -> Value {
    let mut grouped: BTreeMap<String, Vec<&Value>> = BTreeMap::new();
    for row in matches {
        let key = format!(
            "{}:{}",
            row["diagnostic_id"].as_str().unwrap_or(""),
            row["phase_path"].as_str().unwrap_or("monthly")
        );
        grouped.entry(key).or_default().push(row);
    }
    let mut panels = Vec::new();
    for (id, mut rows) in grouped {
        let first = rows[0];
        let longitude = first["sample_family"] == "kuroshio_seasonal_profile_plot";
        let filtered = first["sample_family"] == "kuroshio_filtered_curve_plot";
        let dated = [
            "gulf_stream_dated_half_peak_section",
            "loop_dated_half_peak_section",
        ]
        .iter()
        .any(|f| first["sample_family"] == *f);
        let xfield = if dated {
            "observation_date"
        } else if filtered {
            "plot_year"
        } else if longitude {
            "longitude_degrees_east"
        } else {
            "month"
        };
        let xvalue = |r: &Value| {
            if dated {
                r[xfield]
                    .as_str()
                    .and_then(crate::temporal::day_index)
                    .map(|n| n as f64)
            } else {
                r[xfield].as_f64()
            }
        };
        rows.sort_by(|a, b| xvalue(a).unwrap_or(0.).total_cmp(&xvalue(b).unwrap_or(0.)));
        let source: Vec<_> = corpus
            .iter()
            .filter(|r| r["diagnostic_id"] == first["diagnostic_id"])
            .collect();
        let xs: Vec<_> = source.iter().filter_map(|r| xvalue(r)).collect();
        let xmin = if filtered {
            1993.
        } else if longitude || dated {
            xs.iter().copied().fold(f64::INFINITY, f64::min)
        } else {
            1.
        };
        let xmax = if filtered {
            2009.
        } else if longitude || dated {
            xs.iter().copied().fold(f64::NEG_INFINITY, f64::max)
        } else {
            12.
        };
        let largest = source
            .iter()
            .flat_map(|r| {
                [
                    r["plot_reading_interval_km"].get(1).and_then(Value::as_f64),
                    r["diagnostic_sensitivity_interval_km"]
                        .get(1)
                        .and_then(Value::as_f64),
                    r["value_km"].as_f64(),
                ]
                .into_iter()
                .flatten()
            })
            .fold(0., f64::max);
        let ymax = (largest / 50.).ceil().max(1.) * 50.;
        let px = |x: f64| 58. + (x - xmin) / (xmax - xmin).max(1.) * 558.;
        let py = |y: f64| 220. - y / ymax * 180.;
        let mut ticks: Vec<_> = if filtered {
            (1993..=2009).step_by(2).map(f64::from).collect()
        } else if longitude || dated {
            xs.clone()
        } else {
            (1..=12).map(f64::from).collect()
        };
        ticks.sort_by(f64::total_cmp);
        ticks.dedup();
        if dated {
            ticks = (0..5)
                .map(|i| (xmin + (xmax - xmin) * f64::from(i) / 4.).round())
                .collect();
            ticks.dedup();
        }
        let points:Vec<_>=rows.iter().map(|r| {
            let x=xvalue(r).unwrap_or(xmin);let value=r["value_km"].as_f64();
            let interval=r["plot_reading_interval_km"].as_array().and_then(|a|Some((a.first()?.as_f64()?,a.get(1)?.as_f64()?)));
            let sensitivity=r["diagnostic_sensitivity_interval_km"].as_array().and_then(|a|Some((a.first()?.as_f64()?,a.get(1)?.as_f64()?)));
            json!({"sample_id":r["id"],"label":r["label"],"x_value":x,"value_km":r["value_km"],"plot_reading_interval_km":r["plot_reading_interval_km"],
                "observation_date":r["observation_date"],"source_algorithm":r["source_algorithm"],"diagnostic_sensitivity_interval_km":r["diagnostic_sensitivity_interval_km"],
                "primitive":{"kind":if value.is_some(){"reading"}else{"missing"},"x":px(x),"y":value.map(py),"missing_y":255.,"interval_y":interval.map(|(lo,hi)|[py(lo),py(hi)]),"sensitivity_y":sensitivity.map(|(lo,hi)|[py(lo),py(hi)])}})
        }).collect();
        let title = if filtered {
            "Kuroshio — published half-year-filtered regional width curve".into()
        } else if first["sample_family"] == "loop_dated_half_peak_section" {
            format!(
                "Loop inflow - {} recorded-day spans at 21.875 N",
                if first["source_context"]["product_key"] == "noaa" {
                    "NOAA"
                } else {
                    "DUACS"
                }
            )
        } else if first["sample_family"] == "florida_monthly_half_peak_plot" {
            "Florida Current - 2005-2006 monthly surface-jet widths at 25.42 N".into()
        } else if dated {
            "Gulf Stream system — recorded-day section diagnostics at 70 W".into()
        } else if longitude {
            format!("Kuroshio — {}", first["phase_label"].as_str().unwrap_or(""))
        } else if first["current_id"] == "leeuwin" {
            "Leeuwin — historical monthly fitted widths".into()
        } else if first["sample_family"] == "basin_monthly_component_section"
            && first["source_context"]["is_climatology"] == true
        {
            format!(
                "{} — local component spans (current width unresolved)",
                first["source_context"]["period_label"]
                    .as_str()
                    .unwrap_or("Calendar-month climatology")
            )
        } else if first["sample_family"] == "basin_monthly_component_section" {
            format!(
                "{} — {} local component spans (current width unresolved)",
                first["current_id"].as_str().unwrap_or(""),
                first["year"]
            )
        } else {
            "Pacific NECC — 2013 monthly diagnostics at 140 W".into()
        };
        let mut panel = json!({"id":id,"title":title,"metric":first["metric"],"source_context":first["source_context"],"source_phase":first["source_phase"],
            "view_box":[0,0,640,280],"x_field":xfield,"x_domain":[xmin,xmax],"y_domain_km":[0,ymax],
            "x_ticks":ticks.iter().map(|x|json!({"value":x,"x":px(*x),"label":if dated {json!(crate::temporal::day_label(*x as i64))}else{Value::Null}})).collect::<Vec<_>>(),
            "y_ticks":(0..=4).map(|i|{let value=ymax*f64::from(i)/4.;json!({"value_km":value,"y":py(value)})}).collect::<Vec<_>>(),
            "points":points,"matching_samples":rows.len(),"missing_samples":rows.iter().filter(|r|r["value_km"].is_null()).count()});
        if filtered {
            panel["sample_time_note"] = json!(
                "Monthly plot-coordinate samples of a half-year-filtered curve; not raw monthly means or exact observation dates. Kernel and window alignment are unresolved."
            );
        }
        panels.push(panel);
    }
    json!({"panels":panels,"matching_samples":matches.len(),"scope":"All matching samples before table pagination. Axes use the full source diagnostic and remain fixed under filtering. Dated axes use elapsed Gregorian days, preserving gaps. Solid whiskers are plot-reading allowances; dashed whiskers are finite threshold-choice sensitivity. Neither is a confidence interval. Missing readings are separate from the value axis. No interpolation, annual extrema, cross-method ranking or geographic width footprint."})
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn filtered_curve_uses_plot_years_without_synthesizing_observation_dates() {
        let corpus = vec![
            json!({"id":"a","diagnostic_id":"d","sample_family":"kuroshio_filtered_curve_plot","plot_year":1993.1,"value_km":200,"observation_date":null}),
            json!({"id":"b","diagnostic_id":"d","sample_family":"kuroshio_filtered_curve_plot","plot_year":2008.9,"value_km":220,"observation_date":null}),
        ];
        let full = scene(&corpus.iter().collect::<Vec<_>>(), &corpus);
        let one = scene(&[&corpus[1]], &corpus);
        assert_eq!(full["panels"][0]["x_field"], "plot_year");
        assert_eq!(one["panels"][0]["x_domain"], json!([1993., 2009.]));
        assert_eq!(
            one["panels"][0]["points"][0],
            full["panels"][0]["points"][1]
        );
        assert!(one["panels"][0]["points"][0]["observation_date"].is_null());
        assert!(
            one["panels"][0]["sample_time_note"]
                .as_str()
                .unwrap()
                .contains("not raw monthly means")
        );
    }
    #[test]
    fn filtered_axes_and_separate_missing_strip() {
        let corpus = vec![
            json!({"id":"a","diagnostic_id":"d","current_id":"leeuwin","sample_family":"leeuwin_monthly_fitted_plot","month":1,"value_km":100,"plot_reading_interval_km":[90,110]}),
            json!({"id":"b","diagnostic_id":"d","current_id":"leeuwin","sample_family":"leeuwin_monthly_fitted_plot","month":2,"value_km":null}),
            json!({"id":"c","diagnostic_id":"d","current_id":"leeuwin","sample_family":"leeuwin_monthly_fitted_plot","month":3,"value_km":200,"plot_reading_interval_km":[180,220]}),
        ];
        let full = scene(&corpus.iter().collect::<Vec<_>>(), &corpus);
        let filtered = scene(&[&corpus[0]], &corpus);
        assert_eq!(
            full["panels"][0]["y_domain_km"],
            filtered["panels"][0]["y_domain_km"]
        );
        assert_eq!(filtered["panels"][0]["x_domain"], json!([1., 12.]));
        assert_eq!(
            full["panels"][0]["points"][1]["primitive"]["kind"],
            "missing"
        );
        assert!(full["panels"][0]["points"][1]["primitive"]["y"].is_null());
        assert_eq!(
            full["panels"][0]["points"][1]["primitive"]["missing_y"],
            255.
        );
        assert_eq!(full["matching_samples"], 3);
    }
    #[test]
    fn recorded_dates_preserve_elapsed_gaps() {
        let corpus:Vec<_>=["2025-01-15","2025-02-15","2026-09-27"].iter().enumerate().map(|(i,d)|
            json!({"id":i.to_string(),"diagnostic_id":"d","current_id":"gulf-stream-system","sample_family":"gulf_stream_dated_half_peak_section","observation_date":d,"value_km":90,"diagnostic_sensitivity_interval_km":[80,110]})).collect();
        let full = scene(&corpus.iter().collect::<Vec<_>>(), &corpus);
        let points = full["panels"][0]["points"].as_array().unwrap();
        assert_eq!(
            points[1]["x_value"].as_f64().unwrap() - points[0]["x_value"].as_f64().unwrap(),
            31.
        );
        assert!(
            points[2]["x_value"].as_f64().unwrap() - points[1]["x_value"].as_f64().unwrap() > 500.
        );
        let one = scene(&[&corpus[1]], &corpus);
        assert_eq!(one["panels"][0]["x_domain"], full["panels"][0]["x_domain"]);
        assert_eq!(one["panels"][0]["points"][0], points[1]);
        assert!(points[0]["primitive"]["sensitivity_y"].is_array());
    }
}
