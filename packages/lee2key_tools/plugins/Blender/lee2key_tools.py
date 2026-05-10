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