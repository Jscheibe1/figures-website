import json, asyncio, sys
from playwright.async_api import async_playwright
jobs=json.load(open('imgjobs.json')); OUT='/home/claude/figures-website/assets/'
only=sys.argv[1:] 
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page()
        for j in jobs:
            if only and j['name'] not in only: continue
            x,y,w,h=j['vb']
            await pg.set_viewport_size(dict(width=j['w'],height=j['h']))
            await pg.set_content(f'<html><body style="margin:0;background:transparent"><svg xmlns="http://www.w3.org/2000/svg" viewBox="{x} {y} {w} {h}" width="{j["w"]}" height="{j["h"]}" style="display:block">{j["svg"]}</svg></body></html>')
            await pg.screenshot(path=OUT+j['name'],omit_background=j['t']); print(j['name'])
        await b.close()
asyncio.run(main())
