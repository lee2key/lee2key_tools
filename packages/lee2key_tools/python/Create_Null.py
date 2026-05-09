import hou
def execute():
    # Get selection
    sel = hou.selectedNodes()

    # Set name for the Null
    name = hou.ui.readInput("Enter name",
                            buttons=("OK", "Cancel"),
                            default_choice=0,
                            close_choice=1,
                            title="Create Null",
                            initial_contents="OUT")[1].replace(" ", "_")

    # Get parent context
    if sel:
        parent = sel[0].parent()
    else:
        parent = hou.ui.curDesktop().paneTabOfType(hou.paneTabType.NetworkEditor).pwd()

    null_node = parent.createNode("null", name) # Create Null node

    # If something is selected
    if sel:
        sel = sel[0]
        parent = sel.parent()
        mypos = sel.position()
        mypos[1] -= 1 # Move down one unit

        null_node.setPosition(mypos) # Set position for node

        # Create connection
        try:
            null_node.setInput(0, sel)
        except:
            pass

        null_node.setDisplayFlag(True)
        if isinstance(sel, hou.SopNode):
            null_node.setRenderFlag(True)

    else:
        null_node.moveToGoodPosition()

    # Select the Null
    hou.clearAllSelected()
    null_node.setSelected(True)