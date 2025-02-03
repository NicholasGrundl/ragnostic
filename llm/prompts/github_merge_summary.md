# Generate a branch commit history

Use are some bash scripts to create a formatted history to summarize for the merge PR

1. Simple with logs only

```bash
git log origin/main.. --pretty=format:"%an, %ad : %s" --date=short --reverse > branch_summary.txt
```

2. Detailed with log and files changed
```bash
git log main.. --pretty=format:"%h - %an, %ar : %s" --stat > branch_changes.txt
```


# Prompt

Below is the <git_history> of my current branch that i am making a pull request for.

Please help me summarize this for the PR merge message

<git_history>

[history goes here]

</git_history>