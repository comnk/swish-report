from api.utils.helpers import launch_browser
from api.utils.hs_helpers import get_espn_star_count, is_rankings_finalized, parse_espn_bio, parse_city_state, normalize_position, parse_rivals_high_school

async def fetch_247_data(full_name, link):
    playwright, browser = await launch_browser(headless=True)
    page = await browser.new_page()

    await page.goto(link, wait_until='domcontentloaded', timeout=60000)

    lis = page.locator("ul.metrics-list li")
    pos = (await lis.nth(0).locator("span:nth-of-type(2)").inner_text()).strip()
    height = (await lis.nth(1).locator("span:nth-of-type(2)").inner_text()).strip()
    weight = (await lis.nth(2).locator("span:nth-of-type(2)").inner_text()).strip()

    details_lis = page.locator("ul.details li")
    school = (await details_lis.nth(0).locator("a").inner_text()).strip()

    second_span_text = (await details_lis.nth(1).locator("span:nth-of-type(2)").inner_text()).strip()
    city, state = [v.strip() for v in second_span_text.replace(" ", "").split(",")]

    class_year = (await details_lis.nth(2).locator("span:nth-of-type(2)").inner_text()).strip()

    # --- ranking block ---
    ranking_div = page.locator("div.ranking").first
    stars = await ranking_div.locator("div.stars-block span.icon-starsolid.yellow").count()
    grade = (await ranking_div.locator("div.rank-block").inner_text()).strip()

    # --- second ranks-list ---
    second_ul = page.locator("ul.ranks-list").nth(1)
    player_rank = (await second_ul.locator("li").first.locator("a").first.inner_text()).strip()

    await browser.close()
    await playwright.stop()

    return ("247sports", str(class_year), player_rank, grade, stars, full_name, link, pos, height, weight, school, city, state, "schooltown", is_rankings_finalized(int(class_year)))

async def fetch_espn_data(full_name, link):
    playwright, browser = await launch_browser(headless=True)
    page = await browser.new_page()

    await page.goto(link, wait_until='domcontentloaded', timeout=60000)
    
    ul = page.locator("ul.mod-rating")

    lis = page.locator("div.bio ul li")

    # city, state
    loc_text = await lis.nth(0).locator("a").inner_text()
    city, state = parse_city_state(loc_text)

    school = await lis.nth(1).locator("a").inner_text()

    # position
    pos_text = await lis.nth(2).locator("a").inner_text()
    position = normalize_position(pos_text)

    bio_text = await page.locator("div.bio p").inner_text()
    height, weight, class_year = parse_espn_bio(bio_text)

    grade = await ul.locator("li").nth(0).inner_text()

    second_li_class = await ul.locator("li").nth(1).get_attribute("class")
    stars = get_espn_star_count(second_li_class or "")
    
    await browser.close()
    await playwright.stop()
    
    return ("espn", str(class_year), None, grade, stars, full_name, link, position, height, weight, school, city, state, "hometown", is_rankings_finalized(int(class_year)))

async def fetch_rivals_data(full_name, link):
    playwright, browser = await launch_browser(headless=True)
    page = await browser.new_page()

    await page.goto(link, wait_until='domcontentloaded', timeout=60000)

    results = {}

    # Helper function to safely get <dd> text by matching <dt> text
    async def get_dd_by_dt_text(target_text):
        selector = f'dl.PlayerHeader_group__n4IWV dt:text("{target_text}")'
        dt_element = await page.query_selector(selector)
        if dt_element:
            dl = await dt_element.evaluate_handle("dt => dt.parentElement")  # get parent dl
            dd = await dl.query_selector("dd")
            if dd:
                return (await dd.inner_text()).strip()
        return None

    async def get_dd_for_high_school(page):
        # Select all dl elements with no class
        dd_element = await page.query_selector(
            '//dl[dt[normalize-space(translate(text(),"abcdefghijklmnopqrstuvwxyz","ABCDEFGHIJKLMNOPQRSTUVWXYZ"))="HIGH SCHOOL"]]/dd'
        )
        if dd_element:
            high_school = (await dd_element.inner_text()).strip()
        else:
            high_school = None
        
        return high_school

    # Explicitly wait and get the values
    results["class_year"] = await get_dd_by_dt_text("Class")
    results["position"] = await get_dd_by_dt_text("Pos")
    results["height"] = await get_dd_by_dt_text("Ht")
    results["weight"] = await get_dd_by_dt_text("Wt")

    industry_rating_div = await page.query_selector('div.Rankings_industryRating__5cZxi')
    grade = None
    if industry_rating_div:
        span = await industry_rating_div.query_selector('span')
        if span:
            grade = (await span.inner_text()).strip()

    # Get the aria-label from the span inside the a tag
    star_wrapper = await page.query_selector('a.StarRating_starWrapper__g_Lzo span')
    stars = None
    if star_wrapper:
        aria_label = await star_wrapper.get_attribute('aria-label')
        if aria_label:
            stars = int(aria_label.split()[0])
    
    ranking = await page.query_selector('a.Rankings_rank__9cQ0m')

    if ranking:
        ranking = (await ranking.inner_text()).strip()

    class_year_int = int(results.get("class_year", 0)) if results.get("class_year") else 0

    high_school = await get_dd_for_high_school(page)
    school, city, state = parse_rivals_high_school(high_school)
    
    await browser.close()
    await playwright.stop()

    return (
        "rivals",
        str(results.get("class_year", "")),
        ranking,
        grade,
        stars,
        full_name,
        link,
        results.get("position", ""),
        results.get("height", ""),
        results.get("weight", ""),
        school,
        city,
        state,
        "hometown",
        is_rankings_finalized(class_year_int)
    )