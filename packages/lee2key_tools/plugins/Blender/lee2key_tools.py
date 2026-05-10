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

def lk_import():
    # Читаем txt-файл в папке TEMP
    txt_file = open(tempfile.gettempdir() + os.sep + "lk_Import-Export.txt", "r")
    lines = txt_file.readlines()
    txt_file.close()

    # Выписываем имя объекта, позиции точек, полигонов, нормалей и UV
    name = ""; points = []; faces = []; normals = []; uvs = []
    for line in lines:
        if line.startswith("Name:"):
            name = line.strip()[5:]
            
        if line.startswith("p"):
            points.append(line.strip()[2:].split(" "))
            
        if line.startswith("f"):
            faces.append(line.strip()[2:].split(","))

    #    if line.startswith("n:"):
    #        normals.append(int(line.strip()[2:])
    #        
    #    if line.startswith("uv:"):
    #        if line.strip().split(":")[1] != "0":
    #            uvs.append(line.strip().split(":")[1])

    # Создаем пустой объект
    mesh = bpy.data.meshes.new(name) # Create mesh data
    bm = bmesh.new() # Use bmesh for robust construction

    # Создаем точки
    bm_verts = []
    for p in points:
        pos = [float(p[0]), float(p[1]), float(p[2])]
        bm_verts.append(bm.verts.new(pos))
    bm.verts.index_update()

    # Создаем фейсы
    for f in faces:
        num = [int(f[0]), int(f[1]), int(f[2]), int(f[3])]
        face_verts = [bm_verts[i] for i in num]
        bm.faces.new(face_verts)

    bm.to_mesh(mesh)
    bm.free()
    mesh.update()

    # Create object and link to scene collection
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)


"""
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
"""

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