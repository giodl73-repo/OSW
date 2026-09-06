import importlib.util
import pathlib
import unittest


PATH = pathlib.Path(__file__).with_name("synthesize_oras5_drake_vertical.py")
SPEC = importlib.util.spec_from_file_location("synthesize_oras5_drake_vertical", PATH)
module = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(module)


def payload(scale=1):
    layers = []
    for positive, negative, temp_positive, temp_negative in ((2, -1, 6, -2), (3, -1, 9, -2)):
        layers.append({
            "thickness_m": 500, "positive_volume_Sv": positive * scale, "negative_volume_Sv": negative * scale,
            "positive_temperature_transport_degC_Sv": temp_positive * scale,
            "negative_temperature_transport_degC_Sv": temp_negative * scale,
        })
    rho, cp = 1000, 4000
    net_volume = sum(layer["positive_volume_Sv"] + layer["negative_volume_Sv"] for layer in layers)
    net_temp = sum(layer["positive_temperature_transport_degC_Sv"] + layer["negative_temperature_transport_degC_Sv"] for layer in layers)
    return {"layers": layers, "constants": {"density_kg_m3": rho, "heat_capacity_J_kg_K": cp}, "volume_transport": {"net_Sv": net_volume}, "reference_relative_heat_transport": [{"reference_temperature_degC": 0, "net_PW": net_temp * rho * cp * 1e-9}]}


class DrakeVerticalSynthesisTests(unittest.TestCase):
    def test_strata_conserve_section_totals(self):
        result = module.synthesize([payload(i) for i in (1, 2, 3, 4)])
        self.assertEqual(5, len(result["summary"]))
        for audit in result["conservation_audit"]:
            self.assertAlmostEqual(0, audit["volume_residual_Sv"])
            self.assertAlmostEqual(0, audit["heat_0C_residual_PW"])


if __name__ == "__main__":
    unittest.main()
