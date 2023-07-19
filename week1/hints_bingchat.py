import asyncio
from playwright.sync_api import sync_playwright
from playwright.async_api import async_playwright

def get_google_query(query):
    raise NotImplementedError

def get_webpage_text(page, link):
    page.goto(link)
    
    # Get webpage text
    raise NotImplementedError

async def playwright_init():
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch()
    context = await browser.new_context()
    page = await context.new_page()

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        while True:
            query = input("Enter your query: ")
            google_query = get_google_query(query)
            
            # Could specify specific website for data source (Reddit, Wikipedia, etc)
            google_query_url = f"https://www.google.com/search?q={google_query}"
            page.goto(google_query_url)
            
            # page.type('input[name=q]', 'Your search query')
            # page.press('input[name=q]', 'Enter')
            
            page.wait_for_selector('.g')
            
            # Extract the top K links
            k = 5  # Choose the top K results
            links = page.eval_on_selector_all('.g', '''(results, k) => {
                return Array.from(results).slice(0, k).map(result => {
                    const anchor = result.querySelector('a');
                    return {
                        title: anchor.textContent,
                        href: anchor.href
                    };
                });
            }''', k)
            
            for link in links:
                text = get_webpage_text(page, link)
                
                # Get chunks and save to vectorDB
                
            # Answer question via retrieved chunks
        
            

if __name__ == "__main__":
    main()
