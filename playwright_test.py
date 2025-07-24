import re
from playwright.sync_api import sync_playwright

author_date_pattern = re.compile(r"^[A-Za-z]+\s+[A-Za-z]+\s+\d{1,2}/\d{1,2}/\d{2,4}$")

def search_player(player_name):
    player = player_name.lower().replace(" ", "-")
    results = []  # will hold multiple analyses

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(f'https://nbadraft.net/players/{player}')
        page.wait_for_timeout(5000)

        wrappers = page.query_selector_all('.wpb_wrapper')

        for wrapper in wrappers:
            analysis = {
                "headings": [],
                "paragraphs": []
            }

            # Collect headings
            for h3 in wrapper.query_selector_all('h3'):
                h3_text = h3.inner_text().strip()
                if h3_text.lower() == "related content":
                    continue
                analysis["headings"].append(h3_text)

            # Collect paragraphs
            for p_tag in wrapper.query_selector_all('p'):
                p_text = p_tag.inner_text().strip()

                # Skip unwanted lines
                if "tweets by" in p_text.lower():
                    continue
                if author_date_pattern.match(p_text):
                    continue
                if len(p_text.split()) <= 4 and re.search(r"\d{1,2}/\d{1,2}/\d{2,4}", p_text):
                    continue

                analysis["paragraphs"].append(p_text)

            # Only add if it has actual content
            if analysis["headings"] or analysis["paragraphs"]:
                results.append(analysis)

        page.goto(f'https://nbadraftroom.com/{player}')
        page.wait_for_timeout(5000)
        
        browser.close()

    return results
    
def main():
    while True:
        get_player = input("Enter player name here: ")
        print(f"Searching for {get_player}...")
        results = search_player(get_player)
        print(len(results))

if __name__ == '__main__':
    main()