import hou

# Получаем путь к txt-файлу в папке TEMP
def get_txt_file_path():
    import tempfile, os
    file_path = os.path.join(tempfile.gettempdir(), "lk_Import-Export.txt")
    return file_path

# Читаем файл и выписываем имя объекта, точки и полигоны
def parse_txt_file(file_path):
    txt_file = open(file_path, "r")
    lines = txt_file.readlines()
    txt_file.close()

    name = ""; points = []; faces = []
    for line in lines:
        if line.startswith("Name:"):
            name = line.strip()[5:]
            break

    for line in lines:
        if line.startswith("p"):
            points.append([float(x) for x in line.strip()[2:].split(" ")])
            
        if line.startswith("f"):
            faces.append([int(x) for x in line.strip()[2:].split(" ")])
    
    return name, points, faces

def lk_import():
    # Получаем путь к txt-файлу и парсим его
    file_path = get_txt_file_path()
    name, points, faces = parse_txt_file(file_path)

    # Create Geometry node
    hou.node('obj/').createNode("geo", name, run_init_scripts=False)

    # Create Python script node inside
    hou.node('obj/' + name).createNode("python", name)

    # Set code in the Python node to execute
    hou.node('obj/' + name + '/' + name).setParms({"python": """
import tempfile, os, re

txt_file = open(tempfile.gettempdir() + os.sep + "lk_Import-Export.txt", "r")
lines = txt_file.readlines()
txt_file.close()

node = hou.pwd()
geo = hou.pwd().geometry()

points = []; faces = []
for line in lines:
    if line.startswith("p"):
        points.append(line.strip()[2:].split(" "))
    if line.startswith("f"):
        faces.append(line.strip()[2:].split(" "))

# Create points
hou_points = []
for p in points:
    pos = [float(p[0]), float(p[1]), float(p[2])]
    pt = geo.createPoint()
    pt.setPosition(pos)
    hou_points.append(pt)

# Create faces                                
for f in faces:
    poly = geo.createPolygon()
    for i in f:
        poly.addVertex(hou_points[int(i)])
"""})

    hou.node('obj/' + name + '/' + name).setHardLocked(1)

def lk_export():
    for node in hou.selectedNodes():
        selPath = node.path()

    sel = selPath.split("/")[-2]
    
    #Creating Python node for export
    if len(selPath.split("/")) > 3:
        hou.node('obj/'+sel).createNode("python", "ExportScript")
        hou.node('obj/'+sel+'/ExportScript/').setParms({"python": '''
import tempfile, os

filePath = tempfile.gettempdir() + os.sep + os.sep + "lk_Import-Export.txt"

node = hou.pwd()
geo = node.geometry()                                                        

obj_node = node.parent() # Get the parent OBJ node
world_xform = obj_node.worldTransform() # Get the world transform matrix                                                      
                                                        
if len(geo.points()) > 0:
    f = open(filePath, "w")
    f.write("Points:"+str(len(geo.points())) + "\\n")
    for point in geo.points():
        local_pos = point.position()
        pos = local_pos * world_xform
        f.write("p " + str(pos[0]) + " " + str(pos[1]) + " " + str(pos[2]) + "\\n")

    f.write("Faces:"+str(len(geo.prims())) + "\\n")
    count = 0
    for (fid, prim) in enumerate(geo.prims()):
        ppoint = ""
        for point in reversed(prim.vertices()):
            ppoint += " " + str(hou.Vertex.point(point).number())
        
        transform = ppoint[1:].split(" ")
        transform.insert(0, transform[-1])
        transform = transform[:-1]
        ppoint = " ".join(transform)

        f.write("f " + ppoint + "\\n")
        count += 1
    f.close()'''})
        hou.node('obj/'+sel).createNode("convert", "lee2key_tools_convert")
        hou.node('obj/'+sel+'/lee2key_tools_convert/').setInput(0, hou.node(selPath))
        hou.node('obj/'+sel+'/ExportScript/').setInput(0, hou.node('obj/'+sel+'/lee2key_tools_convert/'))
        hou.node('obj/'+sel+'/ExportScript/').setDisplayFlag(True)
        hou.node('obj/'+sel+'/ExportScript/').setRenderFlag(True)
        hou.node('obj/'+sel+'/ExportScript/').setCurrent(1, False)
        hou.node('obj/'+sel+'/ExportScript/').cook(force=True, frame_range=(int(hou.frame()),int(hou.frame())))
        hou.node('obj/'+sel+'/ExportScript/').destroy()
        hou.node('obj/'+sel+'/lee2key_tools_convert/').destroy()

def main():
    sel = hou.selectedNodes()

    if len(sel) == 0:
        lk_import()

    elif len(sel) == 1:
        lk_export()

    else:
        hou.ui.displayMessage("Please select only one node to export it or select nothing to import", title="lee2key_tools")

if __name__ == "__main__":
    main()