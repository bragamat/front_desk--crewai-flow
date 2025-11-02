
from crewai_tools import GithubSearchTool

tool = GithubSearchTool(
	github_repo='https://github.com/example/repo',
	gh_token='your_github_personal_access_token',
	content_types=['code', 'issue'] # Options: code, repo, pr, issue
)
