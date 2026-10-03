import csv, json
from collections import defaultdict
from pathlib import Path
manifest = Path('scratchpad/gauntlet/ext/ability_redrive_manifests')
assert not manifest.exists(), 'Use fresh manifests or inspect the existing jobs before resuming'
corpora = json.loads(Path('icebow/data/pipeline/gen_dataset_v2.json').read_text())['corpora']
jobs, tag_files = [], {}
for slot_group, original in enumerate(corpora):
    corpus = Path(original)
    output = Path(str(corpus) + '_abil')
    assert not output.exists(), f'Output must be NEW: {output}'
    remaining = {p.stem[7:] for p in corpus.glob('replay_*.json')}
    assert remaining, corpus
    if corpus.parent.name == 'corpus_v6':
        deck = corpus.name
        sources = [(Path(deck)/'data/royaleapi/crawl2', n) for n in ('plays_ext_i1.csv', 'plays_ext.csv')]
        sources += [(Path(f'scratchpad/gauntlet/ext/crawl_hf_{deck}'), 'plays_ext.csv')]
    else:
        sources = [(p, 'plays_ext.csv') for p in sorted(Path('scratchpad/gauntlet/L68/generalist/pilot/crawl').glob('chunk_*'))]
    for crawl, plays_file in sources:
        with (crawl/'battles.csv').open(encoding='utf-8', newline='') as f:
            counts = {r['replay_tag']: int(r['plays']) for r in csv.DictReader(f)}
        events = defaultdict(list)
        with (crawl/plays_file).open(encoding='utf-8', newline='') as f:
            for r in csv.DictReader(f):
                if r['replay_tag'] in remaining:
                    events[r['replay_tag']].append(r)
        selected = sorted(t for t, rows in events.items() if len(rows) == counts.get(t)
            and all(r['attr_ability'] == '1' or all(r[k] not in ('', 'None') for k in ('x_units', 'y_units')) for r in rows))
        if selected:
            tags = manifest/f'tags_{len(jobs):03d}.json'
            tag_files[tags] = selected
            jobs.append(dict(group=slot_group, crawl=str(crawl), plays_file=plays_file, tags=str(tags), out=str(output)))
            remaining.difference_update(selected)
    assert not remaining, (corpus, 'missing source tags', sorted(remaining)[:10])
manifest.mkdir(parents=True)
for path, tags in tag_files.items():
    path.write_text(json.dumps(tags), encoding='utf-8')
(manifest/'jobs.json').write_text(json.dumps(jobs, indent=2), encoding='utf-8')
print('Prepared', len(jobs), 'jobs for', len(corpora), 'corpora;', sum(map(len, tag_files.values())), 'recordings')
