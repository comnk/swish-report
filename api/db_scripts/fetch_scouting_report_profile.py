from playwright.sync_api import sync_playwright
import re

def name_to_slug(name):
    parts = name.strip().split()
    if not parts:
        return ""

    first_parts = list(parts[0])  # e.g. ['A', 'J']
    remaining_parts = parts[1:]   # e.g. ['Johnson']
    
    slug_parts = [char.lower() for char in first_parts] + [p.lower() for p in remaining_parts]
    return "-".join(slug_parts)

def get_nba_scouting_live_profile(player_name, draft_year):
    player_name = name_to_slug(player_name)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Set headless=True to hide browser
        page = browser.new_page()
        page.goto(f'https://www.nbascoutinglive.com/{player_name}', wait_until="domcontentloaded")
        # page.goto(f"https://www.nbascoutinglive.com/{draft_year}-scouting-reports/", wait_until="domcontentloaded")
        page.evaluate("""
            document.oncontextmenu = null;
            document.onselectstart = null;
            document.onmousedown = null;
        """)

        # Bypass alert popup (if it blocks DOM)
        try:
            page.on("dialog", lambda dialog: dialog.dismiss())
        except:
            pass
        
        # p_elements = page.query_selector_all(
        #     'div.the_content p:has(a[href^="https://www.nbascoutinglive.com/"])'
        # )

        # hrefs = []
        # for p_tag in p_elements:
        #     # Get all <a> tags inside the paragraph (there might be more than one)
        #     a_tags = p_tag.query_selector_all("a[href^='https://www.nbascoutinglive.com/']")
        #     for a_tag in a_tags:
        #         href = a_tag.get_attribute("href")
        #         if href:
        #             hrefs.append(href)
        
        # hrefs = hrefs[:len(hrefs)-1]
        p_texts = page.eval_on_selector_all("p", "elements => elements.map(el => el.innerText)")

        start_index = -1
        end_index = -1

        for i, text in enumerate(p_texts):
            if text.startswith("Height:") or "Height:" in text:
                start_index = i
            if text.startswith("Links:") or text.startswith("Games Scouted:"):
                end_index = i
                break

        if start_index == -1:
            raise Exception("Couldn't find start of profile.")
        if end_index == -1:
            end_index = len(p_texts)

        # Extract profile section
        player_profile = p_texts[start_index:end_index]

        page.close()
        browser.close()
        
        return player_profile

def get_nba_draft_net_profile(player_name):
    import re
    from playwright.sync_api import sync_playwright

    player_name = player_name.lower().replace(" ", "-")
    author_date_pattern = re.compile(r"^[A-Za-z]+\s+[A-Za-z]+\s+\d{1,2}/\d{1,2}/\d{2,4}$")
    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(f"https://www.nbadraft.net/players/{player_name}")

        wrappers = page.query_selector_all('.wpb_wrapper')

        for wrapper in wrappers:
            # Grab all headings and paragraphs
            h3_texts = wrapper.eval_on_selector_all("h3", "els => els.map(e => e.innerText.trim())")
            h3_texts = [h for h in h3_texts if h.lower() != "related content"]

            p_texts = wrapper.eval_on_selector_all("p", "els => els.map(e => e.innerText.trim())")
            clean_paragraphs = []
            for p in p_texts:
                if "tweets by" in p.lower():
                    continue
                if author_date_pattern.match(p):
                    continue
                if len(p.split()) <= 4 and re.search(r"\d{1,2}/\d{1,2}/\d{2,4}", p):
                    continue
                clean_paragraphs.append(p)

            # Just append the full text block
            if h3_texts or clean_paragraphs:
                section_text = ""
                for h in h3_texts:
                    section_text += f"{h}\n"
                if clean_paragraphs:
                    section_text += "\n".join(clean_paragraphs)
                results.append(section_text.strip())

    return "\n\n".join(results)

def get_nba_draft_room_profile(player_name):
    player_name = player_name.lower().replace(" ", "-")
    result_text = ""
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Set headless=True to hide browser
        page = browser.new_page()
        page.goto(f'https://www.nbadraftroom.com/p/{player_name}', wait_until='domcontentloaded', timeout=60000)
        page.wait_for_timeout(3000)
        
        wrappers = page.query_selector('.wp-block-column.is-layout-flow.wp-block-column-is-layout-flow')
        
        page.evaluate("""
            () => {
                const pre = document.querySelector('.wp-block-preformatted.has-background.has-medium-font-size');
                if (pre && pre.textContent.includes('Early Season 2025 Big Board')) {
                    pre.remove();
                }
            }
        """)
        
        result_text = wrappers.inner_text()
        
        browser.close()
    
    return result_text


#print(get_nba_scouting_live_profile('AJ Johnson', 2024))
print(get_nba_draft_net_profile('AJ Johnson'))
#print(get_nba_draft_room_profile('AJ Johnson'))