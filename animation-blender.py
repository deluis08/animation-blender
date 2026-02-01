import bpy
import sys
import os

banner = r'''

  /$$$$$$            /$$                           /$$     /$$                           /$$$$$$$  /$$                           /$$                    
 /$$__  $$          |__/                          | $$    |__/                          | $$__  $$| $$                          | $$                    
| $$  \ $$ /$$$$$$$  /$$ /$$$$$$/$$$$   /$$$$$$  /$$$$$$   /$$  /$$$$$$  /$$$$$$$       | $$  \ $$| $$  /$$$$$$  /$$$$$$$   /$$$$$$$  /$$$$$$   /$$$$$$ 
| $$$$$$$$| $$__  $$| $$| $$_  $$_  $$ |____  $$|_  $$_/  | $$ /$$__  $$| $$__  $$      | $$$$$$$ | $$ /$$__  $$| $$__  $$ /$$__  $$ /$$__  $$ /$$__  $$
| $$__  $$| $$  \ $$| $$| $$ \ $$ \ $$  /$$$$$$$  | $$    | $$| $$  \ $$| $$  \ $$      | $$__  $$| $$| $$$$$$$$| $$  \ $$| $$  | $$| $$$$$$$$| $$  \__/
| $$  | $$| $$  | $$| $$| $$ | $$ | $$ /$$__  $$  | $$ /$$| $$| $$  | $$| $$  | $$      | $$  \ $$| $$| $$_____/| $$  | $$| $$  | $$| $$_____/| $$      
| $$  | $$| $$  | $$| $$| $$ | $$ | $$|  $$$$$$$  |  $$$$/| $$|  $$$$$$/| $$  | $$      | $$$$$$$/| $$|  $$$$$$$| $$  | $$|  $$$$$$$|  $$$$$$$| $$      
|__/  |__/|__/  |__/|__/|__/ |__/ |__/ \_______/   \___/  |__/ \______/ |__/  |__/      |_______/ |__/ \_______/|__/  |__/ \_______/ \_______/|__/      
                                          

'''

print(banner)

argv = sys.argv
argv = argv[argv.index("--") + 1:]
if "--" not in sys.argv or len(argv) < 3:
    print("[-] Usage: blender -b -P animation-blender.py -- character.fbx anim_folder ./output.(glb|gltf)")
    sys.exit(1)

character_fbx = argv[0]
anim_folder = argv[1]
output_file = argv[2]
extension = os.path.splitext(output_file)[1].lower()

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

print("[*] Importing character:", character_fbx)
bpy.ops.import_scene.fbx(filepath=character_fbx)

armature = None
for obj in bpy.context.scene.objects:
    if obj.type == 'ARMATURE':
        armature = obj
        break

if armature is None:
    print("[-] No armature found in character file")
    sys.exit(1)

armature.animation_data_create()
print("[*] Character imported successfully.")

anim_files = [
    os.path.join(anim_folder, f)
    for f in os.listdir(anim_folder)
    if f.lower().endswith(".fbx")
]

anim_files.sort()

if not anim_files:
    print("[-] No animation files found.")
    sys.exit(1)

for anim_path in anim_files:
    print("[*] Importing animation:", anim_path)

    bpy.ops.import_scene.fbx(filepath=anim_path)

    imported_arm = None
    imported_objects = list(bpy.context.selected_objects)

    for obj in imported_objects:
        if obj.type == 'ARMATURE':
            imported_arm = obj
            break

    if imported_arm and imported_arm.animation_data:
        action = imported_arm.animation_data.action

        if action:
            action_name = os.path.splitext(os.path.basename(anim_path))[0]
            action.name = action_name
            action.use_fake_user = True

            track = armature.animation_data.nla_tracks.new()
            track.name = action_name
            track.strips.new(
                action_name,
                int(action.frame_range[0]),
                action
            )

    bpy.ops.object.select_all(action='DESELECT')
    for obj in imported_objects:
        if obj.name in bpy.context.scene.objects:
            obj.select_set(True)

    bpy.ops.object.delete()

print("[*] Animations merged successfully.")

bpy.ops.object.select_all(action='DESELECT')
armature.select_set(True)
bpy.context.view_layer.objects.active = armature

print("[*] Exporting:", output_file)

if extension == ".glb":
    bpy.ops.export_scene.gltf(
        filepath=output_file,
        export_format='GLB',
        export_animations=True,
        export_nla_strips=True,
        export_apply=True
    )

elif extension == ".gltf":
    bpy.ops.export_scene.gltf(
        filepath=output_file,
        export_format='GLTF_SEPARATE',
        export_animations=True,
        export_nla_strips=True,
        export_apply=True
    )

else:
    print("[-] Unsupported export format:", extension)
    sys.exit(1)

print("[*] Export complete:", output_file)
