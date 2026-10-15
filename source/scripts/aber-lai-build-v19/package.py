from pathlib import Path
import zipfile,struct,zlib,hashlib,json
r=Path('work/aber-lai-build-v19')
with zipfile.ZipFile(r/'compiled.zip') as z:files={n.replace('\\','/'):z.read(n) for n in z.namelist() if not n.replace('\\','/').endswith('/')}
assert len(files)>=15 and files['models/heroes_wip/abrams/abrams.vmdl_c']==(r/'repaired.vmdl_c').read_bytes()
ui={f'panorama/images/heroes/{x}.vtex_c' for x in ['bull_card_psd','bull_card_gloat_psd','bull_card_critical_psd','bull_mm_psd','bull_sm_psd','bull_sm_psd_19f8ca40','bull_vertical_psd']}|{'panorama/images/hud/abilities/bull_beef_psd.vtex_c'}
ui |= {'panorama/images/hud/abilities/'+n+'.vtex_c' for n in ['bull_charge_psd','bull_jump_psd']}
ui |= {'panorama/images/'+n+'.vsvg_c' for n in ['heroes/hero_names/abrams','heroes/hero_names/abrams_localized','naidan_official_names/schinese/abrams','naidan_official_names/english/abrams']}
assert ui.issubset(files)
assert all(p=='models/heroes_wip/abrams/abrams.vmdl_c' or p.startswith('materials/models/niulai_v19/') or p in ui for p in files)
assert not any(p.startswith(('scripts/','resource/','panorama/layout/','panorama/styles/')) for p in files)

groups={}
for p,data in sorted(files.items()):
 d,_,n=p.rpartition('/');name,ext=n.rsplit('.',1);groups.setdefault(ext,{}).setdefault(d or ' ',[]).append((name,data))
tree=bytearray();payload=bytearray()
for ext,dirs in sorted(groups.items()):
 tree+=ext.encode()+b'\0'
 for d,entries in sorted(dirs.items()):
  tree+=d.encode()+b'\0'
  for name,data in entries:
   tree+=name.encode()+b'\0'+struct.pack('<IHHIIH',zlib.crc32(data),0,32767,len(payload),len(data),65535);payload+=data
  tree+=b'\0'
 tree+=b'\0'
tree+=b'\0';out=struct.pack('<7I',0x55aa1234,2,len(tree),len(payload),0,48,0)+tree+payload
out+=hashlib.md5(tree).digest()+hashlib.md5(b'').digest();out+=hashlib.md5(out).digest()
(r/'aber-lai-v19.vpk').write_bytes(out);report={'sha256':hashlib.sha256(out).hexdigest(),'files':{p:hashlib.sha256(d).hexdigest() for p,d in files.items()}}
(r/'package-manifest.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
