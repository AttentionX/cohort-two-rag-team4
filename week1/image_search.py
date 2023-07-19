import asyncio
from playwright.sync_api import sync_playwright
from playwright.async_api import async_playwright
from urllib.parse import quote_plus

from hints_image_captioning import run_on_cpu


def get_google_query(query):
    return quote_plus(query)


def get_webpage_image(page, link, query):
    url = link['href']
    page.goto(url, wait_until="domcontentloaded")
    try:
        selector = 'img[alt*={}], img[src*=http]'.format(query)
        element = page.wait_for_selector(selector, timeout=5000)
        return str(element.get_attribute("src"))
    except Exception as e:
        print("No image found {}".format(e))
        return None


async def playwright_init():
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch()
    context = await browser.new_context()
    page = await context.new_page()


def main(q: str = None):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        while True:
            query = q or input("Enter your query: ")
            google_query = get_google_query(query)
            captions = []

            # Could specify specific website for data source (Reddit, Wikipedia, etc)
            google_query_url = f"https://www.google.com/search?q={google_query}"
            page.goto(google_query_url)

            # page.type('input[name=q]', 'Your search query')
            # page.press('input[name=q]', 'Enter')

            page.wait_for_selector('.g')

            # Extract the top K links
            k = 10  # Choose the top K results
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
                image = get_webpage_image(page, link, query)
                if image and (image.startswith('https://') or image.startswith('http://')):
                    caption = run_on_cpu(image)
                    print('###### caption: {}'.format(caption))
                    captions.append(caption)

            # Answer question via retrieved chunks
            print("done. result images: {}".format(captions))
            break


if __name__ == "__main__":
    main()
