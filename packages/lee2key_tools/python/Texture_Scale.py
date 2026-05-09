import hou
def execute():
    # Get selected nodes
    selected_nodes = hou.selectedNodes()

    # Get the opened context we are at
    context = selected_nodes[0].parent()

    # Create RS Abs node
    rs_abs = context.createNode("redshift::RSMathAbs", "Scale_Textures")
    
    # Set default scale value to 1
    rs_abs.parm("input").set(1)

    # Set position of the node under cursor
    network = hou.ui.curDesktop().paneTabOfType(hou.paneTabType.NetworkEditor)
    cursor_position = network.cursorPosition()
    cursor_position[0] -= 0.5
    rs_abs.setPosition(cursor_position)

    # Connect RS Abs to all selected texture nodes
    i = 0
    for node in selected_nodes:
        selected_nodes[i].setInput(0, rs_abs)
        i += 1