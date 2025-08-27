from playwright.sync_api import sync_playwright
from core.db import get_db_connection

def fetch_players_247_ranking_history(class_year):
    class_year_history = []

    cnx = get_db_connection()
    cursor = cnx.cursor()

    select_sql = """
    SELECT p.full_name, hspr.link FROM high_school_player_rankings AS hspr INNER JOIN players AS p ON p.player_uid=hspr.player_uid WHERE hspr.class_year=%s AND hspr.source=%s
    """
    cursor.execute(select_sql, (class_year, '247sports'))
    rows = cursor.fetchall()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)

        for (name, link) in rows:
            page = browser.new_page()
            page.goto(f'{link}', wait_until='domcontentloaded', timeout=30000)

            list_item = page.query_selector("ul.ranks-list li")
            if not list_item:
                print(f"No ranks list found for {name}")
                page.close()
                continue

            next_link_elements = list_item.query_selector_all("a")
            if len(next_link_elements) < 2:
                print(f"No next link found for {name}")
                page.close()
                continue

            next_link = next_link_elements[1].get_attribute("href")
            if not next_link:
                print(f"No href found for {name}")
                page.close()
                continue

            page.goto(next_link, wait_until='domcontentloaded', timeout=30000)

            list_items = page.query_selector_all("ul.ranking-history-list li")[1:]

            for item in list_items:
                spans = item.query_selector_all("span")
                rating = spans[0].inner_text().strip() if len(spans) > 0 else None
                rank = spans[1].inner_text().strip() if len(spans) > 1 else None
                change_date = spans[2].inner_text().strip() if len(spans) > 2 else None
                class_year_history.append((name, class_year, "247sports", rating, rank, change_date))

            page.close()

        browser.close()

    cursor.close()
    cnx.close()

    return class_year_history


def fetch_player_rivals_ranking_history(class_year):
    class_year_history = []
    cnx = get_db_connection()
    cursor = cnx.cursor()

    select_sql = """
    SELECT name, link FROM player_rankings WHERE class_year=%s AND source=%s
    """
    cursor.execute(select_sql, (class_year, 'rivals'))
    rows = cursor.fetchall()

    # TODO: Implement rivals scraping

    cursor.close()
    cnx.close()
    return class_year_history


if __name__ == "__main__":
    results = fetch_players_247_ranking_history(2027)
    print(results)