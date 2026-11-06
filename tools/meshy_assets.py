#!/usr/bin/env python3
"""Generate Frosthold's 3D models with Meshy, without paying twice for the same model.

Usage:
  python3 tools/meshy_assets.py --dry-run           # show what would be generated (spends nothing)
  python3 tools/meshy_assets.py                     # generate only what is missing
  python3 tools/meshy_assets.py --only house,yak    # limit to some ids
  python3 tools/meshy_assets.py --force house       # deliberately regenerate one model

How credits are protected:
  * assets/manifest.json records every finished model with a hash of its prompt.
    A model whose file exists and whose prompt is unchanged is skipped.
  * A job that was started but not finished is resumed by its Meshy task id
    instead of starting a new one.
  * If the manifest is lost, finished jobs in your Meshy history with the exact
    same prompt are reused before anything new is created.
  * Nothing is regenerated unless its prompt changes or you pass --force.

The API key: in the cloud session the network proxy adds it automatically.
Elsewhere, set MESHY_API_KEY in your environment.
"""
import argparse, hashlib, json, os, sys, time, urllib.request, urllib.error

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATALOG = os.path.join(ROOT, 'assets', 'catalog.json')
MANIFEST = os.path.join(ROOT, 'assets', 'manifest.json')
MODELS = os.path.join(ROOT, 'assets', 'models')
API = 'https://api.meshy.ai/openapi/v2/text-to-3d'
KEY = os.environ.get('MESHY_API_KEY', 'proxy-injected')   # the cloud proxy replaces the placeholder


def call(method, url, body=None):
    req = urllib.request.Request(url, method=method, data=json.dumps(body).encode() if body else None,
                                 headers={'Authorization': 'Bearer ' + KEY, 'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read() or b'null')
    except urllib.error.HTTPError as e:
        sys.exit(f'Meshy {method} {url} failed: HTTP {e.code} {e.read()[:300]!r}')


def load(path, default):
    try:
        with open(path) as f:
            return json.load(f)
    except FileNotFoundError:
        return default


def save_manifest(m):
    tmp = MANIFEST + '.tmp'
    with open(tmp, 'w') as f:
        json.dump(m, f, indent=2, sort_keys=True)
    os.replace(tmp, MANIFEST)          # written after every step, so an interrupted run loses nothing


def full_prompt(cat, a):
    return f"{a['prompt']}, {cat['style']}"


def phash(cat, a):
    return hashlib.sha256((full_prompt(cat, a) + '|' + cat.get('negative_prompt', '')).encode()).hexdigest()[:16]


def wait(task_id, label):
    while True:
        t = call('GET', f'{API}/{task_id}')
        st = t.get('status')
        if st == 'SUCCEEDED':
            return t
        if st in ('FAILED', 'CANCELED', 'EXPIRED'):
            raise RuntimeError(f'{label}: task {task_id} {st}: {t.get("task_error")}')
        print(f'  {label}: {st} {t.get("progress", 0)}%', flush=True)
        time.sleep(10)


def history():
    """Finished jobs already on the account, newest first (listing is free)."""
    out, page = [], 1
    while page <= 10:
        batch = call('GET', f'{API}?page_num={page}&page_size=50&sort_by=-created_at') or []
        out += batch
        if len(batch) < 50:
            break
        page += 1
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--only', default='')
    ap.add_argument('--force', default='')
    args = ap.parse_args()
    cat = load(CATALOG, None) or sys.exit('assets/catalog.json is missing')
    man = load(MANIFEST, {})
    only = {x for x in args.only.split(',') if x}
    force = {x for x in args.force.split(',') if x}
    os.makedirs(MODELS, exist_ok=True)

    todo = []
    for a in cat['assets']:
        if only and a['id'] not in only:
            continue
        h, rec = phash(cat, a), man.get(a['id'], {})
        have = rec.get('hash') == h and rec.get('status') == 'done' and os.path.exists(os.path.join(ROOT, rec.get('file', '-')))
        if have and a['id'] not in force:
            print(f'skip  {a["id"]:16} already generated (no credits used)')
            continue
        todo.append((a, h))
    if not todo:
        print('Nothing to generate.')
        return
    print(f'\n{len(todo)} model(s) to generate: ' + ', '.join(a['id'] for a, _ in todo))
    print('Each new model runs a preview job and a texture (refine) job on Meshy; check meshy.ai for current credit costs.')
    if args.dry_run:
        return

    past = None
    for a, h in todo:
        aid, rec = a['id'], man.get(a['id'], {})
        if rec.get('hash') != h or aid in force:
            rec = {'hash': h}
        prompt = full_prompt(cat, a)
        print(f'\n== {aid}')
        # 1) reuse a finished job with the identical prompt from the account history
        if not rec.get('refine') and aid not in force:
            if past is None:
                past = history()
            prev = [t for t in past if t.get('prompt') == prompt and t.get('status') == 'SUCCEEDED']
            ref = next((t for t in prev if t.get('mode') == 'refine'), None)
            pre = next((t for t in prev if t.get('mode') == 'preview'), None)
            if ref:
                rec['refine'] = ref['id']; print('  reusing a finished textured job from your Meshy history')
            elif pre and not rec.get('preview'):
                rec['preview'] = pre['id']; print('  reusing a finished preview job from your Meshy history')
        # 2) preview (shape), resumed if already started
        if not rec.get('refine'):
            if not rec.get('preview'):
                body = {'mode': 'preview', 'prompt': prompt, 'negative_prompt': cat.get('negative_prompt', ''),
                        'art_style': 'realistic', 'should_remesh': True, 'topology': 'triangle', 'target_polycount': a.get('polycount', 8000)}
                rec['preview'] = call('POST', API, body)['result']
                man[aid] = rec; save_manifest(man)
                print(f'  started preview {rec["preview"]}')
            wait(rec['preview'], 'preview')
            # 3) refine (textures), resumed if already started
            rec['refine'] = call('POST', API, {'mode': 'refine', 'preview_task_id': rec['preview'], 'enable_pbr': False})['result']
            man[aid] = rec; save_manifest(man)
            print(f'  started refine {rec["refine"]}')
        t = wait(rec['refine'], 'refine')
        # 4) download the GLB
        url = (t.get('model_urls') or {}).get('glb')
        if not url:
            sys.exit(f'{aid}: finished but no GLB url returned')
        rel = os.path.join('assets', 'models', aid + '.glb')
        with urllib.request.urlopen(url, timeout=300) as r, open(os.path.join(ROOT, rel), 'wb') as f:
            f.write(r.read())
        rec.update({'status': 'done', 'file': rel, 'thumbnail': t.get('thumbnail_url', '')})
        man[aid] = rec; save_manifest(man)
        print(f'  saved {rel}')
    print('\nAll requested models are ready.')


if __name__ == '__main__':
    main()
