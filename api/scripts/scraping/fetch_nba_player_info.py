import string, asyncio
from playwright.async_api import async_playwright

async def launch_browser(headless=True):
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=headless)
    return playwright, browser


async def fetch_nba_player_info(browser):
    page = await browser.new_page()
    players = []

    try:
        for letter in string.ascii_lowercase:
            if letter != 'x':
                url = f"https://www.basketball-reference.com/players/{letter}/"
                await page.goto(url, wait_until='domcontentloaded', timeout=60000)
                await page.wait_for_selector("table#players tbody tr", timeout=10000)

                rows_data = await page.evaluate('''() => {
                    const rows = Array.from(document.querySelectorAll("table#players tbody tr"))
                        .filter(row => !row.classList.contains("thead"));

                    return rows.map(row => {
                        const playerCell = row.querySelector('th[data-stat="player"] a');
                        const yearMin = row.querySelector('td[data-stat="year_min"]')?.innerText.trim() || null;
                        const yearMax = row.querySelector('td[data-stat="year_max"]')?.innerText.trim() || null;
                        const position = row.querySelector('td[data-stat="pos"]')?.innerText.trim() || null;
                        const height = row.querySelector('td[data-stat="height"]')?.innerText.trim() || null;
                        const colleges = Array.from(row.querySelectorAll('td[data-stat="colleges"] a'))
                            .map(a => a.innerText.trim());

                        return {
                            name: playerCell ? playerCell.innerText.trim() : null,
                            link: playerCell ? playerCell.getAttribute("href") : null,
                            yearMin,
                            yearMax,
                            position,
                            height,
                            colleges
                        };
                    });
                }''')

                for data in rows_data:
                    players.append((
                        data["name"],
                        data["link"],
                        data["yearMin"],
                        data["yearMax"],
                        data["position"],
                        data["height"],
                        data["colleges"]
                    ))

    except Exception as e:
        print(f"⚠️ Error scraping Basketball Reference {letter}: {e}")
    finally:
        await page.close()

    return players

async def main():
    playwright, browser = await launch_browser(headless=True)
    await fetch_nba_player_info(browser)
    
    await browser.close()
    await playwright.stop()

asyncio.run(main())