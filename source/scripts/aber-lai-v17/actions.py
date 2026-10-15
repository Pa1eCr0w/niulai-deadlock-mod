import bpy,json
from pathlib import Path
with bpy.data.libraries.load('./workspace/original/abrams-original.blend',link=False) as (src,dst):
 names=list(src.actions)
Path('./workspace/aber-lai-v17/stock-actions.json').write_text(json.dumps(names))
print('ACTIONS',len(names))
