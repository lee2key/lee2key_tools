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

import bpy, bmesh
from mathutils import Vector
from bpy.types import Operator, Panel, Menu

def get_txt_file_path():
    # Получаем путь к txt-файлу в папке TEMP
    import tempfile, os
    file_path = os.path.join(tempfile.gettempdir(), "lk_Import-Export.txt")
    return file_path

def parse_txt_file(file_path):
    # Читаем txt-файл
    txt_file = open(file_path, "r")
    lines = txt_file.readlines()
    txt_file.close()

    # Выписываем имя объекта
    name = ""; points = []; faces = []
    for line in lines:
        if line.startswith("Name:"):
            name = line.strip()[5:]
            break
    
    # Выписываем точки и полигоны
    for line in lines:
        if line.startswith("p"):
            points.append([float(x) for x in line.strip()[2:].split(" ")])
            
        if line.startswith("f"):
            faces.append([int(x) for x in line.strip()[2:].split(" ")])
    
    return name, points, faces

def import_geo():
    # Получаем путь к txt-файлу и парсим его
    file_path = get_txt_file_path()
    name, points, faces = parse_txt_file(file_path)

    # Создаем пустой объект
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()

    # Создаем точки
    bm_verts = []
    for p in points:
        pos = [float(p[0]), -float(p[2]), float(p[1])]
        bm_verts.append(bm.verts.new(pos))
    bm.verts.index_update()

    # Создаем фейсы
    for f in faces:
        face_verts = [bm_verts[int(i)] for i in f]
        # Skip degenerate faces (duplicate verts)
        if len(face_verts) != len(set(v.index for v in face_verts)):
            continue
        
        try:
            bm.faces.new(face_verts)
        except ValueError:
            pass  # Skip any other duplicate/invalid faces

    bm.to_mesh(mesh)
    bm.free()
    mesh.update()

    # Create object and link to scene collection
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)

def export_geo():
    # Получаем выделенный объект
    obj = bpy.context.active_object

    # Считаем количество точек и фейсов
    point_count = len(obj.data.vertices)
    face_count = len(obj.data.polygons)

    # Получаем путь к txt-файлу и открываем его для записи
    file_path = get_txt_file_path()
    txt_file = open(file_path, "w")

    # Записываем имя объекта в txt-файл
    txt_file.write("Name:" + obj.name + "\n")

    # Записываем точки в txt-файл
    txt_file.write("Points:" + str(point_count) + "\n")
    for vert in obj.data.vertices:
        txt_file.write("p " + str(vert.co[0]) + " " + str(vert.co[2]) + " " + str(vert.co[1]*-1) + "\n")

    # Записываем фейсы в txt-файл
    txt_file.write("Faces:" + str(face_count) + "\n")
    for poly in obj.data.polygons:
        ppoint = ""
        for idx in poly.vertices:
            ppoint += " " + str(obj.data.vertices[idx].index)
        txt_file.write("f " + ppoint[1:] + "\n")

class lk_Import_Export(bpy.types.Operator):
    """Import or Export selected objects""" # Tooltip
    bl_idname = "object.lk_import_export"
    bl_label = "lk Import-Export"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        sel = bpy.context.selected_objects

        if len(sel) == 0:
            import_geo()
            self.report({'INFO'}, "Import done")

        elif len(sel) == 1:
            export_geo()
            self.report({'INFO'}, "Export done")

        else:
            self.report({'INFO'}, "Please select only one object to export it or select nothing to import")

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