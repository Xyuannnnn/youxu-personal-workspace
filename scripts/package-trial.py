"""Package public assets only; never upload the repository or local user data."""
from pathlib import Path
import zipfile

root = Path(__file__).resolve().parents[1]
dist = root / 'dist'
output = root / 'releases' / 'gradlife-trial.zip'
output.parent.mkdir(exist_ok=True)
assets = {name: (dist / name).read_text() for name in
          ['app.js', 'attachments.js', 'cloud-entry.js', 'cloud.css', 'cloud.html', 'style.css']}
needle = 'fetch("index.html", { cache: "no-store" })'
assert assets['cloud-entry.js'].count(needle) == 1, 'Bundle changed: inspect shell URL before packaging'
assets['cloud-entry.js'] = assets['cloud-entry.js'].replace(needle, 'fetch("workspace-shell.html", { cache: "no-store" })')
assets['cloud.html'] = assets['cloud.html'].replace('<a href="index.html">返回本机工作台</a>', '')
assets['workspace-shell.html'] = (dist / 'index.html').read_text()
assets['index.html'] = '''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="refresh" content="0;url=cloud.html"><title>GradLife</title></head><body><a href="cloud.html">进入邮箱登录工作台</a></body></html>'''
with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as archive:
    for name, text in assets.items():
        archive.writestr(name, text)
print(f'{output}: {len(assets)} public assets; no repository, credentials, or user records included (public client key is bundled).')
