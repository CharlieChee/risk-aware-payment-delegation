"""Check publication language, source paths, secret patterns, and file integrity."""
from pathlib import Path
import gzip, hashlib, json, re, subprocess

ROOT=Path(__file__).resolve().parents[1]
CJK=re.compile(r'[\u3400-\u9fff]')
SECRET=re.compile(r'(?<![A-Za-z0-9])(?:sk-[A-Za-z0-9_-]{20,}|gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}|-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----)')
PRIVATE_PATH=re.compile(r'/(?:Users|home)/[^/\s]+/')
TEXT={'.py','.md','.txt','.tex','.bib','.sty','.bst','.json','.jsonl','.csv','.yml','.yaml','.cff'}

def main():
    failures=[];checked=0
    for p in ROOT.rglob('*'):
        rel=p.relative_to(ROOT)
        if not p.is_file() or any(x in ['.git','.venv','__pycache__','output','runs'] for x in rel.parts):continue
        if p.name in ['.DS_Store'] or p.suffix=='.pyc':continue
        if CJK.search(str(rel)):failures.append((str(rel),'non-English filename'))
        if p.name.startswith('.env') or p.name.lower() in ['key.txt','settings.json','auth.json']:
            failures.append((str(rel),'credential/configuration filename'))
        if p.suffix=='.gz':
            with gzip.open(p,'rt',encoding='utf-8') as f:text=f.read()
        elif p.suffix in TEXT or p.name in ['README','NOTICE','LICENSE','.gitignore']:
            text=p.read_text(encoding='utf-8-sig')
        else:continue
        checked+=1
        if rel.parts[0]!='bilingual' and CJK.search(text):failures.append((str(rel),'Chinese outside bilingual material'))
        if SECRET.search(text):failures.append((str(rel),'secret-pattern match'))
        if PRIVATE_PATH.search(text):failures.append((str(rel),'personal workstation path'))
    artifacts=json.loads((ROOT/'data/artifacts/manifest.json').read_text())
    for shard in artifacts['shards']:
        p=ROOT/shard['path'];assert hashlib.sha256(p.read_bytes()).hexdigest()==shard['sha256']
        with gzip.open(p,'rt') as f:assert sum(1 for _ in f)==shard['records']
    report=dict(status='passed' if not failures else 'failed',text_assets_checked=checked,
                artifact_records=artifacts['records'],failures=failures)
    (ROOT/'output').mkdir(exist_ok=True)
    (ROOT/'output/release_audit.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
    if failures:raise SystemExit(1)

if __name__=='__main__':main()
