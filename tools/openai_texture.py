#!/usr/bin/env python3
"""Generate the seamless ground textures with OpenAI images, without paying twice.

Usage: python3 tools/openai_texture.py [--force name]
Each texture is cached in assets/textures/textures.json by a hash of its prompt: an unchanged
prompt whose image exists is skipped. Writes assets/textures/<name>.png (original) and
<name>.jpg (tileable, what the game loads).
"""
import base64, hashlib, json, os, sys, urllib.request, urllib.error
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'assets', 'textures')
MAN = os.path.join(OUT, 'textures.json')
KEY = os.environ.get('OPENAI_API_KEY', 'proxy-injected')   # the cloud proxy replaces the placeholder
STYLE = ('seamless tileable ground texture seen from straight above, hand-painted 2D mobile strategy game terrain, '
         'rich painterly detail, soft natural lighting, crisp small details, no objects larger than a hand, '
         'no trees, no buildings, no characters, no text, no border, even coverage edge to edge')
TEXTURES = {
    'snow_ground': 'fresh packed snow field: gentle blue-violet shadowed hollows and soft wind-carved drifts, '
                   'scattered small animal footprints and paw tracks, a few tiny dry grass tufts and twigs poking through, '
                   'occasional small grey pebbles half buried, faint sparkle, clean bright white and icy blue palette',
    'grass_ground': 'lush meadow grass: varied greens with lighter and darker patches, small worn sandy dirt patches, '
                    'tiny white and yellow wildflowers, little grass tufts and clover, a few small grey pebbles, '
                    'cozy bright saturated palette',
}


def tileable(png, jpg):
    im = Image.open(png).convert('RGB')
    w, h = im.size
    a = np.asarray(im).astype(float)
    s = np.roll(np.roll(a, w // 2, 1), h // 2, 0)               # the same image shifted half a tile: its seams sit in the middle
    y, x = np.mgrid[0:h, 0:w]
    m = np.clip(np.minimum(np.minimum(x, w - 1 - x), np.minimum(y, h - 1 - y)) / (w * 0.16), 0, 1)[..., None]
    Image.fromarray((a * m + s * (1 - m)).astype('uint8')).save(jpg, quality=86)


def main():
    os.makedirs(OUT, exist_ok=True)
    force = set(sys.argv[sys.argv.index('--force') + 1].split(',')) if '--force' in sys.argv else set()
    man = json.load(open(MAN)) if os.path.exists(MAN) else {}
    for name, desc in TEXTURES.items():
        prompt = desc + ', ' + STYLE
        h = hashlib.sha256(prompt.encode()).hexdigest()[:16]
        png, jpg = os.path.join(OUT, name + '.png'), os.path.join(OUT, name + '.jpg')
        if man.get(name) == h and os.path.exists(png) and name not in force:
            print(f'skip {name}: already generated (no credits used)')
        else:
            req = urllib.request.Request('https://api.openai.com/v1/images/generations', method='POST',
                data=json.dumps({'model': 'gpt-image-2', 'prompt': prompt, 'size': '1024x1024', 'quality': 'high', 'n': 1,
                                 'stream': True, 'partial_images': 2}).encode(),   # streamed so long renders are not cut off
                headers={'Authorization': 'Bearer ' + KEY, 'Content-Type': 'application/json'})
            img = None
            try:
                with urllib.request.urlopen(req, timeout=600) as r:
                    for line in r:
                        if line.startswith(b'data:'):
                            ev = json.loads(line[5:])
                            if ev.get('type') == 'image_generation.completed': img = ev['b64_json']
            except urllib.error.HTTPError as e:
                sys.exit(f'OpenAI failed for {name}: HTTP {e.code} {e.read()[:400]!r}')
            if not img: sys.exit(f'OpenAI returned no image for {name}')
            open(png, 'wb').write(base64.b64decode(img))
            man[name] = h
            json.dump(man, open(MAN, 'w'), indent=2)
            print('generated', name)
        tileable(png, jpg)
    print('done')


if __name__ == '__main__':
    main()
