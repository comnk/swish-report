from utils.hs_helpers import parse_school, parse_247_metrics, normalize_espn_height, get_espn_star_count, is_rankings_finalized

async def fetch_247_sports_info(class_years, browser):
    rankings_247 = []
    page = await browser.new_page()

    try:
        for class_year in class_years:
            url = f'https://247sports.com/season/{class_year}-basketball/recruitrankings/'
            await page.goto(url, wait_until='domcontentloaded', timeout=120000)
            await page.wait_for_selector("ul.rankings-page__list", timeout=10000)

            # Scroll to the bottom robustly
            previous_height = 0
            scroll_attempts = 0
            max_scroll_attempts = 30  # safety limit
            while scroll_attempts < max_scroll_attempts:
                current_height = await page.evaluate("document.body.scrollHeight")
                if current_height == previous_height:
                    scroll_attempts += 1
                else:
                    scroll_attempts = 0
                    previous_height = current_height

                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await page.wait_for_timeout(1500)  # wait for lazy-loaded content

            # Extract player data
            players_data = await page.evaluate('''() => {
                return Array.from(document.querySelectorAll('li.rankings-page__list-item')).map(wrapper => {
                    const aTag = wrapper.querySelector('a');
                    let playerLink = aTag?.getAttribute('href') || null;
                    if (playerLink?.startsWith('/')) {
                        playerLink = 'https://247sports.com' + playerLink;
                    }
                    const imgTag = wrapper.querySelector('.circle-image-block img');
                    let playerImageLink = imgTag?.getAttribute('src') || null;
                    return {
                        playerName: aTag?.innerText.trim() || null,
                        playerLink,
                        playerImageLink,
                        playerRank: wrapper.querySelector('.rank-column .primary')?.innerText.trim() || null,
                        stars: wrapper.querySelectorAll('.rankings-page__star-and-score span.icon-starsolid.yellow').length || 0,
                        grade: parseInt(wrapper.querySelector('.rankings-page__star-and-score .score')?.innerText.trim()) || null,
                        schoolMeta: wrapper.querySelector('.meta')?.innerText.trim() || null,
                        position: wrapper.querySelector('.position')?.innerText.trim() || null,
                        metrics: wrapper.querySelector('.metrics')?.innerText.trim() || null
                    };
                });
            }''')

            for p in players_data:
                school_name, city, state = parse_school('247sports', p['schoolMeta'])
                height, weight = parse_247_metrics(p['metrics'])

                rankings_247.append((
                    "247sports",
                    str(class_year),
                    p['playerRank'],
                    p['playerImageLink'],
                    p['grade'],
                    p['stars'],
                    p['playerName'],
                    p['playerLink'],
                    p['position'],
                    height,
                    weight,
                    school_name,
                    city,
                    state,
                    "schooltown",
                    is_rankings_finalized(class_year)
                ))

    except Exception as e:
        print(f"⚠️ Error scraping 247sports: {e}")
    finally:
        await page.close()

    return rankings_247


async def fetch_espn_info(class_year, browser):
    espn_rankings = []
    page = await browser.new_page()

    try:
        url = f'https://www.espn.com/college-sports/basketball/recruiting/rankings/scnext300boys/_/class/{class_year}/order/true'
        await page.goto(url, wait_until='domcontentloaded', timeout=60000)
        await page.wait_for_selector("tr.oddrow, tr.evenrow", timeout=10000)

        # Extract all rows' data in one evaluate call
        rows_data = await page.evaluate('''() => {
            const rows = Array.from(document.querySelectorAll('tr.oddrow, tr.evenrow'));
            return rows.map(row => {
                const cells = Array.from(row.querySelectorAll('td'));
                if (cells.length < 8) return null;

                const playerRank = cells[0]?.innerText.trim() || null;

                const aTag = cells[1]?.querySelector('a');
                const playerName = aTag ? aTag.innerText.trim() : null;
                let playerLink = aTag ? aTag.getAttribute('href') : null;
                if (playerLink && playerLink.startsWith('/')) {
                    playerLink = 'https://www.espn.com' + playerLink;
                }

                const position = cells[2]?.innerText.trim() || null;
                const schoolRaw = cells[3]?.innerText.trim() || "";
                const heightRaw = cells[4]?.innerText.trim() || "";
                const weight = cells[5]?.innerText.trim() || "";

                const starLi = cells[6]?.querySelector('li.star');
                const starClass = starLi ? starLi.getAttribute('class') : "";
                
                const grade = cells[7]?.innerText.trim() || "";

                return {
                    playerRank,
                    playerName,
                    playerLink,
                    position,
                    schoolRaw,
                    heightRaw,
                    weight,
                    starClass,
                    grade
                };
            }).filter(item => item !== null);
        }''')

        for data in rows_data:
            school_name, city, state = parse_school(source='espn', high_school_raw=data['schoolRaw'])
            height = normalize_espn_height(data['heightRaw'])
            stars = get_espn_star_count(data['starClass'])

            espn_rankings.append((
                "espn",
                str(class_year),
                data['playerRank'],
                None,
                data['grade'],
                stars,
                data['playerName'],
                data['playerLink'],
                data['position'],
                height,
                data['weight'],
                school_name,
                city,
                state,
                "hometown",
                is_rankings_finalized(class_year)
            ))

    except Exception as e:
        print(f"⚠️ Error scraping ESPN {class_year}: {e}")
    finally:
        await page.close()

    return espn_rankings


async def fetch_rivals_info(class_year, browser):
    rivals_players = []
    page = await browser.new_page()

    try:
        url = f"https://www.on3.com/rivals/rankings/player/basketball/{class_year}/"
        await page.goto(url, wait_until='domcontentloaded', timeout=60000)
        await page.wait_for_selector(".PlayerRankingsItem_block__kuO8v", timeout=10000)

        # Extract all player data in a single evaluate call
        players_data = await page.evaluate('''() => {
            const players = Array.from(document.querySelectorAll(".PlayerRankingsItem_block__kuO8v"));
            return players.map(wrapper => {
                const aTag = wrapper.querySelector("a");
                const playerName = aTag ? aTag.innerText.trim() : null;
                let playerLink = aTag ? aTag.getAttribute("href") : null;
                if (playerLink && playerLink.startsWith("/")) {
                    playerLink = "https://www.on3.com" + playerLink;
                }
                
                const imgTag = wrapper.querySelector("img");
                let playerImageLink = imgTag ? imgTag.getAttribute("src") : null;

                const rankDd = wrapper.querySelector('dl[aria-labelledby="rank"] dd');
                const playerRank = rankDd ? rankDd.innerText.trim() : null;

                const ratingDiv = wrapper.querySelector('div[aria-labelledby="rating"]');
                let grade = null, stars = 0;
                if (ratingDiv) {
                    const ratingSpan = ratingDiv.querySelector('span[data-ui="player-rating"]');
                    grade = ratingSpan ? parseInt(ratingSpan.innerText.trim()) : null;

                    const starsSpan = ratingDiv.querySelector('span[data-ui="player-stars"]');
                    if (starsSpan) {
                        const starSvgs = starsSpan.querySelectorAll('svg:has(path[fill="#F2C94C"])');
                        stars = starSvgs.length;
                    }
                }

                const positionDiv = wrapper.querySelector('div[aria-labelledby="position"]');
                const position = positionDiv ? positionDiv.innerText.trim() : null;

                let highSchoolText = "";
                let hometownText = "";
                const locationDl = wrapper.querySelector('dl.PlayerRankingsItem_homeContainer__CLv44');
                if (locationDl) {
                    const dts = Array.from(locationDl.querySelectorAll("dt"));
                    const dds = Array.from(locationDl.querySelectorAll("dd"));
                    for (let i = 0; i < dts.length; i++) {
                        const label = dts[i].innerText.trim();
                        if (label === "High School") {
                            const hsA = dds[i].querySelector("a");
                            highSchoolText = hsA ? hsA.innerText.trim() : dds[i].innerText.trim();
                        } else if (label === "Hometown") {
                            hometownText = dds[i].innerText.trim();
                        }
                    }
                }

                let height = null, weight = null;
                const vitalsDl = wrapper.querySelector('dl.PlayerRankingsItem_vitalsContainer__XYfbI');
                if (vitalsDl) {
                    const dtElements = Array.from(vitalsDl.querySelectorAll('dt'));
                    const ddElements = Array.from(vitalsDl.querySelectorAll('dd'));
                    for (let i = 0; i < dtElements.length; i++) {
                        const label = dtElements[i].innerText.trim().toLowerCase();
                        const value = ddElements[i] ? ddElements[i].innerText.trim() : "";
                        if (label.includes("height")) {
                            height = value;
                        } else if (label.includes("weight")) {
                            weight = value;
                        }
                    }
                }

                return {
                    playerName,
                    playerLink,
                    playerImageLink,
                    playerRank,
                    grade,
                    stars,
                    position,
                    highSchoolText,
                    hometownText,
                    height,
                    weight
                };
            });
        }''')

        for p in players_data:
            school_name, city, state = parse_school(
                source="rivals",
                high_school_raw=p['highSchoolText'],
                hometown_raw=p['hometownText']
            )

            rivals_players.append((
                "rivals",
                str(class_year),
                p['playerRank'],
                p['playerImageLink'],
                p['grade'],
                p['stars'],
                p['playerName'],
                p['playerLink'],
                p['position'],
                p['height'],
                p['weight'],
                school_name,
                city,
                state,
                "hometown",
                is_rankings_finalized(class_year)
            ))

    except Exception as e:
        print(f"⚠️ Error scraping Rivals {class_year}: {e}")
    finally:
        await page.close()

    return rivals_players