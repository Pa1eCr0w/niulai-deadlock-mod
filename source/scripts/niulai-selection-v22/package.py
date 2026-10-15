from pathlib import Path
import zipfile,struct,zlib,hashlib,json
r=Path('work/niulai-selection-v22')
with zipfile.ZipFile('work/aber-lai-build-v19/compiled.zip') as z:files={n.replace(chr(92),'/'):z.read(n) for n in z.namelist() if not n.replace(chr(92),'/').endswith('/')}
with zipfile.ZipFile('work/niulai-successor/changed-compiled.zip') as z:files.update({n.replace(chr(92),'/'):z.read(n) for n in z.namelist() if not n.replace(chr(92),'/').endswith('/')})
oldmanifest=json.loads(Path('outputs/niulai-successor/package-manifest.json').read_text())
assert {p:hashlib.sha256(d).hexdigest() for p,d in files.items()}==oldmanifest['files']
with zipfile.ZipFile(r/'changed-compiled.zip') as z:changes={n.replace(chr(92),'/'):z.read(n) for n in z.namelist() if not n.replace(chr(92),'/').endswith('/')}
allowed={f'panorama/images/heroes/{n}.vtex_c' for n in ['bull_vertical_psd']}
assert set(changes)==allowed
files.update(changes)
assert not any(p.startswith('scripts/') for p in files)
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
(r/'aber-lai-npr.vpk').write_bytes(out);report={'sha256':hashlib.sha256(out).hexdigest(),'files':{p:hashlib.sha256(d).hexdigest() for p,d in files.items()}}
(r/'package-manifest.json').write_text(json.dumps(report,indent=2));print('PACKAGE',report['sha256'],len(files),'resources; changed',len(changes))
