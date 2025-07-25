import re
from playwright.sync_api import sync_playwright

author_date_pattern = re.compile(r"^[A-Za-z]+\s+[A-Za-z]+\s+\d{1,2}/\d{1,2}/\d{2,4}$")

def search_player(player_name):
    player = player_name.lower().replace(" ", "-")
    results = []  # will hold multiple analyses

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(f'https://nbadraft.net/players/{player}', wait_until='domcontentloaded', timeout=60000)
        page.wait_for_timeout(3000)

        wrappers = page.query_selector_all('.wpb_wrapper')
        
        for wrapper in wrappers:
            analysis = {"headings": [], "paragraphs": []}

            # grab all headings at once
            h3_texts = wrapper.eval_on_selector_all(
                "h3",
                "els => els.map(e => e.innerText.trim())"
            )
            for h in h3_texts:
                if h.lower() != "related content":
                    analysis["headings"].append(h)

            # grab all paragraphs at once
            p_texts = wrapper.eval_on_selector_all(
                "p",
                "els => els.map(e => e.innerText.trim())"
            )
            for p_text in p_texts:
                if "tweets by" in p_text.lower():
                    continue
                if author_date_pattern.match(p_text):
                    continue
                if len(p_text.split()) <= 4 and re.search(r"\d{1,2}/\d{1,2}/\d{2,4}", p_text):
                    continue
                analysis["paragraphs"].append(p_text)

            if analysis["headings"] or analysis["paragraphs"]:
                results.append(analysis)

        page.goto(f'https://www.nbadraftroom.com/p/{player}', wait_until='domcontentloaded', timeout=60000)
        page.wait_for_timeout(3000)
        
        wrappers = page.query_selector('.wp-block-column.is-layout-flow.wp-block-column-is-layout-flow').inner_text()
        
        print(wrappers)
        
        
        
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