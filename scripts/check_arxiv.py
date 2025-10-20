import arxiv
import os
import requests
from datetime import datetime, timedelta

# 검색할 키워드
SEARCH_QUERY = '"reinforcement learning"'
# 레포지토리 정보 (본인 깃허브에 맞게 수정)
REPO_OWNER = "nerdbamboo"
REPO_NAME = "rl-paper-collection"

# GITHUB_TOKEN (Actions에서 자동으로 주입됨)
TOKEN = os.environ.get('GH_TOKEN')

def create_github_issue(title, body):
    """깃허브 이슈를 생성하는 함수"""
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/issues"
    headers = {
        "Authorization": f"token {TOKEN}",
        "Accept": "application/vnd.github.v3+json",
    }
    data = {"title": title, "body": body, "labels": ["new-paper"]}
    
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 201:
        print(f"Successfully created issue: {title}")
    else:
        print(f"Failed to create issue: {response.status_code} - {response.text}")

def search_arxiv():
    """어제 하루 동안 arXiv에서 새 논문을 검색합니다."""
    
    # 어제 날짜 계산 (UTC 기준)
    yesterday = datetime.utcnow() - timedelta(days=1)
    yesterday_str = yesterday.strftime('%Y%m%d')
    
    # 쿼리: (cat:cs.LG OR cat:cs.AI) AND all:"reinforcement learning"
    # submittedDate를 사용해 날짜 범위를 지정 (더 정확함)
    query = f'({SEARCH_QUERY}) AND submittedDate:[{yesterday_str}000000 TO {yesterday_str}235959]'

    search = arxiv.Search(
        query=query,
        max_results=20, # 하루 20개면 충분
        sort_by=arxiv.SortCriterion.SubmittedDate,
        sort_order=arxiv.SortOrder.Descending
    )

    found_papers = 0
    for result in search.results():
        # 중복 이슈 방지 (간단하게 제목으로만 체크)
        if check_if_issue_exists(result.title):
            print(f"Issue already exists for: {result.title}")
            continue

        found_papers += 1
        print(f"Found new paper: {result.title}")
        
        # 이슈 제목
        issue_title = f"[New Paper] {result.title}"
        
        # 이슈 본문
        authors = ', '.join([author.name for author in result.authors])
        issue_body = f"**Title:** {result.title}\n"
        issue_body += f"**Authors:** {authors}\n\n"
        issue_body += f"**Abstract:**\n{result.summary}\n\n"
        issue_body += f"**arXiv Link:** {result.entry_id}\n"
        if result.pdf_url:
            issue_body += f"**PDF Link:** {result.pdf_url}\n"
        
        create_github_issue(issue_title, issue_body)

    if found_papers == 0:
        print("No new papers found yesterday.")

def check_if_issue_exists(title):
    """이미 해당 제목의 이슈가 있는지 확인하는 함수 (Rate Limit 때문에 간단히 구현)"""
    # 실제로는 GitHub API로 search-issue를 하는 것이 더 정확하지만,
    # 이 예제에서는 단순화를 위해 생략합니다. 
    # 대신, 스크립트가 하루에 한 번만 돌기 때문에 중복 가능성이 낮습니다.
    # 더 정교하게 만들려면 DB나 파일로 기존 목록을 관리해야 합니다.
    # 여기서는 간단히 'False'를 반환하여 모든 새 논문 이슈를 생성합니다.
    return False

if __name__ == "__main__":
    if not TOKEN:
        print("Error: GITHUB_TOKEN is not set.")
    else:
        search_arxiv()