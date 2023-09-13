# Fetch Q&A from github discussions for a given repo

Fetches Q&A from github discussions via GraphQL API and outputs a JSON file to stdout.
Only takes the latest 100 questions with chosen answers.

## Usage

```bash
python3 fetch.py --repo emqx/emqx --token <github_token> > data.json
```

You can then feed it to ChatGPT to generate prompt/completion pairs.
