"""Identity clean-up applied to the per-agent activity table before it is saved.

These rules are keyed on real account names, so they live here rather than in
the notebook, which only sees the cleaned, later pseudonymised version
"""
import pandas as pd

# Variants of one account that should be a single agent.
RENAMES = {
    # urlencoded copy that came from a Jira JSON response
    "github:dependabot%5Bbot%5D": "github:dependabot",
}

# Individuals who we know use several identities
# canonical id -> every id that is folded into it
MERGES = {
    "github:tfrotscher": ["github:tfrotscher", "github:ShaggsOn"],
    "github:lbl": ["github:labl-ppi", "github:lbl-dev"],  # old notebook key had a trailing space
    "github:nexxTM": ["pars:mariuslowe", "github:nexxTM"],
    "github:msm-ppi": ["github:msm-ppi", "pars:importeduser11"],
}

# Excluded from the analysis: not a single individual.
DROP = [
    "http://soton.ac.uk/pars/agents/github-web-ui",  # GitHub web UI commits: many people - this is a software agent
    "github:github",                                  # same agent under its name in the old data
    "pars:unknown_user",
    "pars:anonymous",
    "pars:unknown",
]

_MERGE_MAP = {old: new for new, olds in MERGES.items() for old in olds}

def canonical_ids(agents: pd.Series) -> pd.Series:
    """Apply the rename and merge rules to a Series of agent ids."""
    return agents.replace(RENAMES).replace(_MERGE_MAP)

def clean_agents(table: pd.DataFrame) -> pd.DataFrame:
    """Rename variants, fold merged identities together, drop non-individuals.

    `table` has an 'agent' column plus numeric metric columns. Rows that end up
    with the same agent id are summed. Ids that aren't in the table are ignored,
    so this still works if upstream fixes have already merged some of them.
    """
    table_copy = table.copy()
    table_copy["agent"] = canonical_ids(table_copy["agent"])
    table_copy = table_copy[~table_copy["agent"].isin(DROP)]
    return table_copy.groupby("agent", as_index=False, sort=False).sum()