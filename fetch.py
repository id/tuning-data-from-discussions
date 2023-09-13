#!/usr/bin/env python3
# Usage: python3 fetch.py -t <github token> -r <repo>

import requests
import json
import os
import sys
import math
from optparse import OptionParser
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

user_agent = sys.argv[0].split('/')[-1]

def query(owner, repo):
    return """
query {
  repository(owner: "%s", name: "%s") {
    discussions(first: 100, orderBy: {field: CREATED_AT, direction: DESC}) {
      nodes {
        title
        bodyText
        answer {
          bodyText
        }
      }
    }
  }
}
    """ % (owner, repo)


def get_headers(token: str):
    return {'Accept': 'application/vnd.github+json',
            'Authorization': f'Bearer {token}',
            'X-GitHub-Api-Version': '2022-11-28',
            'User-Agent': f'{user_agent}'
            }

def get_session():
    session = requests.Session()

    retries = Retry(total=10,
                    backoff_factor=1,  # 1s
                    allowed_methods=None,
                    status_forcelist=[ 429, 500, 502, 503, 504 ])  # Retry on these status codes

    session.mount('https://', HTTPAdapter(max_retries=retries))

    return session

def fetch_discussions(token: str, repo: str):
    session = get_session()
    url = f'https://api.github.com/graphql'
    [repo_owner, repo_repo] = repo.split('/')
    r = session.post(url, headers=get_headers(token), json={'query': query(repo_owner, repo_repo)})
    if r.status_code == 200:
        resp = r.json()
        if not 'data' in resp:
            print(f'Failed to fetch check runs: {r.status_code}\n{r.json()}')
            sys.exit(1)
        return resp['data']['repository']['discussions']['nodes']
    else:
        print(f'Failed to fetch check runs: {r.status_code}\n{r.text}')
        sys.exit(1)

def main():
    parser = OptionParser()
    parser.add_option("-r", "--repo", dest="repo",
                      help="github repo")
    parser.add_option("-t", "--token", dest="gh_token",
                      help="github API token")
    (options, args) = parser.parse_args()

    # Get github token from env var if provided, else use the one from command line.
    # The token must be exported in the env from ${{ secrets.GITHUB_TOKEN }} in the workflow.
    token = os.environ['GITHUB_TOKEN'] if 'GITHUB_TOKEN' in os.environ else options.gh_token
    data = [d for d in fetch_discussions(token, options.repo) if d['answer']]
    print(json.dumps(data, indent=4))

if __name__ == '__main__':
    main()
