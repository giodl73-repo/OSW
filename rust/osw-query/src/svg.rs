//! Portable SVG display export. Source values are escaped, never interpreted as markup.
use serde_json::{Value, json};
use std::fmt::Write;

fn xml(value: &str) -> String {
    value
        .replace('&', "&amp;")
        .replace('<', "&lt;")
        .replace('>', "&gt;")
        .replace('"', "&quot;")
        .replace('\'', "&apos;")
        .chars()
        .filter(|c| {
            *c == '\n'
                || *c == '\r'
                || *c == '\t'
                || (*c >= '\u{20}' && *c != '\u{fffe}' && *c != '\u{ffff}')
        })
        .collect()
}

pub fn render(scene: &Value, query: &Value, bundle_hash: &Value) -> Result<String, String> {
    if !scene.is_object() {
        return Err("SVG maps require an objects query".into());
    }
    let mut out = String::from(
        r##"<svg xmlns="http://www.w3.org/2000/svg" width="1440" height="824" viewBox="0 0 360 206" role="img" aria-labelledby="export-title export-desc"><title id="export-title">OSW query map</title><desc id="export-desc">All matching stored geometry across every results page. Names appear on hover. Display coordinates are not scientific measurements.</desc><style>.mark{stroke:#68e3d1;stroke-width:.5;fill:none}.point{fill:#123d4a;stroke:#d3eeed}.gateway{stroke:#f4c45e;stroke-dasharray:.5 .5}.polygon{stroke:#dba2fc;fill:#ae7bd7;fill-opacity:.25}.dated{stroke:#ffbb71;stroke-dasharray:1.25 .75}.context{opacity:.22}.mark:hover,.mark:focus{stroke:white;stroke-width:1;outline:none}.state{fill:#ffd96b;fill-opacity:.12;stroke:#ffe29c;stroke-width:.5;stroke-dasharray:1.5 .75}.caption{fill:#d3eeed;font-family:system-ui,sans-serif;font-size:3px}</style><rect width="360" height="206" fill="#123d4a"/>"##,
    );
    let mut receipt = json!({"schema":"osw.query-svg.v1", "bundle_sha256":bundle_hash,"query":query,
        "projection":scene["projection"],"matching_objects":scene["matching_objects"],"mapped_objects":scene["mapped_objects"],
        "unmapped_objects":scene["unmapped_objects"],"omitted_features":scene["omitted_features"],"scope":scene["scope"],
        "selected_state_code":scene["selected_state_code"],"features":scene["features"],"spatial_relations":scene["spatial_relations"]});
    if !scene["geometry_time"].is_null() {
        receipt["geometry_time"] = scene["geometry_time"].clone();
    }
    write!(out, "<metadata>{}</metadata>", xml(&receipt.to_string())).unwrap();
    // Repository-controlled coastline, with its original coordinate system retained.
    let ground = include_str!("../../../figures/ocean-motion-dashboard-ground.svg").replacen(
        "<svg ",
        "<svg x=\"0\" y=\"0\" width=\"360\" height=\"180\" opacity=\".6\" ",
        1,
    );
    out.push_str(&ground);
    for feature in scene["state_features"].as_array().into_iter().flatten() {
        write!(
            out,
            "<path class=\"state\" fill-rule=\"evenodd\" d=\"{}\"/>",
            xml(feature["primitive"]["d"].as_str().unwrap_or(""))
        )
        .unwrap();
    }
    for feature in scene["features"].as_array().into_iter().flatten() {
        let primitive = &feature["primitive"];
        let kind = primitive["kind"].as_str().unwrap_or("");
        let role = feature["role"].as_str().unwrap_or("");
        let mut class = format!("mark {kind}");
        if role == "shared_regional_gateway" {
            class.push_str(" gateway");
        }
        if kind == "line" && role != "editorial_reference_route" {
            class.push_str(" dated");
        }
        if feature["matches_selected_state"] == false {
            class.push_str(" context");
        }
        if feature["undated_context"] == true {
            class.push_str(" context");
        }
        let mut name = format!(
            "{} · {}{}{}",
            feature["label"].as_str().unwrap_or(""),
            role,
            feature["observation_date"]
                .as_str()
                .map(|d| format!(" · {d}"))
                .unwrap_or_default(),
            feature["note"]
                .as_str()
                .map(|n| format!(" · {n}"))
                .unwrap_or_default()
        );
        if feature["undated_context"] == true {
            name.push_str(" · undated context");
        }
        let tag = if kind == "point" { "circle" } else { "path" };
        write!(out, "<{tag} class=\"{}\" data-entity=\"{}\" data-role=\"{}\" tabindex=\"0\" aria-label=\"{}\" fill-rule=\"evenodd\" ", xml(&class), xml(feature["entity_id"].as_str().unwrap_or("")), xml(role), xml(&name)).unwrap();
        if kind == "point" {
            write!(
                out,
                "cx=\"{}\" cy=\"{}\" r=\"1.25\"",
                primitive["x"], primitive["y"]
            )
            .unwrap();
        } else {
            write!(out, "d=\"{}\"", xml(primitive["d"].as_str().unwrap_or(""))).unwrap();
        }
        write!(out, "><title>{}</title></{tag}>", xml(&name)).unwrap();
    }
    let count = format!(
        "{} of {} matching records mapped · {} marks · {} records without rendered geography · {} omitted features",
        scene["mapped_objects"],
        scene["matching_objects"],
        scene["features"].as_array().map_or(0, Vec::len),
        scene["unmapped_objects"],
        scene["omitted_features"].as_array().map_or(0, Vec::len)
    );
    for (y, text) in [
        (186, count.as_str()),
        (
            192,
            "Teal: editorial routes · Orange: dated lines · Purple: polygons · Hollow: locators · Amber dashed: shared gateways",
        ),
        (
            198,
            "Hover or focus for names. Coarse OSW coastline; locators and gateways are not occupied footprints.",
        ),
        (
            204,
            "Equirectangular display only. Stored geometries retain their source scope; this is not a length or width measurement.",
        ),
    ] {
        write!(
            out,
            "<text class=\"caption\" x=\"3\" y=\"{y}\">{}</text>",
            xml(text)
        )
        .unwrap();
    }
    if let Some(time) = scene.get("geometry_time") {
        let label = format!(
            "Recorded observations {} through {}; undated marks are context only. No interpolation.",
            time["from"].as_str().unwrap_or(""),
            time["to"].as_str().unwrap_or("")
        );
        // Separate accessible description without overwriting the display legend.
        write!(out, "<desc>{}</desc>", xml(&label)).unwrap();
        write!(
            out,
            "<text class=\"caption\" x=\"3\" y=\"210\">{}</text>",
            xml(&label)
        )
        .unwrap();
        out = out
            .replacen(
                "height=\"824\" viewBox=\"0 0 360 206\"",
                "height=\"848\" viewBox=\"0 0 360 212\"",
                1,
            )
            .replacen(
                "<rect width=\"360\" height=\"206\"",
                "<rect width=\"360\" height=\"212\"",
                1,
            );
    }
    out.push_str("</svg>");
    Ok(out)
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn escapes_source_markup_and_preserves_scene_scope() {
        let record = json!({"id":"current:<bad>","label":"<script>&\"", "map_features":[{"role":"locator", "geometry":{"type":"Point","coordinates":[0,0]}}]});
        let scene = crate::map::scene(&[&record]);
        let svg = render(&scene, &json!({"limit":1}), &json!("hash")).unwrap();
        assert!(!svg.contains("<script>"));
        assert!(svg.contains("data-entity=\"current:&lt;bad&gt;\""));
        assert!(svg.contains("cx=\"180.0\" cy=\"90.0\""));
        assert!(svg.contains("&quot;limit&quot;:1"));
        assert!(render(&Value::Null, &json!({}), &json!("hash")).is_err());
    }
}
