import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def node(source: str) -> str:
    return subprocess.run(["node", "-e", source], cwd=ROOT, check=True, capture_output=True, text=True).stdout.strip()


def test_state_handoff_contract_and_local_routes() -> None:
    result = node("global.window=global;require('./atlas/state-handoffs.js');process.stdout.write(JSON.stringify({gf:OSWStateHandoffs.cards('GFST'),sant:OSWStateHandoffs.cards('SANT'),na:OSWStateHandoffs.cards('NADR')}));")
    assert 'exchange/?province=SANT&depth=0-200m&month=201802' in result
    assert 'event/?scene=event' in result
    assert 'No bounded Drake native-grid temperature passport' in result


def test_handoff_shell_and_history_contract_are_present() -> None:
    html = (ROOT / "atlas" / "index.html").read_text(encoding="utf-8")
    app = (ROOT / "atlas" / "app.js").read_text(encoding="utf-8")
    assert 'id="state-handoff"' in html
    assert 'src="state-handoffs.js"' in html
    assert 'window.addEventListener("popstate"' in app
    assert 'updateAtlasUrl("push")' in app
    assert 'not a physical container' in app


def test_exchange_and_event_admission_lists_match_committed_interfaces() -> None:
    exchange = (ROOT / "exchange" / "hydrography.js").read_text(encoding="utf-8")
    exchange_codes = set(re.findall(r'"osw_code":"([^"]+)', exchange))
    lists = json.loads(node("global.window=global;require('./atlas/state-handoffs.js');require('./exchange/events.js');process.stdout.write(JSON.stringify({exchange:[...OSWStateHandoffs.exchangeCodes],event:[...OSWStateHandoffs.eventCodes],passports:OSW_EVENTS.state_passports.map(item=>item.province)}));"))
    assert set(lists["exchange"]) == exchange_codes
    assert set(lists["event"]) == set(lists["passports"])
