import hou
def execute():
    # Get the node from clipboard
    clipboard_path = hou.ui.getTextFromClipboard()

    # Get context where we are now
    network = hou.ui.curDesktop().paneTabOfType(hou.paneTabType.NetworkEditor)
    current_node_path = network.pwd().path()
    parent_node = hou.node(current_node_path)

    # Create Object Merge node
    objmerge = parent_node.createNode("object_merge", "Merge")

    # Position the node
    cursor_position = network.cursorPosition()
    cursor_position[0] -= 0.5
    objmerge.setPosition(cursor_position)

    # Set path to the node from clipboard
    objmerge.parm("objpath1").set(clipboard_path)