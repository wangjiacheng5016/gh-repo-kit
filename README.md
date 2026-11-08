# gh-repo-kit

[English](#english) | [中文说明](#中文说明)

<a id="english"></a>
Three small scripts for day-to-day GitHub repo management from the command
line, built on the GitHub REST API. They reuse the token your `git push`
already uses (via the git credential helper), so there is nothing to
configure and nothing hardcoded.

| Script | What it does |
|---|---|
| `gh_create.py` | Create a repo (public or private) and print the ready-to-paste `git remote add` line |
| `gh_list.py` | List your (or anyone's) repos with `private` flag and last-update date |
| `gh_verify.py` | After mirroring a project to GitHub, verify that the key files really exist in the **remote** tree |

## Token resolution

All scripts look for a token in this order:

1. `GH_TOKEN` environment variable
2. local git credential store (`git credential fill`) — filled automatically
   after your first `git push`

Public-data commands (`gh_list.py --user someone`) work without a token.

## Examples

```bash
# create a repo and push to it
python gh_create.py --name my-repo --description "One line about it"
git remote add origin git@github.com:you/my-repo.git && git push -u origin main

# audit an account
python gh_list.py
python gh_list.py --user octocat

# did the mirror actually include the entry points?
python gh_verify.py --repo you/my-repo -- README.md src/main.py pyproject.toml
python gh_verify.py --repo you/my-repo --files key_files.txt
```

`key_files.txt` is one path per line; `#` starts a comment:

```
# entry points and configs that must be on the remote
README.md
pyproject.toml
src/main.py
```

`gh_verify.py` exits with code `0` when everything is present, `2` when
something is missing — drop it into CI or a post-push hook.

## License

MIT — see [LICENSE](LICENSE).

---

<a id="中文说明"></a>
# 中文说明

三个基于 GitHub REST API 的命令行仓库管理小脚本，复用 `git push` 已保存的凭证（git credential helper），零配置、无硬编码。

- `gh_create.py`：创建公开/私有仓库，并输出可直接复制的 remote 添加命令
- `gh_list.py`：列出自己（或任意用户）的仓库、private 状态与最近更新时间
- `gh_verify.py`：项目镜像到 GitHub 后，校验关键文件（入口、配置、权重等）是否真的存在于**远端**仓库

凭证优先级：`GH_TOKEN` 环境变量 → git credential store。`gh_verify.py` 全部存在时退出码 0，缺失时为 2，可挂在 CI 或推送钩子里。

```bash
python gh_create.py --name my-repo --description "一句话简介"
python gh_verify.py --repo you/my-repo -- README.md src/main.py
```
