# TERNEXAR Debug Log

## Known Past Error

### GitHub repository not found

Command:

```bash
git push -u origin main --tags
```

Error:

```text
ERROR: Repository not found.
fatal: Could not read from remote repository.
```

Possible causes:
- GitHub repo did not exist yet
- Remote URL was wrong
- SSH key was not connected to GitHub
- GitHub account had no permission
- Username or repository name was misspelled

Safe checks:

```bash
git status
git remote -v
ssh -T git@github.com
```

Rule:
Never force push unless the user clearly confirms it.
