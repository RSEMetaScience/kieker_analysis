"""Replace agent ids with pseudonyms (user_1, user_2, ... user_n).

The agent -> pseudonym key lives in data/agent_pseudonyms.csv, which is gitignored.
It is the only way to get the real accounts back, so !!! back it up
outside the repo!!!. Existing agents keep their number on later runs; new agents are
appended.
"""
import random
from pathlib import Path

import pandas as pd

PSEUDONYM_FILE = Path(__file__).resolve().parents[3] / "data" / "agent_pseudonyms.csv"

# not people, so use real name.
KEEP_NAMES = {"github:dependabot", "github:kieker-ci"}


def _load(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    df = pd.read_csv(path)
    return dict(zip(df["agent"], df["pseudonym"]))


def _save(mapping: dict[str, str], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")  # write-then-rename so a crash can't corrupt the key
    pd.DataFrame({"agent": list(mapping), "pseudonym": list(mapping.values())}).to_csv(tmp, index=False)
    tmp.replace(path)


def pseudonymise(table: pd.DataFrame, path: Path = PSEUDONYM_FILE) -> pd.DataFrame:
    """Return a copy of `table` with its 'agent' column replaced by pseudonyms."""
    mapping = _load(path)
    new_agents = [a for a in table["agent"].unique() if a not in mapping and a not in KEEP_NAMES]
    if new_agents:
        # random order, so a number reveals nothing about the login (e.g. alphabetical position)
        random.SystemRandom().shuffle(new_agents)
        next_n = 1 + max((int(p.split("_")[1]) for p in mapping.values()), default=0)
        for offset, agent in enumerate(new_agents):
            mapping[agent] = f"user_{next_n + offset}"
        _save(mapping, path)
    out = table.copy()
    out["agent"] = out["agent"].map(lambda a: a if a in KEEP_NAMES else mapping[a])
    return out


def real_name(pseudonym: str, path: Path = PSEUDONYM_FILE) -> str:
    """Un-redact: the real agent id behind a pseudonym."""
    return {p: a for a, p in _load(path).items()}[pseudonym]


if __name__ == "__main__":
    import sys
    for p in sys.argv[1:]:
        print(p, "->", real_name(p))