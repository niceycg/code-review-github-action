# Automated Code Review using the ChatGPT language model

# Import statements
import argparse
import openai
import os
import requests
from github import Github

# Adding command-line arguments
parser = argparse.ArgumentParser()
parser.add_argument('--openai_api_key', help='OpenAI API Key')
parser.add_argument('--github_token', help='Github Token')
parser.add_argument('--github_pr_id', help='Github PR ID')
parser.add_argument('--openai_engine', default="gpt-3.5-turbo",
                    help='gtp-3.5-turbo or gpt-4')
parser.add_argument('--mode', default="files",
                    help='PR interpretation form. Options: files, patch')

args = parser.parse_args()

# Authenticating with the OpenAI API
openai.api_key = args.openai_api_key

# Authenticating with the Github API
g = Github(args.github_token)


def files():
    repo = g.get_repo(os.getenv('GITHUB_REPOSITORY'))
    pull_request = repo.get_pull(int(args.github_pr_id))

    # Loop through the commits in the pull request
    commits = pull_request.get_commits()
    for commit in commits:
        # Getting the modified files in the commit
        files = commit.files
        for file in files:
            # Getting the file name and content
            filename = file.filename
            content = repo.get_contents(
                filename, ref=commit.sha).decoded_content.decode('utf-8')

            message = []
            message.append({
                "role": "system",
                "content": "한글로 말할것. 코드리뷰해줘. 에러 또는 문제가 되는 부분을 찾아줘. 개선사항 찾아줘."
            })
            message.append({
                "role": "user",
                "content": content
            })

            # Sending the code to ChatGPT
            response = openai.ChatCompletion.create(
                model=args.openai_engine,
                messages=message,
                user="Pentacle_Code_Review"
            )

            # Adding a comment to the pull request with ChatGPT's response
            pull_request.create_issue_comment(
                f"Code Review file is ``{file.filename}``:\n {response.choices[0].message.content}")


def patch():
    repo = g.get_repo(os.getenv('GITHUB_REPOSITORY'))
    print(f"repo: {repo}")
    pull_request = repo.get_pull(int(args.github_pr_id))
    print(f"pull: {pull_request}")
    content = get_content_patch()

    print(f"content: {content}")

    if len(content) == 0:
        pull_request.create_issue_comment(
            f"Patch file does not contain any changes")
        return

    parsed_text = content.split("diff")

    for diff_text in parsed_text:
        if len(diff_text) == 0:
            continue

        try:
            file_name = diff_text.split("b/")[1].splitlines()[0]
            print(f"file_name: {file_name}")

            path, ext = os.path.splitext(file_name)
            print(f"file_extension: {ext}")

            if ext in ['.java', '.js', '.tsx', '.py']:
                message = []
                message.append({
                    "role": "system",
                    "content": "한글로 말할것. 코드리뷰해줘. 에러 또는 문제가 되는 부분을 찾아줘. 개선사항 찾아줘. Summarize what was done in this diff"
                })
                message.append({
                    "role": "user",
                    "content": diff_text
                })
                response = openai.ChatCompletion.create(
                    model=args.openai_engine,
                    messages=message,
                    user="Pentacle_Code_Review"
                )

                pull_request.create_issue_comment(
                    f"Code Review file ``{file_name}``:\n {response.choices[0].message.content}")

        except Exception as e:
            error_message = str(e)
            pull_request.create_issue_comment(
                f"Error file ``{file_name}``:\n {error_message}")


def get_content_patch():
    url = f"https://api.github.com/repos/{os.getenv('GITHUB_REPOSITORY')}/pulls/{args.github_pr_id}"
    print(f"url: {url}")

    headers = {
        'Authorization': f"token {args.github_token}",
        'Accept': 'application/vnd.github.v3.diff'
    }

    response = requests.request("GET", url, headers=headers)
    print(f"response: {response}")

    if response.status_code != 200:
        raise Exception(response.text)

    return response.text


if (args.mode == "files"):
    files()

if (args.mode == "patch"):
    patch()
