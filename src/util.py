import json
import sqlite3
from pathlib import Path
from urllib.parse import urlparse
from kieker_analysis.queries.queries import Query
from kieker_analysis.sparql.client import run_dataframe
from pandas import DataFrame

def list_events():
    """print a list of the events in the kieker data that change a PR or an issue

    """
    df = run_dataframe(Query.issues_events)

    df_piv = df.pivot_table(
        index="issue",
        columns="event_type",
        values="count",
        fill_value=0
    )
    df_piv.columns = df_piv.columns.map(get_event_name)

    print(f"there are 21 events that make changes to a recorded issue")
def repo_url_to_repo_id(repo_url: str) -> tuple[str, str, str]:
    """
    convert repo url to a named tuple:
        https://github.com/owner/name → (repo_id, owner, name)
    """
    parsed = urlparse(repo_url)
    parts = parsed.path.strip("/").split("/")
    if len(parts) < 2:
        raise ValueError(f"Invalid repo URL: {repo_url}")
    owner, name = parts[0], parts[1]
    return f"{owner}/{name}", owner, name


def parse_repo_url(url: str) -> tuple[str, str, str]:
    """
    Returns (repo_id, owner_login, name)
    """
    path = urlparse(url).path.strip("/")
    owner, name = path.split("/", 1)
    return f"{owner}/{name}", owner, name


def import_user_profiles(jsonl_path: Path) -> None:
    db_path = Path("../data/gh_metadata.sqlite")
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()

    with jsonl_path.open("r", encoding="utf-8") as f:
        for line in f:
            record = json.loads(line)
            data = record.get("data", None)
            if data is None:
                continue

            login = data["login"]

            #  insert user
            cur.execute(
                """
                INSERT OR IGNORE INTO gh_user (
                    login, type, name, bio, website_url,
                    created_at, contributed_repo_count
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    login,
                    data["__typename"],
                    data.get("name"),
                    data.get("bio"),
                    data.get("websiteUrl"),
                    data.get("createdAt"),
                    data["repositoriesContributedTo"]["totalCount"],
                ),
            )

            #  insert organizations + relations
            for org in data["organizations"]["nodes"]:
                org_login = org["login"]
                # orgs first...
                cur.execute(
                    """
                    INSERT OR IGNORE INTO orgs (login,  url)
                    VALUES (?, ? )
                    """,
                    (org_login, org.get("url")
                     ),
                )
                # then memberships
                cur.execute(
                    """
                    INSERT OR IGNORE INTO gh_user_org (user_login, org_login)
                    VALUES (?, ?)
                    """,
                    (login, org_login),
                )

            # get the contibutedto repos and split them up ito some useful values
            for repo in data["repositoriesContributedTo"]["nodes"]:
                repo_url = repo["url"]
                repo_id, owner_login, name = parse_repo_url(repo_url)

                # insert repo ...
                cur.execute(
                    """
                    INSERT OR IGNORE INTO repos (repo_id, owner_login, name, url)
                    VALUES (?, ?, ?, ?)
                    """,
                    (repo_id, owner_login, name, repo_url),
                )

                # ...then link user to repo
                cur.execute(
                    """
                    INSERT OR IGNORE INTO gh_user_repo (user_login, repo_id, relation)
                    VALUES (?, ?, 'contributed')
                    """,
                    (login, repo_id),
                )

    conn.commit()
    conn.close()

def get_event_name(url)->str:
    return url.strip("/").split("/")[-1]

