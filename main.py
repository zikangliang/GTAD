import os
import time
from dotenv import load_dotenv
from src.scraper import GitHubScraper
from src.llm_client import LLMAnalyzer
from src.notifier import Notifier
from src.utils import setup_logger

logger = setup_logger()

def main():
    # Load environment variables
    load_dotenv()
    
    # Configuration
    # MVP: Top 5 projects
    TOP_N = 5 
    
    logger.info("Starting GitHub Trending AI Daily (GTAD)...")
    
    # Initialize components
    try:
        scraper = GitHubScraper()
        # Initialize LLM only if we have a key, else we might mock or skip
        llm_analyzer = None
        if os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY"):
            llm_analyzer = LLMAnalyzer()
        else:
            logger.warning("No valid AI API Key found (GEMINI_API_KEY or OPENAI_API_KEY). AI analysis will be skipped.")
            
        notifier = Notifier()
    except Exception as e:
        logger.error(f"Initialization failed: {e}")
        return

    # 1. Fetch Trending Data
    logger.info("Fetching trending repositories...")
    repos = scraper.get_trending_repos(limit=TOP_N * 2) # Fetch more to allow filtering
    
    # Filter
    filtered_repos = scraper.filter_repos(repos)
    # Take top N after filtering
    target_repos = filtered_repos[:TOP_N]
    
    logger.info(f"Found {len(target_repos)} potential projects to analyze.")
    
    final_projects = []
    
    # 2. Analyze each project
    for repo in target_repos:
        repo_name = repo["name"]
        owner = repo["owner"]["login"]
        full_name = repo["full_name"]
        
        logger.info(f"Analyzing {full_name}...")
        
        # Basic info
        project_data = {
            "name": full_name,
            "url": repo["html_url"],
            "stars": repo["stargazers_count"],
            # Approximation for "stars today" since we don't have historical data DB yet
            # For "search created:>2days", stars are mostly new. 
            # Ideally we'd need a persistence layer to track delta, or scrape the trending page.
            # For now, we'll label it "Total Stars" in the UI effectively.
            "stars_today": "N/A", 
            "language": repo["language"] or "Unknown",
            "analysis": None
        }
        
        # Get README
        readme_content = scraper.get_readme_content(owner, repo_name)
        
        if llm_analyzer and readme_content:
            # AI Analysis
            try:
                analysis_result = llm_analyzer.analyze_readme(readme_content)
                project_data["analysis"] = analysis_result
                # Rate limit protection (simple sleep)
                time.sleep(2) 
            except Exception as e:
                logger.error(f"Failed to analyze {full_name}: {e}")
                project_data["analysis"] = {
                    "one_sentence_summary": "分析失败",
                    "core_features": [],
                    "tech_stack": [],
                    "use_case": "暂无",
                    "score": 0
                }
        else:
            # Fallback if no AI or no README
            project_data["analysis"] = {
                "one_sentence_summary": "暂无 AI 分析 (Missing Key or README)",
                "core_features": [],
                "tech_stack": [],
                "use_case": "暂无",
                "score": 0
            }
            
        final_projects.append(project_data)

    if not final_projects:
        logger.warning("No projects found or analyzed.")
        return

    # 3. Generate Report
    logger.info("Generating HTML report...")
    html_content = notifier.render_report(final_projects)
    
    # 4. Send Email
    logger.info("Sending email...")
    notifier.send_email(html_content)
    
    logger.info("Job completed successfully.")

if __name__ == "__main__":
    main()
