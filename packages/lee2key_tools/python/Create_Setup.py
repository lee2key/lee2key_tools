import hou
def execute():
    # Create Camera node
    node = hou.node("/obj").createNode("cam", "Camera")
    node.parm("tz").set(2)
    node.setPosition([0,0])
    
    # Create RS Dome Light node
    node = hou.node("/obj").createNode("rslightdome", "Dome_Light")
    node.setPosition([0,-1])
    node.setDisplayFlag(False)

    # Create Material Network node
    node = hou.node("/obj").createNode("matnet", "Materials")
    node.setPosition([0,-2])

    # Create ROP Network node
    node = hou.node("/obj").createNode("ropnet", "Render")
    node.setPosition([0,-3])

    # Create Redshift_ROP node
    node = hou.node("/obj/Render").createNode("Redshift_ROP", "Redshift")
    node.parm("RS_renderCamera").set("/obj/Camera")
    node.parm("RS_outputFileNamePrefix").set("$HIP/export/$HIPNAME.$F.exr")
    node.parm("RS_outputExrCompression").set("dwaa")
    node.parm("RS_easyThreshold").set(0.1)
    node.parm("UnifiedAdaptiveErrorThreshold").set(0.1)
    #node.parm("SecondaryGIEngine2").set("RS_GIENGINE_BRUTE_FORCE")
    node.parm("BlockSize").set(3)