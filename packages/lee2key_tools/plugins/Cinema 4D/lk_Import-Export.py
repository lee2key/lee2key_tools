import c4d, tempfile, os
from c4d import utils

def parse_txt_file(path):
    # Читаем txt-файл в папке TEMP
    txt_file = open(path, "r")
    lines = txt_file.readlines()
    txt_file.close()

    # Выписываем имя объекта, точки и полигоны
    name = ""; points = []; faces = []
    for line in lines:
        if line.startswith("Name:"):
            name = line.strip()[5:]
            break
    
    scale = 100 # Масштабируем координаты для корректного отображения в C4D
    for line in lines:
        if line.startswith("p"):
            points.append([float(x) * scale for x in line.strip()[2:].split(" ")])
            
        if line.startswith("f"):
            faces.append([int(x) for x in line.strip()[2:].split(" ")])
    
    return name, points, faces

def melt_ngons(obj, ngon_translations):
    # Сливаем треугольники обратно в N-гоны, используя сохраненные индексы в ngon_translations
    if ngon_translations:        
        poly_selection = obj.GetPolygonS() # Получаем полигоны объекта
        
        for ngon_list in ngon_translations:
            poly_selection.DeselectAll() # Снимаем выделение перед каждой итерацией
            for poly_idx in ngon_list:
                poly_selection.Select(poly_idx) # Выделяем все треугольники, которые нужно объединить в N-гон
                
            # Execute Melt command on the current selection
            utils.SendModelingCommand(
                command=c4d.MCOMMAND_MELT,
                list=[obj],
                mode=c4d.MODELINGCOMMANDMODE_POLYGONSELECTION,
                doc=doc
            )
            
        poly_selection.DeselectAll() # Снимаем выделение после всех итераций, чтобы очистить подсветку

def import_geo():
    # Парсим txt-файл и получаем имя, точки и полигоны
    name, points, faces = parse_txt_file(file_path)
    
    # Считаем количество полигонов (включая разбитые n-гоны)
    total_faces = 0
    for face in faces:
        if len(face) <= 4:
            total_faces += 1 # Если треугольник или четырехугольник, то добавляем 1 полигон
        else:
            total_faces += (len(face) - 2) # Если N-гон, то добавляем (N-2) полигона

    # Создаем новый объект и задаем ему имя
    obj = c4d.PolygonObject(pcnt=len(points), vcnt=total_faces)
    obj.SetName(name)

    # Создаем точки
    for i, pt in enumerate(points):
        vec = c4d.Vector(pt[0], pt[1], -pt[2])
        obj.SetPoint(i, vec)

    # Step 2: Build the internal polygon structures and track N-gon mappings
    c4d_polys = []
    ##ngon_translations = [] # Stores lists of triangle IDs that need to be melted together
    
    internal_poly_idx = 0
    for face in faces:
        sides = len(face)
        
        if sides == 3: # Если треугольник, просто добавляем его
            c4d_polys.append(c4d.CPolygon(face[0], face[1], face[2]))
            internal_poly_idx += 1
        
        elif sides == 4: # Если четырехугольник, просто добавляем его
            c4d_polys.append(c4d.CPolygon(face[0], face[1], face[2], face[3]))
            internal_poly_idx += 1
        
        else: # Если N-гон, разбиваем его на треугольники и сохраняем их индексы для последующего объединения
            start_idx = face[0]
            ngons = []
            
            for i in range(1, sides - 1):
                c4d_polys.append(c4d.CPolygon(start_idx, face[i], face[i+1]))
                ngons.append(internal_poly_idx)
                internal_poly_idx += 1
                
            ##ngon_translations.append(ngons)
            
    # Write the polygons to the object
    for idx, poly in enumerate(c4d_polys):
        obj.SetPolygon(idx, poly)
        
    obj.Message(c4d.MSG_UPDATE)
    doc.InsertObject(obj)

    ##melt_ngons(obj, ngon_translations)

def export_geo():
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
file_path = tempfile.gettempdir() + os.sep + "lk_Import-Export.txt"
if len(sel) == 0:
    import_geo()

elif len(sel) == 1:
    export_geo()

else:
    c4d.gui.MessageDialog("Please select only one object")

c4d.EventAdd() # Обновляем вьюпорт