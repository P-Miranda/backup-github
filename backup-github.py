#!/usr/bin/env python3
# Python script to backup user repositories from Github

import sys
import re
import subprocess
from github import Github


def usage():
    print("Usage: [VENV] backup-github.py [TOKEN] [GH_USER] (CLONE) (ARCHIVE)")
    print("   [VENV]: path to virtual environment python interpreter")
    print("   [TOKEN]: path to file containing github access token")
    print("   [GH_USER]: Github account user name")
    print("   (CLONE): path to clone directory (optional)")
    print("   (ARCHIVE): path to archive directory (optional)")


def get_gh_token(token_file):
    with open(token_file, "r") as token_file:
        return token_file.readline().rstrip("\n")


def filter_repos(all_repos, user_name):
    user_repos = []
    # get repos only from user_name account
    for repo in all_repos:
        if user_name in repo.git_url:
            user_repos.append(repo)
    return user_repos


def special_repo_filter(user_repos):
    pattern = re.compile("^iob-[.]?")
    filtered_repos = []
    # remove private repositories with name starting with "iob-[NAME]"
    for repo in user_repos:
        if not pattern.match(repo.name) or repo.private is False:
            filtered_repos.append(repo)
    return filtered_repos


def create_dir(new_dir):
    subprocess.run(["mkdir", "-p", new_dir])


def clone_single_repo(gh_token, repo, clone_dir):
    clone_url = f"https://{gh_token}@{repo.git_url.replace('git://','')}"
    clone_dir = f"{clone_dir}/{repo.name}"
    subprocess.run(["git", "clone", clone_url, clone_dir])


def clone_all_repos(gh_token, gh_repos, clone_dir):
    create_dir(clone_dir)
    for repo in gh_repos:
        clone_single_repo(gh_token, repo, clone_dir)


def archive_all_repos(clone_dir, archive_dir):
    create_dir(archive_dir)

    find_proc = subprocess.check_output(
        ["find", clone_dir, "-maxdepth", "1", "-mindepth", "1", "-type", "d"]
    )
    source_dirs = find_proc.decode("utf-8").split("\n")
    print(source_dirs)

    for src_dir in source_dirs:
        if src_dir:
            dst_name = f"{archive_dir}/{src_dir.split('/')[-1]}.tar.gz"
            subprocess.run(["tar", "-zcvf", dst_name, src_dir])


if __name__ == "__main__":
    print("Backup Github Repositories")
    if len(sys.argv) < 3:
        usage()
        sys.exit()

    token_file = sys.argv[1]
    user_name = sys.argv[2]
    if len(sys.argv) > 4:
        clone_dir = sys.argv[3]
        archive_dir = sys.argv[4]
    else:
        clone_dir = "clone_dir"
        archive_dir = "archive_dir"

    gh_token = get_gh_token(token_file)

    gh = Github(gh_token)
    user_repos = gh.get_user().get_repos()

    user_repos = filter_repos(user_repos, user_name)
    filtered_repos = special_repo_filter(user_repos)

    clone_all_repos(gh_token, filtered_repos, clone_dir)

    archive_all_repos(clone_dir, archive_dir)

    print("Backup complete")
    print(f"Check {clone_dir} for repository clones.")
    print(f"Check {archive_dir} for repository archives.")
