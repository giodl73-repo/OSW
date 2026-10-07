//! Stateless display projection/fit for checked atlas source geometry.
use serde::Deserialize;
use serde_json::{Value, json};
#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct Request {
    op: String,
    coordinates: Value,
    #[serde(default)]
    closed: bool,
}
pub(crate) fn root((x, y): (f64, f64)) -> (f64, f64) {
    (60. + x / 360. * 1480., 90. + y / 180. * 740.)
}
pub fn execute(bytes: &[u8]) -> Result<Value, String> {
    let r: Request = serde_json::from_slice(bytes).map_err(|e| e.to_string())?;
    match r.op.as_str() {
        "project" => {
            if r.closed {
                return Err("Closed is only valid for paths".into());
            }
            let (x, y) =
                root(crate::map::point(&r.coordinates).ok_or("Invalid longitude/latitude")?);
            Ok(json!({"ok":true,"point":[x,y]}))
        }
        "path" => {
            let d = crate::map::path_formatted(&r.coordinates, r.closed, |p| {
                let (x, y) = root(p);
                format!("{x},{y}")
            })
            .ok_or("Invalid path or polygon requiring seam clipping")?;
            Ok(json!({"ok":true,"d":d}))
        }
        "fit" => {
            if r.closed {
                return Err("Closed is only valid for paths".into());
            }
            let coords = r
                .coordinates
                .as_array()
                .ok_or("Fit requires geographic points")?;
            if coords.is_empty() {
                return Ok(json!({"ok":true,"view_box":null}));
            }
            let points: Vec<_> = coords
                .iter()
                .map(|p| {
                    crate::map::point(p)
                        .map(root)
                        .ok_or("Invalid fit coordinates")
                })
                .collect::<Result<_, _>>()?;
            let min_x = points.iter().map(|p| p.0).fold(f64::INFINITY, f64::min);
            let max_x = points.iter().map(|p| p.0).fold(f64::NEG_INFINITY, f64::max);
            let min_y = points.iter().map(|p| p.1).fold(f64::INFINITY, f64::min);
            let max_y = points.iter().map(|p| p.1).fold(f64::NEG_INFINITY, f64::max);
            let width = ((max_x - min_x) * 1.4)
                .max((max_y - min_y) * 2.8)
                .max(if points.len() == 1 { 160. } else { 16. })
                .min(1480.);
            let x = ((min_x + max_x) / 2. - width / 2.).clamp(60., 1540. - width);
            let y = ((min_y + max_y) / 2. - width / 4.).clamp(90., 830. - width / 2.);
            Ok(json!({"ok":true,"view_box":[x,y,width,width/2.]}))
        }
        _ => Err("Unknown cartographic operation".into()),
    }
}
#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn root_projection_fit_and_seams() {
        let run = |v: &Value| execute(&serde_json::to_vec(v).unwrap());
        assert_eq!(
            run(&json!({"op":"project","coordinates":[0,0]})).unwrap()["point"],
            json!([800., 460.])
        );
        assert_eq!(
            run(&json!({"op":"fit","coordinates":[[0,0]]})).unwrap()["view_box"],
            json!([720., 420., 160., 80.])
        );
        assert_eq!(
            run(&json!({"op":"fit","coordinates":[]})).unwrap()["view_box"],
            Value::Null
        );
        let line = run(&json!({"op":"path","coordinates":[[179,0],[-179,1]]})).unwrap();
        assert_eq!(line["d"].as_str().unwrap().matches('M').count(), 2);
        assert!(run(&json!({"op":"path","closed":true,"coordinates":[[179,0],[-179,0],[-179,1],[179,0]]})).is_err());
        for r in [
            json!({"op":"project","coordinates":[0,91]}),
            json!({"op":"fit","coordinates":[[181,0]]}),
            json!({"op":"path","coordinates":[[0,0]]}),
            json!({"op":"unrecognized","coordinates":[]}),
            json!({"op":"fit","coordinates":[],"extra":true}),
        ] {
            assert!(run(&r).is_err());
        }
    }
}
