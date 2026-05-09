bl_info = {
    "name": "lee2key_tools",
    "author": "Karen Lee",
    "version": (0, 16),
    "blender": (3, 0, 0),
    "location": "",
    "description": "",
    "warning": "",
    "doc_url": "",
    "category": "Object",
}

import bpy, bmesh, tempfile, os
from mathutils import Vector
from bpy.types import Operator, Panel, Menu

# ── CONFIGURATION ────────────────────────────────────────────────
TXT_FILE_PATH = r"C:\Users\lee2key\Desktop\Untitled.obj"
# ─────────────────────────────────────────────────────────────────


def parse_obj_txt(filepath: str):
    """
    Parse a text file.

    Returns
    -------
    objects : list of dict
        Each dict has:
          'name'  : str
          'verts' : list of (x, y, z) float tuples
          'faces' : list of lists of 0-based vertex indices
    """

    objects = []
    current = None

    # Accumulators across the whole file (OBJ indices are global)
    all_verts = []

    def new_object(name="Imported"):
        return {"name": name, "vert_start": len(all_verts), "face_defs": []}

    with open(filepath, "r", encoding="utf-8") as fh:
        for raw_line in fh:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue

            parts = line.split()
            token = parts[0]

            if token == "o":
                # Start a new object block
                current = new_object(" ".join(parts[1:]) if len(parts) > 1 else "Object")
                objects.append(current)

            elif token == "v":
                x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
                all_verts.append((x, y, z))
                # If we haven't seen an 'o' line yet, create a default object
                if current is None:
                    current = new_object()
                    objects.append(current)

            elif token == "f":
                if current is None:
                    current = new_object()
                    objects.append(current)
                # Each face token may be  v  or  v/vt  or  v/vt/vn  or  v//vn
                # OBJ indices are 1-based; negative indices count from end
                face_indices = []
                for tok in parts[1:]:
                    v_idx_str = tok.split("/")[0]
                    v_idx = int(v_idx_str)
                    if v_idx < 0:
                        v_idx = len(all_verts) + v_idx          # negative index
                    else:
                        v_idx -= 1                              # convert to 0-based
                    face_indices.append(v_idx)
                current["face_defs"].append(face_indices)

            # vn / vt / s / mtllib / usemtl — intentionally ignored

    # Build per-object local vertex list and remap face indices
    result = []
    for obj in objects:
        vert_start = obj["vert_start"]
        # Collect only the vertices that belong to this object.
        # Because OBJ verts are global we determine the range from
        # vert_start up to the next object's vert_start.
        next_obj_idx = objects.index(obj) + 1
        if next_obj_idx < len(objects):
            vert_end = objects[next_obj_idx]["vert_start"]
        else:
            vert_end = len(all_verts)

        local_verts = all_verts[vert_start:vert_end]

        # Remap global face indices → local
        local_faces = []
        for face in obj["face_defs"]:
            local_face = [idx - vert_start for idx in face]
            # Safety: skip faces whose indices fall outside this object's vert range
            if all(0 <= i < len(local_verts) for i in local_face):
                local_faces.append(local_face)

        result.append({
            "name": obj["name"],
            "verts": local_verts,
            "faces": local_faces,
        })

    return result


def build_mesh_object(name: str, verts, faces):
    #Creates an object from vertex positions and face index lists.

    # Create mesh data
    mesh = bpy.data.meshes.new(name=name)

    # Use bmesh for robust construction
    bm = bmesh.new()

    # Add vertices
    bm_verts = [bm.verts.new(v) for v in verts]
    bm.verts.index_update()

    # Add faces (bmesh deduplicates edges automatically)
    for face_indices in faces:
        try:
            face_verts = [bm_verts[i] for i in face_indices]
            bm.faces.new(face_verts)
        except ValueError as err:
            # Duplicate face or degenerate polygon — skip silently
            print(f"  [skip] face {face_indices}: {err}")

    bm.to_mesh(mesh)
    bm.free()

    mesh.update()

    # Create object and link to scene collection
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)

    return obj


def lk_import():
    path = bpy.path.abspath(TXT_FILE_PATH)

    if not os.path.isfile(path):
        raise FileNotFoundError(f"File not found: {path}")

    print(f"\n── Importing: {path}")
    objects = parse_obj_txt(path)

    if not objects:
        print("No geometry found in file.")
        return

    created = []
    for obj_data in objects:
        name  = obj_data["name"]
        verts = obj_data["verts"]
        faces = obj_data["faces"]

        print(f"  Object '{name}': {len(verts)} verts, {len(faces)} faces")

        if not verts:
            print(f"    (no vertices — skipping)")
            continue

        blender_obj = build_mesh_object(name, verts, faces)
        created.append(blender_obj)
        print(f"    → Created Blender object: '{blender_obj.name}'")

    # Select all created objects and make the last one active
    bpy.ops.object.select_all(action='DESELECT')
    for obj in created:
        obj.select_set(True)
    if created:
        bpy.context.view_layer.objects.active = created[-1]

    print(f"\n── Done. {len(created)} object(s) added to the scene.\n")






def lk_import_old():
    # Читаем txt-файл в папке TEMP
    txt_file = open(tempfile.gettempdir() + os.sep + "lk_Import-Export.txt", "r")
    lines = txt_file.readlines()
    txt_file.close()

    # Выписываем имя объекта, откуда экспортирован, сколько имеем точек, нормалей и прочее
    vertline = []; polyline = []; vtxnormals = []; uvMaps = []; name = ""
    count = 0
    for line in lines:
        if line.startswith("Points:"):
            vertline.append([int(line.strip().split(":")[1].strip()), count])
        if line.startswith("Polygons:"):
            polyline.append([int(line.strip().split(":")[1].strip()), count])
        if line.startswith("Normals:"):
            vtxnormals.append([int(line.strip().split(":")[1].strip()), count])
        if line.startswith("UV:"):
            if line.strip().split(":")[1] != "0":
                uvMaps.append([line.strip().split(":")[1], count])
        if line.startswith("Name:"):
            name = line.strip().split(":")[1]
        count += 1

    # Записываем точки
    for v in vertline:
        verts = []
        for i in range(v[1] + 1, v[1] + v[0] + 1):
        x = lines[i].split(" ")
        pt = [ float(x[0].strip()), float(x[2].strip())*-1, float(x[1].strip()) ]
        verts.append(pt)

    blenderMats = bpy.data.materials[:]
    blenderMatsNames = []
    for bm in blenderMats:
        blenderMatsNames.append(bm.name)

    # Записываем полигоны
    for polygons in polyline:
        faces = []
        facesMat = []
        objMats = []
        for i in range(polygons[1] + 1, polygons[1] + polygons[0] + 1):
        pts = []
        surf = (lines[i].split(";;")[1]).strip()
        for x in (lines[i].split(";;")[0]).strip().split(","):
            pts.append(int(x.strip()))
        faces.append(pts)
        if surf not in blenderMatsNames:
            blenderMatsNames.append(surf)
            bpy.data.materials.new(surf)
            #obj.data.materials.append(blenderSurf)
        if surf not in objMats:
            objMats.append(surf)
        facesMat.append(surf)

    #remove old object first
    obj = bpy.context.active_object
    if obj != None:
        me = obj.data
        bpy.ops.object.mode_set(mode = 'OBJECT')
        facesr = me.polygons
        for f in facesr: f.select = 1
        bpy.ops.object.mode_set(mode = 'EDIT')
        bpy.ops.mesh.delete(type='FACE')
        bpy.ops.object.mode_set(mode = 'OBJECT')
        mesh = me
        mesh.from_pydata(verts, [], faces)
        mesh.update()
        mesh.update()
    else:
    # the rest keep like in this example
    # here the mesh data is constructed
        mesh = bpy.data.meshes.new(name)
        mesh.from_pydata(verts, [], faces)
        mesh.update()
        mesh.update()
        # now generate an object to hold this data
        obj = bpy.data.objects.new(name, mesh)
        # link the object to the scene (it is not visible so far!)
        bpy.context.scene.collection.objects.link(obj)

    for i in range(len(obj.material_slots)):
        bpy.ops.object.material_slot_remove({'object': obj})
    for mat in objMats:
        obj.data.materials.append(bpy.data.materials.get(mat))

    for i in range(len(faces)):
        obj.data.polygons[i].material_index = objMats.index(facesMat[i])

    # create vertex group lookup dictionary for names
    vgroup_names = {vgroup.index: vgroup.name for vgroup in obj.vertex_groups}

    # create dictionary of vertex group assignments per vertex
    vgroups = {v.index: [vgroup_names[g.group] for g in v.groups] for v in obj.data.vertices}

    for x in obj.vertex_groups:
        obj.vertex_groups.remove(x)

    for x in mesh.uv_layers:
        mesh.uv_layers.remove(x)

    for uvMap in uvMaps:
        uv = mesh.uv_layers.new(name=uvMap[0][0])
        bm = bmesh.new()
        bm.from_mesh(mesh)
        bm.faces.ensure_lookup_table()
        uv_layer = bm.loops.layers.uv[uv.name]

        count = 0
        for i in range(int(uvMap[0][1])):
            line = lines[uvMap[1]+1+count]
            split = line.split(":")
            if len(split) > 3: #check the format to see if it has a point and poly classifier, determining with that, whether the uv is discontinuous or continuous
                face = (bm.faces[int(split[2])].loops[count%(len(bm.faces[int(split[2])].loops))])[uv_layer].uv = [float(split[0].split(" ")[0]), float(split[0].split(" ")[1])]
            else:
                pass
            count +=1
        bm.to_mesh(mesh)

    bpy.context.view_layer.update()
    
    # EXPORT OBJECT
    def lk_export2(ob, me):
        # clear the vert group.
        group_names = [g.name for g in ob.vertex_groups]
        group_names_tot = len(group_names)
        if not group_names_tot:
            # no verts? return a vert aligned empty list
            return [[] for i in range(len(me.vertices))], []
        else:
            weight_ls = [[0.0] * group_names_tot for i in range(len(me.vertices))]
        for i, v in enumerate(me.vertices):
            for g in v.groups:
                # possible weights are out of range
                index = g.group
                if index < group_names_tot:
                    weight_ls[i][index] = g.weight
        return group_names, weight_ls

    # get active object
    obj = bpy.context.active_object
    mesh = obj.data
    name = obj.name

    point_count = len(obj.data.vertices)
    poly_count = len(obj.data.polygons)

    f = open(txt_file, "w")
    f.write ("VERTICES:" + str(point_count) + "\n")

    #write Vertices
    for vert in obj.data.vertices:
        f.write(str(vert.co[0]) + " " + str(vert.co[2]) + " " + str(vert.co[1]*-1) + "\n")

    #write polygons-point connection for poly reconstructions
    f.write("POLYGONS:" + str(poly_count) + "\n")
    for poly in obj.data.polygons:
        surf = "Default"
        if len(obj.material_slots)!= 0:
            slot = obj.material_slots[poly.material_index]
            surf = slot.name
        ppoint = ""
        polytype = "FACE"
        for idx in poly.vertices:
            ppoint += "," + str(obj.data.vertices[idx].index)
        f.write(ppoint[1:] + ";;" + str(surf) + ";;" + polytype + "\n")
    
    return {'FINISHED'}

class lk_Import_Export(bpy.types.Operator):
    """Import or Export selected objects""" # Tooltip
    bl_idname = "object.lk_import_export"
    bl_label = "lk Import-Export"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        lk_import()
        self.report({'INFO'}, "Done")
        return {'FINISHED'}

# Define the menu function
def menu_func(self, context):
    self.layout.separator()
    self.layout.operator(lk_Import_Export.bl_idname)

def register():
    bpy.utils.register_class(lk_Import_Export)
    bpy.types.VIEW3D_MT_object.append(menu_func)

def unregister():
    bpy.types.VIEW3D_MT_object.remove(menu_func)
    bpy.utils.unregister_class(lk_Import_Export)

if __name__ == "__main__":
    register()