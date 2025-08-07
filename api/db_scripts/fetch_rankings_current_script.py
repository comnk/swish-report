from db_script_helper_functions import parse_school, parse_247_metrics, normalize_espn_height, get_espn_star_count, is_rankings_finalized

async def fetch_247_sports_info(class_year, browser):
    rankings_247 = []
    page = await browser.new_page()

    try:
        url = f'https://247sports.com/season/{class_year}-basketball/recruitrankings/'
        await page.goto(url, wait_until='domcontentloaded', timeout=60000)
        await page.wait_for_selector("li.rankings-page__list-item", timeout=10000)

        players_data = await page.evaluate('''() => {
            const items = Array.from(document.querySelectorAll('li.rankings-page__list-item'));
            return items.map(wrapper => {
                const aTag = wrapper.querySelector('a');
                const playerName = aTag ? aTag.innerText.trim() : null;
                let playerLink = aTag ? aTag.getAttribute('href') : null;
                if (playerLink && playerLink.startsWith('/')) {
                    playerLink = 'https://247sports.com' + playerLink;
                }

                const rankDiv = wrapper.querySelector('.rank-column .primary');
                const playerRank = rankDiv ? rankDiv.innerText.trim() : null;

                const ratingDiv = wrapper.querySelector('.rating');
                let stars = 0, grade = null;
                if (ratingDiv) {
                    stars = ratingDiv.querySelectorAll('.rankings-page__star-and-score span.icon-starsolid.yellow').length;
                    const scoreSpan = ratingDiv.querySelector('.score');
                    if (scoreSpan) {
                        grade = parseInt(scoreSpan.innerText.trim());
                    }
                }

                const metaSpan = wrapper.querySelector('.meta');
                const schoolMeta = metaSpan ? metaSpan.innerText.trim() : null;

                const posDiv = wrapper.querySelector('.position');
                const position = posDiv ? posDiv.innerText.trim() : null;

                const metricsDiv = wrapper.querySelector('.metrics');
                const metrics = metricsDiv ? metricsDiv.innerText.trim() : null;

                return {
                    playerName,
                    playerLink,
                    playerRank,
                    stars,
                    grade,
                    schoolMeta,
                    position,
                    metrics
                };
            });
        }''')

        for p in players_data:
            school_name, city, state = parse_school(source='247sports', high_school_raw=p['schoolMeta'])
            height, weight = parse_247_metrics(p['metrics'])

            rankings_247.append((
                "247sports",
                str(class_year),
                p['playerRank'],
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
        print(f"⚠️ Error scraping 247sports {class_year}: {e}")
    finally:
        await page.close()

    return rankings_247


async def fetch_espn_info(class_year, browser):
    espn_rankings = []
    page = await browser.new_page()

    try:
        await page.goto(
            f'https://www.espn.com/college-sports/basketball/recruiting/rankings/scnext300boys/_/class/{class_year}/order/true',
            wait_until='domcontentloaded',
            timeout=60000
        )
        await page.wait_for_selector("tr.oddrow")

        wrappers = await page.query_selector_all("tr.oddrow, tr.evenrow")

        for wrapper in wrappers:
            tds = await wrapper.query_selector_all("td")
            if len(tds) < 8:
                continue

            player_rank = await tds[0].inner_text()
            player_rank = player_rank.strip() if player_rank else None

            # Player name & profile link
            a_tag = await tds[1].query_selector("a")
            player_name = await a_tag.inner_text() if a_tag else None
            if player_name:
                player_name = player_name.strip()
            player_link = await a_tag.get_attribute("href") if a_tag else None
            if player_link and player_link.startswith("/"):
                player_link = "https://www.espn.com" + player_link

            position = await tds[2].inner_text()
            position = position.strip() if position else None

            school_raw = await tds[3].inner_text()
            school_raw = school_raw.strip() if school_raw else ""
            school_name, city, state = parse_school(source='espn', high_school_raw=school_raw)

            height_raw = await tds[4].inner_text()
            height = normalize_espn_height(height_raw.strip() if height_raw else "")

            weight_raw = await tds[5].inner_text()
            weight = weight_raw.strip() if weight_raw else ""

            star_li = await tds[6].query_selector("li.star")
            star_class = await star_li.get_attribute("class") if star_li else ""
            stars = get_espn_star_count(star_class)

            grade_raw = await tds[7].inner_text()
            grade = grade_raw.strip() if grade_raw else ""

            espn_rankings.append((
                "espn",
                str(class_year),
                player_rank,
                grade,
                stars,
                player_name,
                player_link,
                position,
                height,
                weight,
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
        await page.goto(
            f"https://www.on3.com/rivals/rankings/player/basketball/{class_year}/",
            wait_until='domcontentloaded',
            timeout=60000
        )

        wrappers = await page.query_selector_all(".PlayerRankingsItem_block__kuO8v")

        for wrapper in wrappers:
            a_tag = await wrapper.query_selector("a")
            player_name = await a_tag.inner_text() if a_tag else None
            if player_name:
                player_name = player_name.strip()
            player_link = await a_tag.get_attribute("href") if a_tag else None
            if player_link and player_link.startswith("/"):
                player_link = "https://www.on3.com" + player_link

            # Rank
            rank_dd = await wrapper.query_selector('dl[aria-labelledby="rank"] dd')
            player_rank = await rank_dd.inner_text() if rank_dd else None
            if player_rank:
                player_rank = player_rank.strip()

            # Rating & Stars
            rating = await wrapper.query_selector('div[aria-labelledby="rating"]')
            grade = stars = None
            if rating:
                player_rating_span = await rating.query_selector('span[data-ui="player-rating"]')
                grade_text = await player_rating_span.inner_text() if player_rating_span else None
                grade = int(grade_text.strip()) if grade_text else None

                stars_span = await rating.query_selector('span[data-ui="player-stars"]')
                if stars_span:
                    star_svgs = await stars_span.query_selector_all('svg:has(path[fill="#F2C94C"])')
                    stars = len(star_svgs)
                else:
                    stars = 0
            else:
                grade = None
                stars = 0

            # Position
            position_div = await wrapper.query_selector('div[aria-labelledby="position"]')
            position = await position_div.inner_text() if position_div else None
            if position:
                position = position.strip()

            # High school + hometown → parse into city/state/school
            location_dl = await wrapper.query_selector('dl.PlayerRankingsItem_homeContainer__CLv44')
            high_school_text = ""
            hometown_text = ""
            if location_dl:
                dts = await location_dl.query_selector_all("dt")
                dds = await location_dl.query_selector_all("dd")
                for dt, dd in zip(dts, dds):
                    label = await dt.inner_text()
                    label = label.strip() if label else ""
                    if label == "High School":
                        hs_a = await dd.query_selector("a")
                        if hs_a:
                            high_school_text = await hs_a.inner_text()
                            high_school_text = high_school_text.strip() if high_school_text else ""
                        else:
                            high_school_text = await dd.inner_text()
                            high_school_text = high_school_text.strip() if high_school_text else ""
                    elif label == "Hometown":
                        hometown_text = await dd.inner_text()
                        hometown_text = hometown_text.strip() if hometown_text else ""

            school_name, city, state = parse_school(
                source="rivals",
                high_school_raw=high_school_text,
                hometown_raw=hometown_text
            )

            # Vitals (height, weight)
            vitals_dl = await wrapper.query_selector('dl.PlayerRankingsItem_vitalsContainer__XYfbI')
            height = weight = None
            if vitals_dl:
                dt_elements = await vitals_dl.query_selector_all('dt')
                dd_elements = await vitals_dl.query_selector_all('dd')
                for i, dt_el in enumerate(dt_elements):
                    label = await dt_el.inner_text()
                    label = label.strip().lower() if label else ""
                    value = await dd_elements[i].inner_text() if i < len(dd_elements) else ""
                    value = value.strip() if value else ""
                    if "height" in label:
                        height = value
                    elif "weight" in label:
                        weight = value

            # Append data
            rivals_players.append((
                "rivals",
                str(class_year),
                player_rank,
                grade,
                stars,
                player_name,
                player_link,
                position,
                height,
                weight,
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