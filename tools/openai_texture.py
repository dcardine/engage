#!/usr/bin/env python3
"""Generate a seamless ground texture with OpenAI images, cached like the Meshy models.
Usage: python3 tools/openai_texture.py [--force]
Writes assets/textures/snow_ground.png (and a 512px jpg the game loads). Skips if it already exists."""
import base64, io, json, os, sys, urllib.request
from PIL import Image
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'assets', 'textures')
KEY = os.environ.get('OPENAI_API_KEY', 'proxy-injected')
PROMPT = ('Seamless tileable top-down texture of soft fresh snow ground for a stylized cozy low-poly mobile game, '
          'hand-painted, gentle pale blue-white tones with subtle soft drifts, faint footprints-free, a few tiny pale blue '
          'shadows and sparkles, very low contrast, no objects, no rocks, no grass, no text, flat even lighting, seamless edges')
def main():
    os.makedirs(OUT, exist_ok=True)
    png = os.path.join(OUT, 'snow_ground.png')
    if os.path.exists(png) and '--force' not in sys.argv:
        print('skip: snow_ground.png already exists (no credits used)')
    else:
        req = urllib.request.Request('https://api.openai.com/v1/images/generations', method='POST',
            data=json.dumps({'model': 'gpt-image-2', 'prompt': PROMPT, 'size': '1024x1024', 'quality': 'medium', 'n': 1}).encode(),
            headers={'Authorization': 'Bearer ' + KEY, 'Content-Type': 'application/json'})
        try:
            r = json.loads(urllib.request.urlopen(req, timeout=300).read())
        except urllib.error.HTTPError as e:
            sys.exit(f'OpenAI failed: HTTP {e.code} {e.read()[:400]!r}')
        open(png, 'wb').write(base64.b64decode(r['data'][0]['b64_json']))
        print('saved', png)
    im = Image.open(png).convert('RGB')
    # make it truly tileable: blend each edge with the opposite one
    w, h = im.size; import numpy as np
    a = np.asarray(im).astype(float); s = np.roll(np.roll(a, w // 2, 1), h // 2, 0)
    y, x = np.mgrid[0:h, 0:w]; m = np.minimum(np.minimum(x, w - 1 - x), np.minimum(y, h - 1 - y)) / (w * 0.18)
    m = np.clip(m, 0, 1)[..., None]; out = a * m + s * (1 - m)
    Image.fromarray(out.astype('uint8')).resize((512, 512), Image.LANCZOS).save(os.path.join(OUT, 'snow_ground.jpg'), quality=85)
    print('wrote snow_ground.jpg')
if __name__ == '__main__': main()
