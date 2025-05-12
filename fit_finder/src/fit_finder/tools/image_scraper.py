from crewai.tools import BaseTool
from pydantic import BaseModel, Field
import asyncio
from playwright.async_api import async_playwright
import tempfile
import requests
import os
from typing import List

class ScraperInput(BaseModel):
    board_url: str = Field(..., description="Pinterest board URL to extract image URLs from")

class PinterestImageScraperTool(BaseTool):
    name = "PinterestImageScraperTool"
    description = "Scrapes image URLs from a Pinterest board"
    args_schema = ScraperInput

    def _run(self, board_url: str) -> List[str]:
        return asyncio.run(self._scrape_images(board_url))

    async def _scrape_images(self, board_url: str) -> List[str]:
        image_urls = []
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(board_url)
            await page.wait_for_timeout(5000)  # wait for JS to load

            images = await page.query_selector_all("img")
            for img in images:
                src = await img.get_attribute("src")
                if src and src.startswith("http"):
                    image_urls.append(src)

            await browser.close()

        return list(set(image_urls))[:10]  # Return top 10 unique image URLs