# Backup Github
Automatic backups for Github Repositories.

This script only clones repositories from the `GH_USER` account (with url:
https://github.com/`GH_USER`/<repo_name>).

It also has a special rule to filter some repositories.

# Setup
1. Generate a [Github Access
   Token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)
   with `repo` and `user` permissions.
2. Copy the access token to a file. (Example: `.token`)

# Usage
- Run `make all` target with the following optional variables:
    - GH_USER: string with Github user name
    - TOKEN: path to file with Github access token (`.token` by default)
    - CLONE_DIR: path to directory for all repository clones (`clone_dir` by
      default)
    - ARCHIVE_DIR: path to directory for all repository archives (`archive_dir`
      by default)

## Example
```Bash
make all TOKEN=.my_token GH_USER=John-Smith CLONE_DIR=clones ARCHIVE_DIR=archives
```
