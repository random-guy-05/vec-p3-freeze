from __future__ import annotations

import argparse
from pathlib import Path
from .core import checklist, freeze, verify


def main(argv=None)->int:
    p=argparse.ArgumentParser(description='Freeze scarce VEC P3 submission slots.')
    s=p.add_subparsers(dest='cmd',add_help=True,required=True)
    f=s.add_parser('freeze'); f.add_argument('--bundle',type=Path,default=Path('p3_bundle')); f.add_argument('--board',required=True); f.add_argument('--slot',type=int,required=True); f.add_argument('--file',type=Path,required=True); f.add_argument('--note',default='')
    v=s.add_parser('verify'); v.add_argument('--bundle',type=Path,default=Path('p3_bundle'))
    c=s.add_parser('checklist'); c.add_argument('--bundle',type=Path,default=Path('p3_bundle')); c.add_argument('--out',type=Path)
    a=p.parse_args(argv)
    if a.cmd=='freeze':
        m=freeze(a.bundle,a.board,a.slot,a.file,a.note); print(m['sha256'], m['file']); return 0
    if a.cmd=='verify':
        rows=verify(a.bundle)
        for r in rows: print(r['status'],r['board'],r['slot'],r['file'])
        return 1 if any(r['status']!='OK' for r in rows) else 0
    text=checklist(a.bundle); out=a.out or a.bundle/'SUBMISSION_CHECKLIST.md'; out.parent.mkdir(parents=True,exist_ok=True); out.write_text(text); print(out); return 0
