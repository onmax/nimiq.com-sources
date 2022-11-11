"""Computes stats from GitHub."""

import datetime
import os
from multiprocessing import Pool

import requests

from util import OUTPUT_FOLDER, get_variable, set_contents

GITHUB_TOKEN = get_variable("GITHUB_TOKEN")

headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
}

# The statitistics will be computed for the last SINCE_DAYS days
SINCE_DAYS = 30


def get_date_ago(days: int) -> datetime.datetime:
    """Get the date one month ago."""
    return datetime.datetime.now() - datetime.timedelta(days=days)


def get_additions(org: str, repo_name: str, sha: str) -> int:
    """Get the number of additions in the given list of commits."""
    url = f"https://api.github.com/repos/{org}/{repo_name}/commits/{sha}"
    response = requests.get(url, headers=headers, timeout=10)
    res = response.json()
    return res["stats"]["additions"]


def get_stats_from_repo_since(
        org: str, repo_name: str, since: datetime.datetime) -> dict:
    """Get the number of commits and additions since a date."""
    # get all repos
    print(f"Getting stats for {repo_name}")
    url = f"https://api.github.com/repos/{org}/{repo_name}/commits"
    params = {
        "per_page": 100,
    }
    response = requests.get(url, params=params, headers=headers, timeout=10)
    res = response.json()

    commits_since = 0  # total number of commits
    additions_since = 0  # total additions
    for commit in res:
        # commits
        commit_date = datetime.datetime.strptime(
            commit["commit"]["author"]["date"], "%Y-%m-%dT%H:%M:%SZ")
        if commit_date > since:
            commits_since += 1

            # additions
            additions_since += get_additions(org, repo_name, commit["sha"])

    return {
        "name": repo_name,
        "commits": commits_since,
        "additions": additions_since,
    }


def get_stats(org: str, since: datetime.datetime) -> int:
    """Get the number of commits of a user since a date."""
    # get all repos
    url = f"https://api.github.com/orgs/{org}/repos"
    params = {
        "per_page": 100,
    }
    response = requests.get(url, params=params, headers=headers, timeout=10)
    repos = response.json()
    print(f"Found {len(repos)} repos for {org}")

    results = []
    with Pool(len(repos)) as pool:
        results = pool.starmap(
            get_stats_from_repo_since,
            [(org, repo["name"], since) for repo in repos],
        )

    return results


repo_stats = get_stats("nimiq", get_date_ago(30))
commits_count = sum(stat['commits'] for stat in repo_stats)
additions_count = sum(stat['additions'] for stat in repo_stats)

stats = {
    "commits_last_month": commits_count,
    "additions_last_month": additions_count
}

filename_stats = os.path.join(f"{OUTPUT_FOLDER}/stats", "stats.json")
print(f"Saving {stats} in {filename_stats}")
set_contents(filename_stats, stats, remove_old=True)

filename_by_repo = os.path.join(f"{OUTPUT_FOLDER}/stats", "stats-by-repo.json")
print(f"Saving stats by repo in {filename_by_repo}")
set_contents(filename_by_repo, repo_stats, remove_old=True)

print(repo_stats)
print(f"Total commits in the last {SINCE_DAYS} days: {commits_count}")
print(f"Total additions in the last {SINCE_DAYS} days: {additions_count}")
