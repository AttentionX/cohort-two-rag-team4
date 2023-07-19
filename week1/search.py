import asyncio
from playwright.sync_api import sync_playwright
from playwright.async_api import async_playwright

def get_webpage_text(page, link):
    page.goto(link)
    text = page.inner_text("body")
    return text

def get_webpage_data(page, link):
    page.goto(link)
    page.wait_for_load_state("domcontentloaded")
    
    # Extract the webpage text
    text = page.inner_text("body")
    
    # Extract image URLs
    img_urls = page.eval_on_selector_all('img', '''(images) => {
        return Array.from(images).map(image => image.src);
    }''')
    
    return text, img_urls

async def playwright_init():
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch()
    context = await browser.new_context()
    page = await context.new_page()

def search_for_text(google_query, k=5):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        # Could specify specific website for data source (Reddit, Wikipedia, etc)
        google_query_url = f"https://www.google.com/search?q={google_query}"
        page.goto(google_query_url)
        
        # page.type('input[name=q]', 'Your search query')
        # page.press('input[name=q]', 'Enter')
        
        page.wait_for_selector('.g')
        
        # Extract the top K links
        links = page.eval_on_selector_all('.g', '''(results, k) => {
            return Array.from(results).slice(0, k).map(result => {
                const anchor = result.querySelector('a');
                return {
                    title: anchor.textContent,
                    href: anchor.href
                };
            });
        }''', k)
        
        texts = []
        
        for link in links:
            link = link['href']
            text = get_webpage_text(page, str(link))
            texts.append((link, text))
            
        return texts

def search_for_data(google_query, k=5):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        # Could specify specific website for data source (Reddit, Wikipedia, etc)
        google_query_url = f"https://www.google.com/search?q={google_query}"
        page.goto(google_query_url)
        
        # page.type('input[name=q]', 'Your search query')
        # page.press('input[name=q]', 'Enter')
        
        page.wait_for_selector('.g')
        
        # Extract the top K links
        links = page.eval_on_selector_all('.g', '''(results, k) => {
            return Array.from(results).slice(0, k).map(result => {
                const anchor = result.querySelector('a');
                return {
                    title: anchor.textContent,
                    href: anchor.href
                };
            });
        }''', k)
        
        data = []
        
        for link in links:
            link = link['href']
            text, img_urls = get_webpage_data(page, link)
            data.append((link, text, img_urls))
            
        return data

if __name__ == "__main__":
    data = search_for_data('BLIP paper', k=2)
    for (link, text, image_urls) in data:
        print(link, text[:20], sep=' ')