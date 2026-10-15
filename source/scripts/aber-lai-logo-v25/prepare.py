from pathlib import Path
import shutil,zipfile,json,re
r=Path('work/aber-lai-logo-v25');old=Path('./workspace/reference/localized-logo-panel')
src=r/'ui-source'; (src/'panorama/styles').mkdir(parents=True,exist_ok=True);(src/'panorama/layout').mkdir(parents=True,exist_ok=True)
css=(old/'ui-source/panorama/styles/citadel_hero_logo.css').read_text()
# Keep engine fallback for heroes not present in the map.
css=css.replace('#LogoImage, .ShowHeroLogo #LogoImage { visibility: collapse; }','').replace('.HeroName, .ShowHeroName .HeroName, .ShowHeroName.ShowHeroLogo .HeroName { visibility: collapse; }','')
css=css.replace('CitadelHeroLogo #NaidanLocalizedLogo { width: 600px; visibility: visible; }','CitadelHeroLogo #NaidanLocalizedLogo { width: 600px; visibility: collapse; }')
css=css.replace('panorama/images/heroes/hero_names/baba_naidan_english.vsvg','panorama/images/heroes/hero_names/baba.vsvg')
# Preserve stock engine image styling for unmapped future heroes.
base=Path('work/niulai-successor/retail-ui-decoded/panorama/styles/citadel_hero_logo.css').read_text()
css=base+'\n'+css
m=json.loads((old.parent/'yellow-v3/hero-logo-map.json').read_text())
for hero in m:
 for prefix in [f'.{hero} CitadelHeroLogo',f'CitadelHeroLogo.{hero}']:
  css+=f'\n{prefix} #NaidanLocalizedLogo {{ visibility: visible; }}\n{prefix} #LogoImage, {prefix} .HeroName {{ visibility: collapse; }}\n'
(src/'panorama/styles/citadel_hero_logo.css').write_text(css)
shutil.copy2(old/'ui-source/panorama/layout/citadel_hero_logo.xml',src/'panorama/layout/citadel_hero_logo.xml')
shutil.copytree(old/'stage/panorama/images/naidan_official_names',r/'art-stage/panorama/images/naidan_official_names',dirs_exist_ok=True)
# Abrams artwork in the existing v24 mod must win over stock copies.
for lang in ['english','schinese']:
 (r/f'art-stage/panorama/images/naidan_official_names/{lang}/abrams.vsvg_c').unlink()
with zipfile.ZipFile(r/'ui-source.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in src.rglob('*'):
  if p.is_file():z.write(p,p.relative_to(src))
print('Prepared independent logo panel for',len(m),'heroes; fallback preserved for unmapped heroes')
