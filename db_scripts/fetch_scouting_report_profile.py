from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)  # Set headless=True to hide browser
    page = browser.new_page()
    page.goto("https://www.nbascoutinglive.com/2024-scouting-reports/", wait_until="domcontentloaded")
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
    
    p_elements = page.query_selector_all(
        'div.the_content p:has(a[href^="https://www.nbascoutinglive.com/"])'
    )

    hrefs = []
    for p_tag in p_elements:
        # Get all <a> tags inside the paragraph (there might be more than one)
        a_tags = p_tag.query_selector_all("a[href^='https://www.nbascoutinglive.com/']")
        for a_tag in a_tags:
            href = a_tag.get_attribute("href")
            if href:
                hrefs.append(href)
    
    hrefs = hrefs[:len(hrefs)-1]
    page.goto(hrefs[-1])
    p_texts = page.eval_on_selector_all("p", "elements => elements.map(el => el.innerText)")

    start_index = -1
    end_index = -1

    for i, text in enumerate(p_texts):
        if text.startswith("Height:") or "Height:" in text:
            start_index = i
        if text.startswith("Links:") or text.startswith("Games Scouted:"):
            end_index = i
            break

    # Fallback in case structure changes
    if start_index == -1:
        raise Exception("Couldn't find start of profile.")
    if end_index == -1:
        end_index = len(p_texts)

    # Extract profile section
    player_profile = p_texts[start_index:end_index]

    # Print cleaned profile
    for line in player_profile:
        print(line)

    browser.close()