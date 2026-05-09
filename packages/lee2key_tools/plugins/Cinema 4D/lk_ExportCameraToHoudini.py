import c4d, tempfile, os

# Get active document
doc = c4d.documents.GetActiveDocument()

# Check if there's a selected object
selected_objects = doc.GetActiveObjects(c4d.GETACTIVEOBJECTFLAGS_SELECTIONORDER)

# Get scene resolution
width = int(doc.GetActiveRenderData()[c4d.RDATA_XRES])
height = int(doc.GetActiveRenderData()[c4d.RDATA_YRES])
object_name = "camera_" + str(width) + "_" + str(height) + ".fbx"

# Get Windows temp directory
temp_dir = tempfile.gettempdir()

# Generate a unique filename using standard Python time module
export_filename = os.path.join(temp_dir, object_name)

# Create a document with just the selected objects
temp_doc = c4d.documents.BaseDocument()

# Clone the selected objects and add them to the temp document
for obj in selected_objects:
    clone = obj.GetClone()
    temp_doc.InsertObject(clone)

# Use the correct FBX export plugin ID
plug_id = 1026370  # FBX export plugin ID

c4d.documents.SaveDocument(temp_doc, export_filename, c4d.SAVEDOCUMENTFLAGS_DONTADDTORECENTLIST, plug_id)