#!/usr/bin/env python3
# Python script to backup user repositories from Github

import argparse
import json
import re
import requests
import subprocess

def parse_arguments():
    parser = argparse.ArgumentParser(
        prog="backup-github", description="Clone and archive github repositories"
    )
    parser.add_argument(
        "token_file",
        type=str,
        help="Path to file containing github access token with repository permissions",
    )
    parser.add_argument("gh_user", type=str, help="Github account user name")
    parser.add_argument(
        "clone_dir",
        nargs="?",
        default="clone_dir",
        type=str,
        help="Path to clone directory (optional)",
    )
    parser.add_argument(
        "archive_dir",
        nargs="?",
        default="archive_dir",
        type=str,
        help="Path to archive directory (optional)",
    )

    return parser.parse_args()


def get_gh_token(token_file):
    with open(token_file, "r") as token_file:
        return token_file.readline().rstrip("\n")


def get_repos_from_api(repo_list, api_response):
    repos = api_response.json()
    if repos == []:
        return False

    for repo in repos:
        tmp_dict = {}
        tmp_dict["name"] = repo["name"]
        tmp_dict["html_url"] = repo["html_url"]
        tmp_dict["private"] = repo["private"]
        repo_list.append(tmp_dict)

    return True


def get_all_repos_from_user(user, token):

    # try to get max number of pages
    # check: https://docs.github.com/en/rest/repos/repos?apiVersion=2022-11-28
    # /user/repos endpoint
    user_repos_endpoint = f"https://api.github.com/user/repos"
    params = {"per_page": 100, "page": 1}

    repos = []
    get_next_page = True
    # get all other repo pages
    while get_next_page == True:
        get_next_page = get_repos_from_api(
            repos, requests.get(user_repos_endpoint, auth=(user, token), params=params)
        )
        # next iteration: get next page
        params["page"] = params["page"] + 1

    return repos


def filter_repos(all_repos, user_name):
    user_repos = []
    # get repos only from user_name account
    for repo in all_repos:
        if user_name in repo["html_url"]:
            user_repos.append(repo)
    return user_repos


def special_repo_filter(user_repos):
    pattern = re.compile("^iob-[.]?")
    filtered_repos = []
    # remove private repositories with name starting with "iob-[NAME]"
    for repo in user_repos:
        if not pattern.match(repo["name"]) or repo["private"] is False:
            filtered_repos.append(repo)
    return filtered_repos


def create_dir(new_dir):
    subprocess.run(["mkdir", "-p", new_dir])


def clone_single_repo(gh_token, repo, clone_dir):
    clone_url = f'https://{gh_token}@{repo["html_url"].replace("https://","")}'
    clone_dir = f'{clone_dir}/{repo["name"]}'
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

    for src_dir in source_dirs:
        if src_dir:
            print(f"Archiving {src_dir}")
            dst_name = f"{archive_dir}/{src_dir.split('/')[-1]}.tar.gz"
            subprocess.run(["tar", "-zcf", dst_name, src_dir])


if __name__ == "__main__":
    print("Backup Github Repositories")

    args = parse_arguments()

    gh_token = get_gh_token(args.token_file)
    user_repos = get_all_repos_from_user(args.gh_user, gh_token)

    user_repos = filter_repos(user_repos, args.gh_user)
    filtered_repos = special_repo_filter(user_repos)

    clone_all_repos(gh_token, filtered_repos, args.clone_dir)

    archive_all_repos(args.clone_dir, args.archive_dir)

    print("Backup complete")
    print(f"Check {args.clone_dir} for repository clones.")
    print(f"Check {args.archive_dir} for repository archives.")
