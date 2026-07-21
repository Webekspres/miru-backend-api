path = '.ai-steering/08-task-list.md'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()
replacements = [
    ('- [ ] Model konten edukasi', '- [x] Model konten edukasi'),
    ('- [ ] CRUD API \u2014 admin/koordinator', '- [x] CRUD API \u2014 admin/koordinator'),
    ('- [ ] List/detail public (atau auth nasabah) untuk mobile', '- [x] List/detail public (atau auth nasabah) untuk mobile'),
    ('- [ ] Seed konten awal dari panduan pemilahan', '- [x] Seed konten awal dari panduan pemilahan'),
]
for old, new in replacements:
    content = content.replace(old, new)
with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print('Task list updated')
