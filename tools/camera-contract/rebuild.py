"""Reproduce the released VPK from an exact baseline, optionally rerunning repair source."""
from pathlib import Path
import argparse,hashlib,json,struct,zlib,tempfile,subprocess,shutil

def digest(b):return hashlib.sha256(b).hexdigest()
def read_vpk(b):
 sig,ver,size=struct.unpack_from('<3I',b);assert sig==0x55aa1234 and ver==2
 p=28;files={}
 def string():
  nonlocal p
  q=b.index(0,p);s=b[p:q].decode();p=q+1;return s
 while(ext:=string()):
  while(d:=string()):
   while(n:=string()):
    crc,pre,arc,off,length,end=struct.unpack_from('<IHHIIH',b,p);p+=18;assert arc==32767 and end==65535
    value=b[p:p+pre]+b[28+size+off:28+size+off+length];p+=pre;assert zlib.crc32(value)==crc
    files[(d+'/'if d!=' 'else'')+n+'.'+ext]=value
 return files

def write_vpk(files):
 groups={}
 for p,b in sorted(files.items()):
  d,_,n=p.rpartition('/');name,ext=n.rsplit('.',1);groups.setdefault(ext,{}).setdefault(d or' ',[]).append((name,b))
 tree=bytearray();payload=bytearray()
 for ext,dirs in sorted(groups.items()):
  tree+=ext.encode()+b'\0'
  for d,entries in sorted(dirs.items()):
   tree+=d.encode()+b'\0'
   for name,b in entries:tree+=name.encode()+b'\0'+struct.pack('<IHHIIH',zlib.crc32(b),0,32767,len(payload),len(b),65535);payload+=b
   tree+=b'\0'
  tree+=b'\0'
 tree+=b'\0';b=struct.pack('<7I',0x55aa1234,2,len(tree),len(payload),0,48,0)+tree+payload;b+=hashlib.md5(tree).digest()+hashlib.md5(b'').digest();b+=hashlib.md5(b).digest();return b

def main():
 p=argparse.ArgumentParser();p.add_argument('baseline',type=Path);p.add_argument('output',type=Path);p.add_argument('--version',required=True);p.add_argument('--from-source',action='store_true');p.add_argument('--vrf-project',type=Path);p.add_argument('--dotnet',default='dotnet');a=p.parse_args()
 repo=Path(__file__).resolve().parents[2];release=repo/'release-data'/('v'+a.version);cfg=json.loads((release/'release.json').read_text());raw=a.baseline.read_bytes();assert digest(raw)==cfg['baselineVpkSHA256'],'Wrong baseline';files=read_vpk(raw);hero=cfg['hero'];model=f'models/heroes_wip/{hero}/{hero}.vmdl_c'
 if a.from_source:
  if not a.vrf_project:p.error('--from-source requires --vrf-project')
  with tempfile.TemporaryDirectory(prefix='camera-contract-')as tmp:
   t=Path(tmp);(t/'clips').mkdir();(t/'retail').mkdir();source=t/(hero+'.vmdl_c');source.write_bytes(files[model]);retail=t/'retail'/(hero+'.vmdl_c');shutil.copy2(release/('retail-'+hero+'.vmdl_c'),retail)
   def run(project,*args):
    pr=repo/'tools/camera-contract'/project/(project+'.csproj');subprocess.run([a.dotnet,'build',str(pr),'-p:ValveResourceFormatProject='+str(a.vrf_project.resolve()),'--nologo','-v:q'],check=True);subprocess.run([a.dotnet,str(pr.parent/'bin/Debug/net10.0'/(project+'.dll')),*map(str,args)],check=True)
   if hero=='baba':
    for k,b in files.items():
     if k.startswith('models/heroes_wip/baba/clips/')and k.endswith('.vnmclip_c'):(t/'clips'/Path(k).name).write_bytes(b)
    run('ConvertNew',release/'retail-baba.vnmskel_c',release/'legacy-baba.vnmskel_c',release/'new-clips',t/'converted')
    for f in (t/'converted/models/heroes_wip/baba/clips').glob('*.vnmclip_c'):shutil.copy2(f,t/'clips'/f.name)
   run('Patch',source,retail,t/'clips',t/'patched');files[model]=(t/'patched'/(hero+'.vmdl_c')).read_bytes()
   if hero=='baba':
    files['models/heroes_wip/baba/baba.vnmskel_c']=(release/'legacy-baba.vnmskel_c').read_bytes()
    for f in (t/'patched/clips').glob('*.vnmclip_c'):files['models/heroes_wip/baba/clips/'+f.name]=f.read_bytes()
 else:
  for f in (release/'compiled').rglob('*'):
   if f.is_file():files[f.relative_to(release/'compiled').as_posix()]=f.read_bytes()
 expected=json.loads((release/'payload-sha256.json').read_text());assert {k:digest(v)for k,v in files.items()}==expected,'Resource manifest differs';b=write_vpk(files);assert digest(b)==cfg['expectedVpkSHA256'],'VPK hash differs';assert read_vpk(b)==files
 a.output.parent.mkdir(parents=True,exist_ok=True)
 with a.output.open('xb')as f:f.write(b)
 print('PASS',cfg['name'],cfg['version'],len(files),'resources',digest(b))
if __name__=='__main__':main()
