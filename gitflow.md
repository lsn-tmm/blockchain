# Simple Git Workflow

### A basic basic branching workflow for continuous delivery

Try to follow this model:

[https://www.atlassian.com/blog/git/simple-git-workflow-is-simple](https://www.atlassian.com/blog/git/simple-git-workflow-is-simple)

> For a complete description of most popular git workflows with advantages and disadvantages:
>
> [https://docs.gitlab.com/ee/topics/gitlab_flow.html](https://docs.gitlab.com/ee/topics/gitlab_flow.html)

### Initial git setup

Configuration of identity, inside the repo:

```
git config user.name <e.g. name surname>
git config user.email <your-github@mail.com>
git config user.username <your-github-username>
```
> If you want to setup a config globally, and not only for a local repo, add `--global` flag

#### shell tools

Maybe can be useful, for bash shell:

[https://github.com/magicmonty/bash-git-prompt](https://github.com/magicmonty/bash-git-prompt)

instead, if you're using zsh shell, choose your favorite [oh-my-zsh](https://github.com/ohmyzsh/ohmyzsh) theme + plugin

#### aliases

With `git config` you can setup aliases as you want, below a useful alias to view commit history as a clear graph:

```
git config alias.l 'log --oneline --graph --color --abbrev-commit --all --decorate'
```
