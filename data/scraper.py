import asyncio
import json
import os
import datetime
from crawl4ai import AsyncWebCrawler

# Comprehensive List of URLs to Scrape
URLS_TO_SCRAPE = [
    # 1) Academic Catalog – Regulations
    {"url": "https://catalog.olemiss.edu/academics/regulations/complete", "type": "regulation"},
    {"url": "https://catalog.olemiss.edu/academics/regulations/class-registration", "type": "regulation"},
    {"url": "https://catalog.olemiss.edu/academics/regulations/credit", "type": "regulation"},
    {"url": "https://catalog.olemiss.edu/academics/regulations/degree-requirements", "type": "regulation"},
    {"url": "https://catalog.olemiss.edu/academics/regulations/general-education", "type": "regulation"},
    {"url": "https://catalog.olemiss.edu/academics/regulations/academic-forgiveness", "type": "regulation"}, # Added based on research

    # 2) Academic Catalog – CS program + courses
    {"url": "https://catalog.olemiss.edu/engineering/computer-science", "type": "program"},
    {"url": "https://catalog.olemiss.edu/engineering/computer-science/bs-comp-sci", "type": "program"},
    {"url": "https://catalog.olemiss.edu/engineering/computer-science/bs-comp-sci/requirements", "type": "program"},
    {"url": "https://catalog.olemiss.edu/engineering/computer-science/courses", "type": "course_list"},
    {"url": "https://catalog.olemiss.edu/engineering/computer-science/bs-comp-sci/degree-audit", "type": "program"},

    # 3) Catalog – Electives & Minors
    {"url": "https://catalog.olemiss.edu/courses", "type": "course_index"},
    {"url": "https://catalog.olemiss.edu/engineering/computer-science/minor-comp-sci", "type": "program"}, # Added Minor

    # 4) School of Engineering gen-ed rules
    {"url": "https://catalog.olemiss.edu/engineering/academics", "type": "regulation"},

    # 5) Registrar – Registration & Calendars
    {"url": "https://olemiss.edu/registrar/registration/", "type": "calendar"},
    {"url": "https://olemiss.edu/departments/provost/registrar/calendars/index.php", "type": "calendar"},
    {"url": "https://olemiss.edu/registrar/transfer-equivalencies/", "type": "regulation"}, # Added Transfer

    # 6) CS Department (Forms & Plans)
    {"url": "https://cs.olemiss.edu/forms/", "type": "form"},
    # Note: PDF links like the 4-year plan need a different handling strategy (downloading), 
    # but crawl4ai might extract text if they are simple. For now we scrape the landing page.

    # 7) IT & Other
    {"url": "https://olemiss.edu/depts/it/servicesr1.html", "type": "guide"},
    {"url": "https://www.honors.olemiss.edu/admissions/requirements/", "type": "program"}, # Added Honors
]

OUTPUT_DIR = "data"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "olemiss_data.jsonl")

def extract_course_metadata(text, url):
    """
    Simple heuristic to extract course metadata if this is a course page.
    In a real production system, this would be a more robust regex or LLM parser.
    """
    metadata = {}
    if "courses" in url:
        # Placeholder for logic to extract Course Code, Credits, etc.
        # For now, we rely on the LLM to parse the 'text_clean' later.
        metadata["is_course_page"] = True
    return metadata

async def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"Starting scrape of {len(URLS_TO_SCRAPE)} pages...")
    
    async with AsyncWebCrawler(verbose=True) as crawler:
        # Extract just the URLs for the crawler
        urls = [item["url"] for item in URLS_TO_SCRAPE]
        results = await crawler.arun_many(urls)
        
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            for i, result in enumerate(results):
                original_item = URLS_TO_SCRAPE[i]
                
                if result.success:
                    print(f"Successfully scraped: {result.url}")
                    
                    # 1. Basic Metadata
                    record = {
                        "url": result.url,
                        "title": "Ole Miss Academic Data", # Ideally extract from HTML title
                        "page_type": original_item["type"],
                        "fetched_at": datetime.datetime.now().isoformat(),
                        "catalog_year": "2024-2025", # Default assumption, or extract from text
                        
                        # 2. Content
                        "text_clean": result.markdown, # Markdown is best for RAG
                        "html_raw": result.html,       # Keep raw just in case
                        
                        # 3. Links (Graph Building)
                        "links_out": [link['href'] for link in result.links.get('internal', [])],
                        
                        # 4. Course Specifics (Placeholder)
                        "course_metadata": extract_course_metadata(result.markdown, result.url)
                    }
                    
                    f.write(json.dumps(record, ensure_ascii=False) + "\n")
                else:
                    print(f"Failed to scrape: {result.url} - Error: {result.error_message}")

    print(f"Scraping complete! Data saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    asyncio.run(main())
