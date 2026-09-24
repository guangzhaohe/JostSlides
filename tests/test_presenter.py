"""The public deck starts offline and its teaching interaction remains correct."""
from pathlib import Path
import sys
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from slidekit.project import load_deck
from slidekit.build import build


deck = load_deck()
page_path = build(deck, activate=False)
ids = [slide['id'] for slide in deck.slides]
errors = []
requests = []

with sync_playwright() as p:
    browser = p.chromium.launch()
    context = browser.new_context(offline=True, viewport={'width': 1600, 'height': 1000})
    page = context.new_page()
    page.on('pageerror', lambda error: errors.append(str(error)))
    context.on('request', lambda request: requests.append(request.url))
    page.goto(page_path.as_uri())
    page.wait_for_function('presentationReady', timeout=120_000)
    expect(page.locator('#counter')).to_have_text(f'1 / {len(ids)}')

    page.evaluate('i=>go(i)', ids.index('moge1-normalized-shift'))
    scene = page.locator('.normalized-shift-scene')
    expect(scene).to_have_count(1)
    page.locator('input[aria-label="Affine point-map scale"]').evaluate(
        '(e)=>{e.value="2.4";e.dispatchEvent(new Event("input",{bubbles:true}))}'
    )
    page.locator('input[aria-label="Affine point-map depth shift"]').evaluate(
        '(e)=>{e.value="3.6";e.dispatchEvent(new Event("input",{bubbles:true}))}'
    )
    expect(scene).to_have_attribute('data-normalized-shift', '1.500')
    assert float(scene.get_attribute('data-projection-error')) < 1e-12

    page.evaluate('i=>go(i)', ids.index('moge3-method'))
    expect(page.locator('#slide img')).to_have_count(1)
    assert page.locator('#slide img').evaluate('(image)=>image.complete && image.naturalWidth > 0')

    page.locator('#notes-input').fill('Public test note')
    page.reload()
    page.wait_for_function('presentationReady', timeout=120_000)
    expect(page.locator('#notes-input')).to_have_value('Public test note')

    assert not errors, errors
    assert all(url.startswith(('file:', 'data:', 'blob:')) for url in requests), requests
    browser.close()

print('PASS: offline startup, notes, official pipeline asset, and normalized-shift interaction.')
