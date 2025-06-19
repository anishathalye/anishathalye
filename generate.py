#!/usr/bin/env python3

import argparse
from datetime import UTC, datetime
from typing import Any

import yaml
from github import Github
from github.Repository import Repository

WATCH_FILE = "watch.yml"
LANGUAGE_FILE = "languages.yml"
OUTPUT_MD = "README.md"
OUTPUT_DATA = "data.yml"
OUTPUT_CI = "ci-status.md"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--default-user", type=str, required=True, help="Default username")
    parser.add_argument(
        "--token",
        type=str,
        help="GitHub personal access token (to avoid rate limiting)",
    )
    args = parser.parse_args()

    with open(LANGUAGE_FILE) as fin:
        languages = yaml.safe_load(fin)
    with open(WATCH_FILE) as fin:
        watch = yaml.safe_load(fin)

    g = Github(args.token)

    raw_data: dict[str, Any] = {"date": datetime.now(UTC).isoformat(), "user": {}, "repositories": {}}

    ci_data = []

    with open(OUTPUT_MD, "w") as fout:
        for section in watch:
            hidden = section["name"] == "Hidden"
            if not hidden:
                # header
                fout.write('<h3 align="center">{}</h3>\n\n'.format(section["name"]))
                # table header
                fout.write("| | | |\n")
                fout.write("|---|---|---|\n")
            for repo_name in section["repos"]:
                display_name = repo_name
                raw_display_name = repo_name
                if "/" not in repo_name:
                    repo_name = f"{args.default_user}/{repo_name}"
                repo = g.get_repo(repo_name)
                raw_data["repositories"][raw_display_name] = {
                    "stars": repo.stargazers_count,
                    "forks": repo.forks_count,
                    "watching": repo.subscribers_count,
                }

                badges = get_ci_badges(repo)
                if badges:
                    ci_data.append({"name": raw_display_name, "repo_name": repo_name, "badges": badges})
                if hidden:
                    continue
                # prevent breaking on '-' and '/'
                display_name = display_name.replace("-", "\u2060-\u2060")
                display_name = display_name.replace("/", "\u2060/\u2060")
                link = f"[**{display_name}**](https://github.com/{repo_name})"
                language_logo = f"![{repo.language}]({languages[repo.language]})" if repo.language else ""
                if repo.stargazers_count >= 1000:
                    stars = f"{round(repo.stargazers_count / 100) / 10:.1f}k"
                    if stars.endswith(".0k"):
                        stars = f"{stars[:-3]}k"
                else:
                    stars = f"{repo.stargazers_count:d}"
                fout.write(f"| {link} <br /> \u2605\u2060 \u2060{stars} | {language_logo} | {repo.description} |\n")
            if not hidden:
                fout.write("\n")
        user = g.get_user(args.default_user)
        raw_data["user"] = {
            "name": args.default_user,
            "followers": user.followers,
            "following": user.following,
            "repos": user.public_repos,
            "gists": user.public_gists,
        }
    with open(OUTPUT_DATA, "w") as fout:
        yaml.safe_dump(raw_data, fout, sort_keys=False)

    with open(OUTPUT_CI, "w") as fout:
        fout.write("# CI Status\n\n")
        fout.write("| Repository | CI Status |\n")
        fout.write("|---|---|\n")
        for project in ci_data:
            badges_str = " ".join(project["badges"])
            repo_link = f"[{project['name']}](https://github.com/{project['repo_name']})"
            fout.write(f"| {repo_link} | {badges_str} |\n")


def get_ci_badges(repo: Repository) -> list[str]:
    """Get CI status badges for a repository"""
    badges = []
    workflows = repo.get_workflows()
    for workflow in workflows:
        # Skip built-in GitHub workflows
        if workflow.path.startswith(".github/workflows/"):
            badge_url = (
                f"https://github.com/{repo.full_name}/actions/workflows/{workflow.path.split('/')[-1]}/badge.svg"
            )
            badges.append(f"![{workflow.name}]({badge_url})")
    return badges


if __name__ == "__main__":
    main()
