import c4d, tempfile, os

def lk_import():
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

    # Записываем имя объекта и другие данные
    output = f"o {name}\n"
    output += "g default\n"

    # Записываем точки
    for verts in vertline:
        for i in range(verts[1] + 1, verts[1] + verts[0] + 1):
            x = list(map(float, lines[i].split()))
            output += "v " + str(x[0]) + " " + str(x[1]) + " " + str(x[2]) + "\n"

    # Записываем UV
    values = []
    assignment = []
    for uvMap in uvMaps:
        count = 0
        for i in range(int(uvMap[0])):
            split = lines[uvMap[1]+1+count].split(":")
            if str(float(split[0].split(" ")[0])) + " " + str(float(split[0].split(" ")[1])) not in values:
                values.append(str(float(split[0].split(" ")[0])) + " " + str(float(split[0].split(" ")[1])))
            assignment.append(str(float(split[0].split(" ")[0])) + " " + str(float(split[0].split(" ")[1])))
            count +=1

        values.sort()
        for val in values:
            output += "vt " + val + "\n"

    # Записываем нормали
    for N in vtxnormals:
        for i in range(N[1] + 1, N[1] + N[0] + 1):
            x = list(map(float, lines[i].split()))
            output += "vn " + str(x[0]) + " " + str(x[1]) + " " + str(x[2]) + "\n"

    # Записываем полигоны
    for polygons in polyline:
        count = 0
        ncount = 0
        mat = ""
        testnorm = []

        for i in range(polygons[1] + 1, polygons[1] + polygons[0] + 1):
            pts = lines[i].split(";;")[0].split(",")
            newpts = []
            #indices in an obj start at 1, so we gotta add one to each index
            testpts = []
            testidx = []
            for p in range(len(pts)):
                if len(uvMaps) < 1:
                    newpts.append(str(int(pts[p]) + 1))
                    if len(vtxnormals) > 0:
                        newpts[-1] = str(newpts[-1]) + "//" + str(count+1)
                else:
                    testpts.append(str(int(pts[p])+1))
                    testidx.append(str(values.index(assignment[count])+1))
                    if len(vtxnormals) > 0:
                        testnorm.append(count)
                count += 1
            string = ""
            for t in range(len(testpts)):
                string += " " + testpts[t] + "/" + testidx[len(testpts)-1-t]
                if len(testnorm) > 0:
                    string += "/" + str(testnorm[ncount]+1)
                    ncount += 1
            if lines[i].split(";;")[1].strip() != mat:
                output += "g " + lines[i].split(";;")[1].strip() + "\n"
                output += "usemtl " + lines[i].split(";;")[1].strip() + "\n"
                #output += "s 1\n"
                mat = lines[i].split(";;")[1].strip()
            if string != "":
                output += "f " + string.strip() + "\n"
            else:
                output += "f " + " ".join(newpts) + "\n"

    # Записываем в .obj файл
    obj_filepath = tempfile.gettempdir() + os.sep + "lk_C4DImport.obj" # Записываем путь к obj-файлу в папке TEMP, через который будем импортировать
    obj_file = open(obj_filepath, "w")
    obj_file.write(output)
    obj_file.close()

    flags = (c4d.SCENEFILTER_OBJECTS | c4d.SCENEFILTER_MATERIALS | c4d.SCENEFILTER_MERGESCENE)
    c4d.documents.MergeDocument(doc, obj_filepath, flags, None) # Импортируем .obj файл в Синему

def lk_export():
    # Создаем пустую сцену с выделенным объектом
    docTemp = c4d.documents.IsolateObjects(doc, sel)
    if docTemp == None:
        return

    # Создаем путь к obj файлу в системной папке TEMP
    obj = tempfile.gettempdir() + os.sep + "lk_Import-Export_c4d_export.obj"

    # Сохраняем выделенный файл из временной сцены в формате obj в папку TEMP
    save = c4d.documents.SaveDocument(docTemp, obj, c4d.SAVEDOCUMENTFLAGS_DONTADDTORECENTLIST, 1030178)

    if save:
        # Открываем и читаем сохраненный obj файл
        file = open(obj, "r")
        lines = file.readlines()
        file.close()

        # Списки для записи данных о геометрии
        points = []; polygons = []; uvs = []; vertexnormals = []

        # Проходим по каждой строчке из obj файла
        count = 0
        for line in lines:
            if line.startswith("v "):
                points.append(line.strip()[2:])
            if line.startswith("f "):
                polygons.append([line.strip()[2:], count])
            if line.startswith("vt "):
                uvs.append(line.strip()[2:])
            if line.startswith("vn "):
                vertexnormals.append(line.strip()[2:])
            count += 1

        # Записываю программу из которой был экспорт
        output = "FROM:C4D\n"

        # Записываю имя выделенного объекта
        name = sel[0].GetName()
        output += "Name:" + name + "\n"

        # Записываем точки
        output += "Points:" + str(len(points)) + "\n"
        for p in points:
            output += p + "\n"

        # Записываю полигоны
        output += "Polygons:" + str(len(polygons)) + "\n"
        count = 0
        uvinfo = []
        mat = "Default"
        for poly in polygons:
            pts = poly[0].split(" ")
            newpts = []
            #indices in an vertdata start at 0, so we gotta subtract one from each index
            for p in pts:
                if "/" in p:
                    newpts.append(str(int(p.split("/")[0]) - 1))
                    uvinfo.append([count, int(p.split("/")[1]), int(p.split("/")[0]) - 1])
                else:
                    newpts.append(str(int(p) - 1))
            count += 1
            if "usemtl" in lines[poly[1]-1]:
                mat = lines[poly[1]-1].split(" ")[1].strip()
            output += ",".join(newpts) + ";;" + mat + ";;FACE\n"

        # Записываю UV
        if len(uvinfo) > 0:
            output += "UV:" + str(len(uvinfo)) + "\n"
            for info in uvinfo:
                output += uvs[info[1]-1][1:] + ":PLY:" + str(info[0]) + ":PNT:" + str(info[2]) + "\n"

        # Записываю нормали
        if len(vertexnormals) > 0:
            output += "Normals:" + str(len(vertexnormals)) + "\n"
            for normal in vertexnormals:
                output += normal + "\n"

        # Записываю данные в txt файл в папке TEMP
        txt_file = open(tempfile.gettempdir() + os.sep + "lk_Import-Export.txt", "w")
        txt_file.write(output)
        txt_file.close()

sel = doc.GetActiveObjects(c4d.GETACTIVEOBJECTFLAGS_CHILDREN)
if len(sel) == 0:
    lk_import()
    c4d.gui.MessageDialog("Импорт завершен")

elif len(sel) == 1:
    lk_export()
    c4d.gui.MessageDialog("Экспорт завершен")

else:
    c4d.gui.MessageDialog("Please select only one object")

c4d.EventAdd() # Обновляем вьюпорт