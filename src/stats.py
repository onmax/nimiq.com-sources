"""Computes stats from GitHub."""

import datetime
import os
import time

import requests

from util import OUTPUT_FOLDER, get_variable, set_contents

GITHUB_TOKEN = get_variable("GITHUB_TOKEN")

headers = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
}

WEEKS_COUNT = 4


params = {
    "per_page": 100,
}


def get(path: str) -> dict:
    """Make a GET request to the GitHub API."""
    res = requests.get(f"https://api.github.com{path}",
                       params=params, headers=headers, timeout=10)
    return res


def fetch_all(path: str) -> list:
    """Fetch all results of all pages from GitHub API."""
    results = []

    while path:
        response = get(path)
        results += response.json()
        path = response.links.get("next", {}).get("url")
        time.sleep(0.2)
    return results


def get_stat(url: str):
    """Make and check a request to the GitHub API."""
    request = get(url)
    res = request.json()
    if 200 < request.status_code >= 300:
        return None
    if request.status_code == 202:
        time.sleep(1)
        return get_stat(url)
    return res


def get_stats_from_repo(
        org: str, repo: str, weeks: int):
    """Get the number of commits and additions since a date."""
    # get the number of commits in the last weeks
    commit_activity = get_stat(f"/repos/{org}/{repo}/stats/commit_activity")
    repo_commits_count = sum(week['total'] for week in commit_activity[-weeks:]
                             ) if commit_activity else 0

    code_frequency = get_stat(f"/repos/{org}/{repo}/stats/code_frequency")
    repo_additions = sum(week[1] for week in code_frequency[-weeks:]
                         ) if code_frequency else 0
    # lines removed
    repo_deletions = sum(week[2] for week in code_frequency[-weeks:]
                         ) if code_frequency else 0

    print(f"Found {repo_commits_count} commits and {repo_additions} additions "
          f"for {org}/{repo}")
    return {
        "name": repo,
        "commits_count": repo_commits_count,
        "additions": repo_additions,
        "deletions": repo_deletions,
    }


def get_stats(org: str, weeks: int, start_date: datetime.datetime):
    """Get the number of commits of a user since a date."""
    print(f"Getting stats for {org}...")
    repos = fetch_all(f"/orgs/{org}/repos")
    initial_length = len(repos)

    # ignore repos that have not been updated in the COUNT_WEEKS
    repos = [repo for repo in repos if repo['pushed_at'] >
             start_date.isoformat()]

    print(
        f"Found {initial_length} repos, but "
        f"ignoring {initial_length - len(repos)} repos that have not been "
        f"pushed in the last {weeks} weeks")

    results = []
    for repo in repos:
        results.append(get_stats_from_repo(org, repo["name"], weeks))
    return results


start_date = datetime.datetime.now() - datetime.timedelta(weeks=WEEKS_COUNT)
repo_stats = get_stats("nimiq", WEEKS_COUNT, start_date)

commits_count = sum(stat["commits_count"] for stat in repo_stats)
additions_count = sum(stat['additions'] for stat in repo_stats)
deletions_count = sum(stat['deletions'] for stat in repo_stats)
end_date = datetime.datetime.now()

stats = {
    "end_date": end_date.isoformat(),
    "start_date": start_date.isoformat(),
    "commits": commits_count,
    "additions": additions_count,
    "deletions": deletions_count
}

filename_stats = os.path.join(f"{OUTPUT_FOLDER}/stats", "stats.json")
print(f"Saving {stats} in {filename_stats}")
set_contents(filename_stats, stats, remove_old=True)

filename_by_repo = os.path.join(f"{OUTPUT_FOLDER}/stats", "stats-by-repo.json")
print(f"Saving stats by repo in {filename_by_repo}")
repo_stats_json = {
    "end_date": end_date.isoformat(),
    "start_date": start_date.isoformat(),
    "repos": repo_stats
}
set_contents(filename_by_repo, repo_stats_json, remove_old=True)

print(f"Total commits in the last {WEEKS_COUNT} weeks: {commits_count}")
print(f"Total additions in the last {WEEKS_COUNT} weeks: {additions_count}")
