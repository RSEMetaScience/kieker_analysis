"""First and last activity date per agent, from the Workbench dates query."""
import pandas as pd

from kieker_analysis.stats.agent_cleanup import DROP, canonical_ids
from kieker_analysis.stats.pseudo import pseudonymise
from kieker_analysis.stats.util import short_name


def agent_dates(raw: pd.DataFrame) -> pd.DataFrame:
    """raw: the query output (user, earliestStart, latestEnd, activityCount).

    Returns agent (pseudonymised), start_date, end_date as YYYY-MM-DD.
    """
    dates_per_agent = pd.DataFrame({
        "agent": canonical_ids(raw["user"].map(short_name)),
        "start_date": pd.to_datetime(raw["earliestStart"], utc=True, format="ISO8601").dt.strftime("%Y-%m-%d"),
        "end_date": pd.to_datetime(raw["latestEnd"], utc=True, format="ISO8601").dt.strftime("%Y-%m-%d"),
    })
    dates_per_agent = dates_per_agent[~dates_per_agent["agent"].isin(DROP)]
    # merged accounts: widest range (ISO date strings sort correctly, so min/max work)
    dates_per_agent = dates_per_agent.groupby("agent", as_index=False).agg(
        start_date=("start_date", "min"), end_date=("end_date", "max"))
    return pseudonymise(dates_per_agent)