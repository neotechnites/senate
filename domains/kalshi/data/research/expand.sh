#!/bin/zsh
cd /Users/ryanwhitehead/Documents/senate/domains/kalshi/data/research
until grep -q ALLDONE family_pull2.log; do sleep 15; done
/usr/bin/python3 - <<'PY'
import json,os
C='/Users/ryanwhitehead/Documents/senate/domains/kalshi/data/research/family_census_cache'
# EXPANSION (pre-declared): for the two priority families take the FULL population,
# not a sample. No selection is involved - census, so no sampling bias possible.
for f in ('KXFEDFUNDSYEAR','KXUSCPIYEAR','KXNOMGDPGROWTH'):
    p=os.path.join(C,f'sample2_{f}.json'); o=json.load(open(p))
    mk=[m['ticker'] for m in json.load(open(os.path.join(C,f'markets_{f}.json')))]
    rest=[t for t in sorted(mk) if t not in set(o['sample'])]
    o['sample']=o['sample']+rest; o['expanded_to_full_population']=True
    json.dump(o,open(p,'w'),indent=1); print(f,len(o['sample']))
PY
N=999 NBOOKS=40 /usr/bin/python3 family_census_pull.py KXFEDFUNDSYEAR,KXUSCPIYEAR,KXNOMGDPGROWTH >> family_pull3.log 2>&1
echo EXPDONE >> family_pull3.log
