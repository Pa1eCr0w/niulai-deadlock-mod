from pathlib import Path
import hashlib,json,struct,zlib
root=Path(__file__).resolve().parents[1]
files={p.relative_to(root/'compiled').as_posix():p.read_bytes() for p in (root/'compiled').rglob('*') if p.is_file()}
assert len(files)==26
assert not any(p.startswith(('resource/','scripts/','panorama/images/naidan_official_names/')) for p in files)
assert not any('baba' in p or 'naidan' in p for p in files)
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
dst=root/'build';dst.mkdir(parents=True,exist_ok=True)
(dst/'niulai-independent-wordmark-candidate.vpk').write_bytes(out)
(dst/'candidate-manifest.json').write_text(json.dumps({'status':'candidate-not-installed-not-runtime-tested','sha256':hashlib.sha256(out).hexdigest(),'files':{k:hashlib.sha256(v).hexdigest() for k,v in files.items()}},indent=2))
print('Candidate built',len(files),'payloads',len(out),'bytes')
