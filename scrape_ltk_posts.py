import asyncio
from playwright.async_api import async_playwright

async def scrape_ltk_post_urls(keyword="gold hoops"):
    search_url = f"https://www.shopltk.com/search?keyword={keyword.replace(' ', '%20')}&type=post"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto(search_url)

        # Scroll to load more results
        for _ in range(3):
            await page.mouse.wheel(0, 3000)
            await asyncio.sleep(2)

        # Extract post URLs
        post_links = await page.locator('a[href*="/explore/"]').all()
        unique_urls = set()

        for link in post_links:
            href = await link.get_attribute("href")
            if href and "/posts/" in href:
                full_url = f"https://www.shopltk.com{href}"
                unique_urls.add(full_url)

        print(f"Found {len(unique_urls)} unique post URLs\n")

        for i, post_url in enumerate(list(unique_urls)[:5]):  # Limit for testing
            post_page = await browser.new_page()
            try:
                await post_page.goto(post_url)
                await asyncio.sleep(3)

                # Try to extract the main image alt text
                try:
                    alt_text = await post_page.locator("img.c-image").first.get_attribute("alt")
                except:
                    alt_text = "[No image alt found]"

                creator = post_url.split("/explore/")[1].split("/")[0]

                print(f"\nPost {i+1} by @{creator}")
                print(f"    Description: {alt_text}")
                print(f"    URL: {post_url}")

                # Grab product links
                product_links = await post_page.locator('a[href*="rstyle.me"]').all()
                if not product_links:
                    print("No product links found.")
                else:
                    for link in product_links:
                        href = await link.get_attribute("href")
                        print(f"    Product URL: {href}")

            except Exception as e:
                print(f"Failed to load post {i+1}: {e}")
            finally:
                await post_page.close()

        await browser.close()

asyncio.run(scrape_ltk_post_urls("gold hoops"))