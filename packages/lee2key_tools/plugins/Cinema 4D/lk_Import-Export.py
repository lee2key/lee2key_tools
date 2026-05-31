import c4d, tempfile, os

def lk_import():
    # Читаем txt-файл в папке TEMP
    txt_file = open(tempfile.gettempdir() + os.sep + "lk_Import-Export.txt", "r")
    lines = txt_file.readlines()
    txt_file.close()

    # Выписываем имя объекта, откуда экспортирован, сколько имеем точек, нормалей и прочее
    name = ""; points = []; faces = []
    for line in lines:
        if line.startswith("Name:"):
            name = line.strip()[5:]
            break
    for line in lines:
        if line.startswith("p"):
            points.append([float(x) * 100 for x in line.strip()[2:].split(" ")])
            
        if line.startswith("f"):
            faces.append([int(x) for x in line.strip()[2:].split(" ")])

    # Записываем имя объекта и другие данные
    obj = c4d.PolygonObject(len(points), len(faces))
    obj.SetName(name)
    
    # Записываем точки
    for i, pt in enumerate(points):
        vec = c4d.Vector(pt[0], pt[1], -pt[2])
        obj.SetPoint(i, vec)
    
    # Записываем фейсы
    for i, f in enumerate(faces):
        if len(f) == 3:
            poly = c4d.CPolygon(f[0], f[1], f[2], f[2])
        else:
            poly = c4d.CPolygon(f[0], f[1], f[2], f[3])
        obj.SetPolygon(i, poly)
    
    obj.Message(c4d.MSG_UPDATE)
    doc.InsertObject(obj)

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
        points = []; faces = []; normals = []; uvs = []

        # Проходим по каждой строчке из obj файла
        count = 0
        for line in lines:
            if line.startswith("v "):
                points.append(line.strip()[2:])
            if line.startswith("f "):
                faces.append([line.strip()[2:], count])
            if line.startswith("n "):
                normals.append(line.strip()[2:])
            if line.startswith("uv "):
                uvs.append(line.strip()[2:])
            count += 1

        # Записываю имя выделенного объекта
        name = sel[0].GetName()
        output = ""
        output += "Name:" + name + "\n"
        
        # Записываем точки
        output += "Points:" + str(len(points)) + "\n"
        for p in points:
            output += "p " + p + "\n"
        
        # Записываю полигоны
        output += "Faces:" + str(len(faces)) + "\n"
        count = 0
        for f in faces:
            pts = f[0].split(" ")
            newpts = []
            #indices in an vertdata start at 0, so we gotta subtract one from each index
            for p in pts:
                if "/" in p:
                    newpts.append(str(int(p.split("/")[0]) - 1))
                else:
                    newpts.append(str(int(p) - 1))
            count += 1

            output += "f " + " ".join(newpts) + "\n"

        # Записываю данные в txt файл в папке TEMP
        txt_file = open(tempfile.gettempdir() + os.sep + "lk_Import-Export.txt", "w")
        txt_file.write(output)
        txt_file.close()

sel = doc.GetActiveObjects(c4d.GETACTIVEOBJECTFLAGS_CHILDREN)
if len(sel) == 0:
    lk_import()

elif len(sel) == 1:
    lk_export()

else:
    c4d.gui.MessageDialog("Please select only one object")

c4d.EventAdd() # Обновляем вьюпорт