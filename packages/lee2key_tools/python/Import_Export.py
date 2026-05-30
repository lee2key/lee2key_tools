import hou, tempfile, os #Importing Houdini and Windows TEMP folder modules

def lk_import():
    # Read the temporary text file
    txt_file = open(tempfile.gettempdir() + os.sep + "lk_Import-Export.txt", "r")
    lines = txt_file.readlines()
    txt_file.close()

    # Extract the name for the Geometry node
    name = ""
    for line in lines:
        if line.startswith("Name:"):
            name = line.strip()[5:]
            break

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

points = []; faces = []; normals = []; uvs = []
for line in lines:
    if line.startswith("p"):
        points.append(line.strip()[2:].split(" "))
        
    if line.startswith("f"):
        faces.append(line.strip()[2:].split(","))

    # if line.startswith("Normals:"):
    #     normals.append([int(line.strip().split(":")[1].strip()), count])
    # if line.startswith("UV:"):
    #     if line.strip().split(":")[1] != "0":
    #         UV.append([line.strip().split(":")[1], count])

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
        poly.addVertex(hou_points[i])
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
# encoding: utf-8
import tempfile, os, random, sys, re

filePath = tempfile.gettempdir() + os.sep + os.sep + "lk_Import-Export.txt"

node = hou.pwd()
geo = node.geometry()

if len(geo.points()) > 0:
    f = open(filePath, "w")
    f.write("Points:"+str(len(geo.points())) + "\\n")
    for point in geo.points():
        pos = point.position()
        f.write("p " + str(pos[0]) + " " + str(pos[1]) + " " + str(pos[2]) + "\\n")

    uvs = []
    check = geo.findVertexAttrib("uv")
    f.write("Polygons:"+str(len(geo.prims())) + "\\n")
    count = 0
    for (fid, prim) in enumerate(geo.prims()):
        ppoint = ""
        for point in reversed(prim.vertices()):
            ppoint += "," + str(hou.Vertex.point(point).number())
            if check != None:
                uvs.append(str(point.attribValue("uv")[0]) + " " + str(point.attribValue("uv")[1]) + ":PLY:" + str(count) + ":PNT:" + str(hou.Vertex.point(point).number()) + "\\n")
 
        transform = ppoint[1:].split(",")
        transform.insert(0, transform[-1])
        transform = transform[:-1]
        ppoint = ",".join(transform)

        f.write("f " + ppoint + "\\n")
        count += 1

    attribs = geo.pointAttribs()
    weights = []
    for attrib in attribs:
        if attrib.type() == hou.attribType.Point:
            if attrib.dataType() == hou.attribData.Float and attrib.size() == 1:
                weights.append(attrib.name())

    if len(weights) > 0:
        for wmap in weights:
            wmapName = re.sub(r"_..", lambda m: chr(int(m.group()[1:], 16)), wmap)
            attrib = wmap
            f.write("WEIGHT:" + wmapName + "\\n")
            for p in geo.points():
                f.write(str(p.attribValue(wmap))+ "\\n")

    if len(uvs) > 0:
        f.write("UV:UVMap:"+ str(len(uvs)) + "\\n")
        for uv in uvs:
            f.write(uv)
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

def execute():
    sel = hou.selectedNodes()

    if len(sel) == 0:
        lk_import()

    elif len(sel) == 1:
        lk_export()

    else:
        hou.ui.displayMessage("Please select only one node to export it or select nothing to import", title="lee2key_tools")
