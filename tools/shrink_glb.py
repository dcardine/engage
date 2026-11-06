#!/usr/bin/env python3
"""Make Meshy models phone-friendly: downsize every embedded texture and repack the GLB.

Usage: python3 tools/shrink_glb.py [--size 512]
Reads assets/models/*.glb (the originals, kept untouched) and writes assets/game/*.glb plus a
self-contained assets/game/*.json copy, which is what the game loads. Only models that are new or changed are reprocessed.
"""
import argparse, base64, io, json, os, struct
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC, DST = os.path.join(ROOT, 'assets', 'models'), os.path.join(ROOT, 'assets', 'game')


def read_glb(path):
    b = open(path, 'rb').read()
    assert b[:4] == b'glTF', path + ' is not a GLB'
    off, js, bin_ = 12, None, b''
    while off < len(b):
        ln, kind = struct.unpack('<II', b[off:off + 8])
        chunk = b[off + 8:off + 8 + ln]
        if kind == 0x4E4F534A: js = json.loads(chunk)
        elif kind == 0x004E4942: bin_ = chunk
        off += 8 + ln
    return js, bin_


def write_glb(path, js, bin_):
    j = json.dumps(js, separators=(',', ':')).encode()
    j += b' ' * (-len(j) % 4)
    bin_ += b'\0' * (-len(bin_) % 4)
    total = 12 + 8 + len(j) + 8 + len(bin_)
    with open(path, 'wb') as f:
        f.write(struct.pack('<4sII', b'glTF', 2, total))
        f.write(struct.pack('<II', len(j), 0x4E4F534A) + j)
        f.write(struct.pack('<II', len(bin_), 0x004E4942) + bin_)


def shrink(src, dst, size):
    js, bin_ = read_glb(src)
    views = js['bufferViews']
    image_views = {im['bufferView']: i for i, im in enumerate(js.get('images', [])) if 'bufferView' in im}
    out, new_views = bytearray(), []
    for vi, v in enumerate(views):
        data = bin_[v.get('byteOffset', 0): v.get('byteOffset', 0) + v['byteLength']]
        if vi in image_views:
            im = Image.open(io.BytesIO(data))
            im.thumbnail((size, size), Image.LANCZOS)
            buf = io.BytesIO()
            if im.mode in ('RGBA', 'LA') and im.getextrema()[-1][0] < 255:   # keep real transparency
                im.save(buf, 'PNG', optimize=True); js['images'][image_views[vi]]['mimeType'] = 'image/png'
            else:
                im.convert('RGB').save(buf, 'JPEG', quality=82, optimize=True); js['images'][image_views[vi]]['mimeType'] = 'image/jpeg'
            data = buf.getvalue()
        out += b'\0' * (-len(out) % 4)
        nv = dict(v); nv['byteOffset'] = len(out); nv['byteLength'] = len(data)
        out += data; new_views.append(nv)
    js['bufferViews'] = new_views
    js['buffers'] = [{'byteLength': len(out) + (-len(out) % 4)}]
    write_glb(dst, js, bytes(out))
    # also a self-contained .json copy: claude.ai artifacts can serve JSON but not .glb
    js['buffers'] = [{'byteLength': len(out), 'uri': 'data:application/octet-stream;base64,' + base64.b64encode(bytes(out)).decode()}]
    with open(dst[:-4] + '.json', 'w') as f:
        json.dump(js, f, separators=(',', ':'))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--size', type=int, default=512); a = ap.parse_args()
    os.makedirs(DST, exist_ok=True)
    for name in sorted(os.listdir(SRC)):
        if not name.endswith('.glb'): continue
        s, d = os.path.join(SRC, name), os.path.join(DST, name)
        if os.path.exists(d) and os.path.getmtime(d) >= os.path.getmtime(s):
            print(f'skip {name}'); continue
        shrink(s, d, a.size)
        print(f'{name}: {os.path.getsize(s) // 1024} KB -> {os.path.getsize(d) // 1024} KB')


if __name__ == '__main__':
    main()
