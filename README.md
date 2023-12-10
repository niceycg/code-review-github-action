# OpenAI를 이용한 코드리뷰 
## GitAction 추가 
```yml
name: Code Review

on:
  pull_request:                       
    types: [opened]     # opened,synchronized 

jobs:
  hello_world_job: # Define the job
    runs-on: ubuntu-latest # Specify the runner to run the job on
    name: Code Review # Job name
    steps:
      - name: check code # Step name
        uses: mz-pentacle/code-review-github-action@1.4
        with:
          openai_api_key: ${{ secrets.openai_api_key }}
          github_token: ${{ secrets.GITHUB_TOKEN }}
          github_pr_id: ${{ github.event.number }}
          openai_engine: "gpt-4"
          mode: "patch"
```
### Actions secrets and variables
- openai_api_key 추가: open-ai API 키 추가

