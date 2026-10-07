//! Editorial schematic geometry; crossings never assert physical connectivity.
use serde_json::{Value, json};
use std::collections::{BTreeMap, BTreeSet};

fn snap(p: &Value) -> Result<[f64; 2], String> {
    let lon = p[0].as_f64().ok_or("Missing schematic longitude")?;
    let lat = p[1].as_f64().ok_or("Missing schematic latitude")?;
    if !lon.is_finite() || !lat.is_finite() || lon.abs() > 180. || lat.abs() > 90. {
        return Err("Invalid schematic coordinate".into());
    }
    Ok([
        ((60. + (lon + 180.) / 360. * 1480.) / 8.).round() * 8.,
        ((90. + (90. - lat) / 180. * 740.) / 8.).round() * 8.,
    ])
}
fn point(p: [f64; 2]) -> String {
    format!("{},{}", p[0], p[1])
}
fn corner(a: [f64; 2], b: [f64; 2]) -> [f64; 2] {
    let dx = b[0] - a[0];
    let dy = b[1] - a[1];
    let d = dx.abs().min(dy.abs());
    [a[0] + dx.signum() * d, a[1] + dy.signum() * d]
}
fn route(coordinates: &[Value]) -> Result<String, String> {
    let mut previous: Option<[f64; 2]> = None;
    let mut commands = Vec::new();
    for coordinate in coordinates {
        let p = snap(coordinate)?;
        if let Some(a) = previous.filter(|a| (a[0] - p[0]).abs() <= 740.) {
            commands.push(format!("L{}L{}", point(corner(a, p)), point(p)));
        } else {
            commands.push(format!("M{}", point(p)));
        }
        previous = Some(p);
    }
    Ok(commands.join(" "))
}
fn separate(p: [f64; 2], placed: &mut Vec<[f64; 2]>) -> Result<[f64; 2], String> {
    let origin = [p[0].clamp(74., 1526.), p[1].clamp(104., 816.)];
    for ring in 0_i32..40 {
        let mut candidates = Vec::new();
        for dx in -ring..=ring {
            for dy in -ring..=ring {
                if dx.abs().max(dy.abs()) == ring {
                    candidates.push([
                        origin[0] + f64::from(dx) * 16.,
                        origin[1] + f64::from(dy) * 16.,
                    ]);
                }
            }
        }
        // Stable sorting preserves the source algorithm's tie order.
        candidates.sort_by(|a, b| {
            (a[0] - origin[0])
                .hypot(a[1] - origin[1])
                .total_cmp(&(b[0] - origin[0]).hypot(b[1] - origin[1]))
        });
        for p in candidates {
            if (74. ..=1526.).contains(&p[0])
                && (104. ..=816.).contains(&p[1])
                && placed
                    .iter()
                    .all(|q| (p[0] - q[0]).hypot(p[1] - q[1]) >= 30.)
            {
                placed.push(p);
                return Ok(p);
            }
        }
    }
    Err("Unable to separate current stations".into())
}

fn basin_group(basin: &str) -> &'static str {
    let b = basin.to_lowercase();
    for (words, name) in [
        (
            &["mediterranean", "adriatic", "aegean", "black sea"][..],
            "Mediterranean and neighboring seas",
        ),
        (&["southern", "antarctic"][..], "Southern Ocean"),
        (&["indian", "arabian", "bengal", "oman"][..], "Indian Ocean"),
        (
            &[
                "pacific",
                "china",
                "japan",
                "tasman",
                "austral",
                "new guinea",
            ][..],
            "Pacific and connected seas",
        ),
        (
            &[
                "atlantic",
                "greenland",
                "gulf of mexico",
                "caribbean",
                "baffin",
                "labrador",
                "norwegian",
                "arctic",
            ][..],
            "Atlantic and Arctic",
        ),
    ] {
        if words.iter().any(|w| b.contains(w)) {
            return name;
        }
    }
    "Other and multiple basins"
}

pub fn scene(
    doc: &Value,
    ids: &[String],
    metric: &str,
    changed: &BTreeSet<&str>,
    box_: [f64; 4],
) -> Result<Value, String> {
    if box_.iter().any(|v| !v.is_finite()) || box_[2] <= 0. || box_[3] <= 0. {
        return Err("Invalid schematic view box".into());
    }
    let all = doc["entries"]
        .as_array()
        .ok_or("Missing schematic inventory")?;
    let selected: BTreeSet<_> = ids.iter().map(String::as_str).collect();
    let colors = [
        "#ec657a", "#51c8db", "#f0bc4e", "#b897f0", "#65dcb3", "#f19855",
    ];
    let size = box_[2] / 1480.;
    let mut stations = Vec::new();
    let mut routes = Vec::new();
    let mut positions = BTreeMap::new();
    let mut placed = Vec::new();
    let mut number = 0;
    let mut filtered = 0;
    let mut routed = 0;
    let mut in_view = 0;
    for row in all.iter().filter(|r| r["type"] == "named_current") {
        number += 1;
        let id = row["id"].as_str().ok_or("Missing current ID")?;
        if !selected.contains(id) {
            continue;
        }
        let color = colors[filtered % colors.len()];
        filtered += 1;
        let features = row["map_features"]
            .as_array()
            .ok_or("Missing schematic features")?;
        let path = features
            .iter()
            .find(|f| f["role"] == "editorial_reference_route");
        let anchor = if let Some(path) = path {
            let coords = path["geometry"]["coordinates"]
                .as_array()
                .filter(|a| !a.is_empty())
                .ok_or("Empty schematic route")?;
            routes.push(json!({"id":id,"color":color,"d":route(coords)?,"note":format!("Octilinear simplification of an editorial route. {}",path["note"].as_str().unwrap_or(""))}));
            routed += 1;
            Some(&coords[coords.len() / 2])
        } else {
            features
                .iter()
                .find(|f| f["geometry"]["type"] == "Point")
                .map(|f| &f["geometry"]["coordinates"])
        };
        let Some(anchor) = anchor else {
            continue;
        };
        let p = separate(snap(anchor)?, &mut placed)?;
        positions.insert(id, p);
        if p[0] >= box_[0]
            && p[0] <= box_[0] + box_[2]
            && p[1] >= box_[1]
            && p[1] <= box_[1] + box_[3]
        {
            in_view += 1;
        }
        let label = row["label"].as_str().ok_or("Missing station label")?;
        let lx = (p[0] + 10. * size)
            .min(box_[0] + box_[2] - label.encode_utf16().count() as f64 * 10. * size - 3. * size)
            .max(box_[0] + 3. * size);
        let ly = (p[1] - 10. * size)
            .min(box_[1] + box_[3] - 5. * size)
            .max(box_[1] + 20. * size);
        let leader = if (ly - p[1]).abs() > 23. * size {
            Some(format!("M0,0L{},{}", lx - p[0], ly - p[1] - 3. * size))
        } else {
            None
        };
        stations.push(json!({"id":id,"number":number,"x":p[0],"y":p[1],"label_x":lx-p[0],"label_y":ly-p[1],"leader_d":leader,
            "covered":row["capabilities"][metric].as_u64().unwrap_or(0)>0,"updated":changed.contains(id),
            "note":format!("Schematic station for {label}. {} Diagram placement is not an observed core, endpoint or intersection.",if path.is_some(){"Placed along an editorial reference route."}else{"Only a name locator is available; no route is drawn."})}));
    }
    let mut connections = Vec::new();
    for c in doc["connections"].as_array().into_iter().flatten() {
        let (Some(a), Some(b)) = (
            c["subject_id"].as_str().and_then(|id| positions.get(id)),
            c["object_id"].as_str().and_then(|id| positions.get(id)),
        ) else {
            continue;
        };
        let d = if (a[0] - b[0]).abs() > 740. {
            let (right, left) = if a[0] > b[0] { (a, b) } else { (b, a) };
            format!("M{}H1540M60,{}H{}", point(*right), left[1], left[0])
        } else {
            format!("M{}L{}L{}", point(*a), point(corner(*a, *b)), point(*b))
        };
        connections.push(json!({"id":c["id"],"d":d}));
    }
    let mut basins: Vec<(&str, Vec<&Value>)> = Vec::new();
    for row in all.iter().filter(|r| {
        r["type"] != "named_current" && r["id"].as_str().is_some_and(|id| selected.contains(id))
    }) {
        let basin = row["basin"].as_str().ok_or("Missing eddy basin")?;
        if let Some((_, rows)) = basins.iter_mut().find(|(b, _)| *b == basin) {
            rows.push(row);
        } else {
            basins.push((basin, vec![row]));
        }
    }
    let mut gateways = Vec::new();
    for (basin, rows) in &basins {
        let features: Vec<_> = rows
            .iter()
            .flat_map(|r| r["map_features"].as_array().into_iter().flatten())
            .collect();
        let coordinate = features
            .iter()
            .find(|f| f["geometry"]["type"] == "Point")
            .map(|f| &f["geometry"]["coordinates"])
            .or_else(|| {
                features
                    .iter()
                    .find(|f| f["geometry"]["type"] == "Polygon")
                    .map(|f| &f["geometry"]["coordinates"][0][0])
            });
        let Some(coordinate) = coordinate else {
            continue;
        };
        let p = snap(coordinate)?;
        gateways.push(json!({"basin":basin,"ids":rows.iter().map(|r|&r["id"]).collect::<Vec<_>>(),"x":p[0]+12.*size,"y":p[1]+16.*size,
            "covered":rows.iter().any(|r|r["capabilities"][metric].as_u64().unwrap_or(0)>0),"updated":rows.iter().any(|r|r["id"].as_str().is_some_and(|id|changed.contains(id)))}));
    }
    let mut groups: Vec<(&str, Vec<Value>)> = Vec::new();
    for (i, row) in all
        .iter()
        .filter(|r| r["type"] == "named_current")
        .enumerate()
    {
        let id = row["id"].as_str().ok_or("Missing current ID")?;
        if !selected.contains(id) {
            continue;
        }
        let name = basin_group(row["basin"].as_str().ok_or("Missing current basin")?);
        let index = groups
            .iter()
            .position(|(n, _)| *n == name)
            .unwrap_or_else(|| {
                groups.push((name, Vec::new()));
                groups.len() - 1
            });
        let y = groups[index].1.len() * 38 + 24;
        groups[index].1.push(json!({"id":id,"number":i+1,"y":y,"track_d":format!("M16,{}H40L49,{y}H88",y+9),
            "covered":row["capabilities"][metric].as_u64().unwrap_or(0)>0,"updated":changed.contains(id)}));
    }
    let panels:Vec<_>=groups.iter().enumerate().map(|(i,(name,rows))|json!({"name":name,"color":colors[i%colors.len()],"height":rows.len()*38+18,"rows":rows})).collect();
    let eddy_groups:Vec<_>=basins.iter().map(|(basin,rows)|json!({"basin":basin,"ids":rows.iter().map(|r|&r["id"]).collect::<Vec<_>>(),
        "covered_count":rows.iter().filter(|r|r["capabilities"][metric].as_u64().unwrap_or(0)>0).count(),
        "updated":rows.iter().any(|r|r["id"].as_str().is_some_and(|id|changed.contains(id)))})).collect();
    Ok(
        json!({"size":size,"view_box":box_,"stations":stations,"routes":routes,"connections":connections,"eddy_gateways":gateways,"panels":panels,"eddy_groups":eddy_groups,
        "total_currents":number,"filtered_currents":filtered,"routed_currents":routed,"in_view":in_view,
        "scope":"Editorial schematic. Only source-described connections are drawn; crossings and regional gateways assert no physical junction or footprint."}),
    )
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn station_collision_and_seam_geometry() {
        let mut placed = Vec::new();
        let a = separate([800., 400.], &mut placed).unwrap();
        let b = separate([800., 400.], &mut placed).unwrap();
        assert!((a[0] - b[0]).hypot(a[1] - b[1]) >= 30.);
        assert_eq!(
            route(&[json!([179., 0.]), json!([-179., 0.])])
                .unwrap()
                .matches('M')
                .count(),
            2
        );
        assert!(snap(&json!([0., 91.])).is_err());
    }
}
