from datetime import datetime

import asyncio
import string
import re
import traceback
import random

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/115.0.0.0 Safari/537.36"
)

async def safe_goto(page, url, max_retries=3):
    for attempt in range(max_retries):
        try:
            await page.goto(url, wait_until='domcontentloaded', timeout=40000)
            return
        except Exception as e:
            print(f"⚠️ Navigation failed (attempt {attempt+1}) for {url}: {e}")
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(5 + random.random()*5)

async def scrape_player(browser, data, delay_range=(2,5)):
    player_url = f"https://www.basketball-reference.com{data['link']}"
    page = await browser.new_page()
    try:
        await page.set_extra_http_headers({"User-Agent": USER_AGENT})
        await safe_goto(page, player_url)

        try:
            await page.click("#meta_more_button", timeout=3000)
            await page.wait_for_selector("div#info p", timeout=5000)
        except:
            pass

        info_paragraphs = await page.evaluate('''() => {
            const infoDiv = document.querySelector("div#info");
            if (!infoDiv) return [];
            return Array.from(infoDiv.querySelectorAll("p"))
                .map(p => p.innerText.trim())
                .filter(Boolean);
        }''')
        
        teams_data = await page.evaluate('''() => {
            const uniDiv = document.querySelector("div.uni_holder");
            if (!uniDiv) return [];
            return Array.from(uniDiv.querySelectorAll("a"))
                .map(a => a.getAttribute("data-tip"))
                .filter(Boolean);
        }''')

        team_names = []
        for tip in teams_data:
            parts = tip.split(",", 1)
            if parts:
                team_names.append(parts[0].strip())
        
        accolades = await page.evaluate('''() => {
            const blingList = document.querySelector("ul#bling");
            if (!blingList) return [];
            return Array.from(blingList.querySelectorAll("li"))
                .map(li => li.getAttribute("data-tip"))
                .filter(Boolean);
        }''')

        years_pro = draft_round = draft_pick = draft_year = high_schools = None
        is_active = False

        for p_text in info_paragraphs:
            text_lower = p_text.lower()
            
            if "experience" in text_lower or "career length" in text_lower:
                exp_match = re.search(r'(\d+)', p_text)
                if exp_match:
                    years_pro = int(exp_match.group(1))

            if "draft" in text_lower:
                round_match = re.search(r'(?:Round\s+(\d+)|(\d+)(?:st|nd|rd|th)\s+round)', p_text, re.IGNORECASE)
                pick_match = re.search(r'(?:Pick\s+(\d+)|(\d+)(?:st|nd|rd|th)\s+pick)', p_text, re.IGNORECASE)
                year_match = re.search(r'(\d{4})', p_text)

                if round_match:
                    draft_round = int(next(g for g in round_match.groups() if g))
                if pick_match:
                    draft_pick = int(next(g for g in pick_match.groups() if g))
                if year_match:
                    draft_year = int(year_match.group(1))
            
            if text_lower.startswith("high school:") or text_lower.startswith("high schools:"):
                if text_lower.startswith("high school:"):
                    hs_part = p_text[len("High School:"):].strip()
                else:
                    hs_part = p_text[len("High Schools:"):].strip()

                matches = re.findall(r'([^,]+?)\s+in\s+[^,]+(?:,\s*[^,]+)?', hs_part)
                high_schools = [m.strip() for m in matches if m.strip()]
        
        if (data["yearMax"] == datetime.now().year):
            is_active = True
        
        print((
            data["name"], player_url, data["yearMin"], data["yearMax"],
            data["position"], data["height"], data["weight"], team_names, draft_round, draft_pick,
            draft_year, years_pro, accolades, data["colleges"], high_schools, is_active
        ))
        return (
            data["name"], player_url, data["yearMin"], data["yearMax"],
            data["position"], data["height"], data["weight"], team_names, draft_round, draft_pick,
            draft_year, years_pro, accolades, data["colleges"], high_schools, is_active
        )

    except Exception:
        print(f"⚠️ Error fetching {player_url}:\n{traceback.format_exc()}")
        return (
            data["name"], player_url, data["yearMin"], data["yearMax"],
            data["position"], data["height"], data["weight"], team_names, None, None,
            None, years_pro, accolades, data["colleges"], None, is_active
        )
    finally:
        await page.close()
        await asyncio.sleep(random.uniform(*delay_range))  # polite delay between player requests

async def fetch_nba_players(browser, batch_size=3, letter_delay_range=(5,10)):
    players = []
    page = await browser.new_page()
    await page.set_extra_http_headers({"User-Agent": USER_AGENT})

    for letter in string.ascii_lowercase:
        if letter == 'x':
            continue

        url = f"https://www.basketball-reference.com/players/{letter}/"
        try:
            await safe_goto(page, url)
            await page.wait_for_selector("table#players tbody tr", timeout=15000)

            rows_data = await page.evaluate('''() => {
                const rows = Array.from(document.querySelectorAll("table#players tbody tr"))
                    .filter(row => !row.classList.contains("thead"));

                return rows.map(row => {
                    const playerCell = row.querySelector('th[data-stat="player"] a');
                    const yearMin = row.querySelector('td[data-stat="year_min"]')?.innerText.trim() || null;
                    const yearMax = row.querySelector('td[data-stat="year_max"]')?.innerText.trim() || null;
                    const position = row.querySelector('td[data-stat="pos"]')?.innerText.trim() || null;
                    const height = row.querySelector('td[data-stat="height"]')?.innerText.trim() || null;
                    const weight = row.querySelector('td[data-stat="weight"]')?.innerText.trim() || null;
                    const colleges = Array.from(row.querySelectorAll('td[data-stat="colleges"] a'))
                        .map(a => a.innerText.trim());

                    return {
                        name: playerCell ? playerCell.innerText.trim() : null,
                        link: playerCell ? playerCell.getAttribute("href") : None,
                        yearMin,
                        yearMax,
                        position,
                        height,
                        weight,
                        colleges
                    };
                });
            }''')

            rows_data = [row for row in rows_data if row["link"]]

            for i in range(0, len(rows_data), batch_size):
                batch = rows_data[i:i + batch_size]
                results = await asyncio.gather(*(scrape_player(browser, d) for d in batch), return_exceptions=True)
                for r in results:
                    if isinstance(r, Exception):
                        print(f"⚠️ Exception in batch: {r}")
                    else:
                        players.append(r)

            await asyncio.sleep(random.uniform(*letter_delay_range))  # polite delay between letter pages

        except Exception:
            print(f"⚠️ Error scraping list page for letter '{letter}':\n{traceback.format_exc()}")

    await page.close()
    return players