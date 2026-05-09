import hou
def execute():
    # Get context where we are now
    network = hou.ui.curDesktop().paneTabOfType(hou.paneTabType.NetworkEditor)
    current_node_path = network.pwd().path()
    context = hou.node(current_node_path)
    

    # Open input dialog for naming Null
    mat_name = hou.ui.readInput("Enter name",
                                buttons=("OK", "Cancel"),
                                default_choice=0,
                                close_choice=1,
                                title="New Material",
                                initial_contents="Mat_1")[1]
    mat_name = mat_name.replace(" ", "_")

    rs_mat = context.createNode("redshift_vopnet", mat_name)
    cursor_position = network.cursorPosition()
    cursor_position[0] -= 0.5
    rs_mat.setPosition(cursor_position)