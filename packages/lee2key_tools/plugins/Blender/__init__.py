bl_info = {
    "name": "lee2key tools",
    "author": "Karen Lee",
    "version": (0, 14),
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
from bpy.utils import register_class, unregister_class

# 0. Interface
class lee2key_rename(Menu):
    bl_idname = "VIEW3D_MT_lee2key_rename"
    bl_label = "Rename..."
    
    def draw(self, context):
        layout = self.layout
        layout.operator("object.rename_numbers")
        layout.operator("object.rename_meshdata")
        layout.operator("object.rename_material")

class lee2key_drawmenu(Menu):
    bl_idname = "VIEW3D_MT_lee2key_drawmenu"
    bl_label = "lee2key tools v0.14"
    
    def draw(self, context):
        layout = self.layout
        layout.operator("object.lk_import_export", icon='UV_SYNC_SELECT')
        layout.operator("mesh.origintoselected")
        layout.operator("object.origintoground")
        layout.menu(lee2key_rename.bl_idname)

class lee2key_tools(Operator):
    bl_idname = "view3d.lee2key_tools"
    bl_label = "lee2key tools"
    
    def execute(self, context):
        bpy.ops.wm.call_menu(name=lee2key_drawmenu.bl_idname)
        return {'FINISHED'}

# 1. Origin to Selected
class Origin_to_Selected(Operator):
    """Set object origin to center of selection"""
    bl_label = "Origin to Selected"
    bl_idname = "mesh.origintoselected"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if context.active_object.mode == 'EDIT':
            c = bpy.context.scene.cursor.location.copy()            
            bpy.ops.view3d.snap_cursor_to_selected()
            bpy.ops.object.editmode_toggle()
            bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
            bpy.context.scene.cursor.location = [c[0], c[1], c[2]]
        else:
            self.report({'INFO'}, 'Go to Edit Mode')
        
        return {'FINISHED'}

# 2. Origin to Ground
class Origin_to_Ground(Operator):
    """Moves origin to bottom center of the object"""
    bl_label = "Origin to Ground"
    bl_idname = "object.origintoground"
    bl_options = {'REGISTER', 'UNDO'}
        
    def execute(self, context):
        objects = bpy.context.selected_objects
        cursor_loc = bpy.context.scene.cursor.location.copy()
        bpy.ops.object.mode_set(mode = 'OBJECT')
        
        for obj in objects:
            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.mode_set(mode='EDIT')
            bm = bmesh.from_edit_mesh(obj.data)
            bm.verts.ensure_lookup_table()
            
            #Находим минимальное значение по Z
            z = (obj.matrix_world @ bm.verts[0].co)[2]
            for vert in bm.verts:
                if (obj.matrix_world @ vert.co)[2] < z:
                    z = (obj.matrix_world @ vert.co)[2]
            new_loc = [0, 0, z]
            
            #Находим минимальное и максимальное значения по X, а затем их середину
            x_min = (obj.matrix_world @ bm.verts[0].co)[0]
            for vert in bm.verts:
                if (obj.matrix_world @ vert.co)[0] < x_min:
                    x_min = (obj.matrix_world @ vert.co)[0]        
            
            x_max = (obj.matrix_world @ bm.verts[0].co)[0]
            for vert in bm.verts:
                if (obj.matrix_world @ vert.co)[0] > x_max:
                    x_max = (obj.matrix_world @ vert.co)[0]
            new_loc[0] = (x_min+x_max)/2
            
            #Находим минимальное и максимальное значения по Y, а затем их середину
            y_min = (obj.matrix_world @ bm.verts[0].co)[1]
            for vert in bm.verts:
                if (obj.matrix_world @ vert.co)[1] < y_min:
                    y_min = (obj.matrix_world @ vert.co)[1]
                    
            y_max = (obj.matrix_world @ bm.verts[0].co)[1]
            for vert in bm.verts:
                if (obj.matrix_world @ vert.co)[1] > y_max:
                    y_max = (obj.matrix_world @ vert.co)[1]
            new_loc[1] = (y_min+y_max)/2
            
            bpy.context.scene.cursor.location = new_loc
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
        
        bpy.context.scene.cursor.location = cursor_loc            
        
        return {'FINISHED'}

# 3. Rename with Numbers
class Rename_Numbers(Operator):
    """Set suffixes with numbers"""
    bl_label = "With numbers"
    bl_idname = "object.rename_numbers"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        selected = bpy.context.selected_objects
        i = 0
        
        if len(selected) < 10:
            lessten = True
        else:
            lessten = False
        
        for obj in selected:
            i += 1
            new_name = obj.name
            
            if '.' in new_name:
                r = new_name.split('.')
                new_name = r[0]
            
            if '_' in new_name:
                r = new_name.split('_')
                new_name = r[0]
            
            if lessten:
                obj.name = new_name + "_" + str(i)
            else:
                if i < 10:
                    obj.name = new_name + "_0" + str(i)
                else:
                    obj.name = new_name + "_" + str(i)
        
        return {'FINISHED'}

# 4. Rename Object Data
class Rename_MeshData(Operator):
    """Rename Mesh Data as object's name"""
    bl_label = "Mesh Data as Object"
    bl_idname = "object.rename_meshdata"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        for i in bpy.context.selected_objects:
            if i.type != 'EMPTY':
                i.data.name = i.name
        
        return {'FINISHED'}

# 5. Rename Material
class Rename_Material(Operator):
    """Rename first material on the object as object's name"""
    bl_label = "Materal as Object"
    bl_idname = "object.rename_material"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        selected = bpy.context.selected_objects
        for obj in selected:
            if obj.type == 'MESH':
                if len(obj.data.materials) > 0:
                    obj.data.materials[0].name = obj.name
        
        return {'FINISHED'}

# 6. Import and Export to Cloud
class lk_Import_Export(Operator):
    """Import mesh from memory to the scene"""
    bl_label = "lk Import/Export"
    bl_idname = "object.lk_import_export"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        
        file = tempfile.gettempdir() + os.sep + "lee2key_tools_export.txt"
        name = "Imported"
        
        # IMPORT OBJECT
        if len(bpy.context.selected_objects) == 0:
            
            # Read temp file
            if os.path.exists(file):
              f = open(file)
              lines = f.readlines()
              f.close()
            else:
                print("Cannot find file")

            vertline = []; polyline = []; uvMaps = []; morphMaps = []; weightMaps = []
            count = 0

            # Parse the file to see what data we have
            for line in lines:
                if line.startswith("NAME:"):
                    name = line.strip().split(":")[1].strip()
                if line.startswith("VERTICES:"):
                    vertline.append([int(line.strip().split(":")[1].strip()), count])
                if line.startswith("POLYGONS:"):
                    polyline.append([int(line.strip().split(":")[1].strip()), count])
                if line.startswith("UV:"):
                    uvMaps.append([line.strip().split(":")[1:], count])  # changed this to add the # of uv coordinates into the mix
                if line.startswith("MORPH"):
                    morphMaps.append([line.split(":")[1].strip(), count])
                if line.startswith("WEIGHT"):
                    weightMaps.append([line.split(":")[1].strip(), count])
                count += 1

            #create Points
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

            #setup  weightmaps
            for weightMap in weightMaps:
              vg = obj.vertex_groups.new(weightMap[0])
              count = 0
              for v in range(len(verts)):
                if lines[weightMap[1]+1+count].strip() != "None":
                  vg.add([v], float(lines[weightMap[1]+1+count].strip()), "ADD")
                count += 1

            if obj.data.shape_keys != None:
              bpy.ops.object.shape_key_remove(all=True)

            #create Base Shape Key
            if len(morphMaps) > 0:
              shapeKey = obj.shape_key_add(from_mix=False)
              #shapeKey.name = "Base"
              for vert in obj.data.vertices:
                shapeKey.data[vert.index].co = vert.co

            #Set Morph Map Values
            for morphMap in morphMaps:
              shapeKey = obj.shape_key_add(from_mix=False)
              shapeKey.name = morphMap[0]
              count = 0
              for vert in obj.data.vertices:
                if lines[morphMap[1]+1+count].strip() != "None":
                  x = float(lines[morphMap[1]+1+count].split(" ")[0])
                  y = float(lines[morphMap[1]+1+count].split(" ")[1])
                  z = float(lines[morphMap[1]+1+count].split(" ")[2])*-1
                  newVert = Vector((vert.co[0] + x, vert.co[1] + z, vert.co[2]+y))
                  shapeKey.data[vert.index].co = newVert
                count += 1

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
            
            if lines[0].startswith("FROM:C4D"):
                for vertex in mesh.vertices:
                    vertex.co *= 0.01
        
        # EXPORT OBJECT 
        else:
            def mesh_to_weight_list(ob, me):
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

            f = open(file, "w")
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

            #write all weights
            result1, result2 = mesh_to_weight_list(obj, mesh)
            if len(result1[0]) > 0:
                count = 0
                for weight in result1:
                    f.write("WEIGHT:" + weight + "\n")
                    for r in result2:
                        f.write(str(r[count]) + "\n")
                    count += 1

            #write object morphs
            keys = obj.data.shape_keys
            if keys:
                for key in keys.key_blocks[1:]:
                    f.write("MORPH:" + key.name + "\n")
                    basis_verts = keys.key_blocks[0].data
                    for j, kv in enumerate(key.data):
                        delta = kv.co - basis_verts[j].co
                        f.write(str(delta[0]) + " " + str(delta[2]) + " " + str(delta[1]*-1) + "\n")

            #UVs
            for j, ul in enumerate(mesh.uv_layers):
                uv = []
                for poly in mesh.polygons:
                    for i in poly.loop_indices:
                        l = mesh.loops[i]
                        v = mesh.vertices[l.vertex_index]
                        uv.append([str(ul.data[l.index].uv[0]), str(ul.data[l.index].uv[1]), str(poly.index), str(l.vertex_index) ])
                f.write("UV:" + ul.name + ":" + str(len(uv)) + "\n")
                for entry in uv:
                    f.write(entry[0] + " " + entry[1] + ":PLY:" + entry[2] + ":PNT:" + entry[3] + "\n")
        
        return {'FINISHED'}

classes = [
    lee2key_rename,
    lee2key_drawmenu,
    lee2key_tools,
    Origin_to_Selected,
    Origin_to_Ground,
    Rename_Numbers,
    Rename_MeshData,
    Rename_Material,
    lk_Import_Export
]

addon_keymaps = []

def register():
    for cl in classes:
        register_class(cl)
    
    kc = bpy.context.window_manager.keyconfigs.addon
    km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
    kmi = km.keymap_items.new("view3d.lee2key_tools", 'FOUR', 'PRESS')
    addon_keymaps.append((km, kmi))

def unregister():
    for cl in reversed(classes):
        unregister_class(cl)
    
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

if __name__ == "__main__":
    register()
