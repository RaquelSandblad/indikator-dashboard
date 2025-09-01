"""Exportera normaliserade Infonet-tabeller till CSV i data/infonet_parsed
Skapar katalogen om den saknas och skriver en CSV per mappad nyckel.
"""
import os
from pathlib import Path
from data_sources import get_infonet_data

out_dir = Path('data') / 'infonet_parsed'
out_dir.mkdir(parents=True, exist_ok=True)

data = get_infonet_data()
if not data:
    print('Ingen infonet-data hittades; se till att PPTX finns i repo-root.')
    raise SystemExit(1)

created = []
for key, val in data.items():
    if key == 'text':
        # spara text som .txt
        p = out_dir / 'presentation_text.txt'
        p.write_text(val or '', encoding='utf-8')
        created.append(str(p))
    elif key == 'other':
        # spara varje annan tabell som separate filer
        for i, tbl in enumerate(val):
            try:
                p = out_dir / f'other_table_{i}.csv'
                tbl.to_csv(p, index=False, encoding='utf-8')
                created.append(str(p))
            except Exception as e:
                print(f"Kunde inte skriva other_table_{i}: {e}")
    else:
        try:
            p = out_dir / f'{key}.csv'
            if hasattr(val, 'to_csv'):
                val.to_csv(p, index=False, encoding='utf-8')
                created.append(str(p))
            else:
                # skriv repr
                p.write_text(repr(val), encoding='utf-8')
                created.append(str(p))
        except Exception as e:
            print(f"Kunde inte skriva {key}: {e}")

print('Skapade filer:')
for c in created:
    print(' -', c)

# Försök committa till git
import subprocess
try:
    subprocess.run(['git', 'add', str(out_dir)], check=True)
    subprocess.run(['git', 'commit', '-m', 'Add parsed infonet CSV exports'], check=True)
    # försök push
    res = subprocess.run(['git', 'push'], check=False)
    if res.returncode == 0:
        print('Pushed changes to remote')
    else:
        print('Git push misslyckades (kanske ingen remote eller autentisering saknas).')
except Exception as e:
    print('Git commit/push misslyckades:', e)
