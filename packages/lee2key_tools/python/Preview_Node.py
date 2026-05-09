import hou
def execute():
    selected_nodes = hou.selectedNodes()

    # Check if node is selected
    if selected_nodes:
        # Get the first selected node if there are many
        node = selected_nodes[0]

        # Check if the selected node is a VOP node
        if node.type().category().name() != 'Vop':
            hou.ui.displayMessage("Preview node tool works only in 'Material network' with Redshift nodes", title="lee2key_tools")
            return

        # Get the count of outputs on the selected node
        output_count = len(node.outputConnectors())

        # Find the redshift_material node
        redshift_material_node = None
        for i in node.parent().children():
            if i.type().name() == "redshift_material":
                redshift_material_node = i
                break

        # If redshift_material node is not found, print an error and return
        if not redshift_material_node:
            hou.ui.displayMessage("'Redshift Material' output node is not found", title="lee2key_tools")
            return

        # Check if the selected node is already connected to the redshift_material node
        is_connected = False
        for input in redshift_material_node.inputs():
            if input == node:
                is_connected = True
                break

        if is_connected:
            # Find connections to Redshift Output node
            connections = []
            outputs = node.outputConnectors()
            outputs_count = len(node.outputConnectors())

            for output_index, connector in enumerate(outputs):
                # For each output connector, check all connected nodes
                for connection in connector:
                    connected_node = connection.outputNode()
                    if connected_node.type().name() == "redshift_material":
                        connections.append((output_index, connected_node.path()))

            if connections[0][0] == outputs_count - 1:
                standard_material_node = None
                for i in node.parent().children():
                    if i.type().name() == "redshift::StandardMaterial":
                        standard_material_node = i
                        break
                redshift_material_node.setInput(0, standard_material_node, 0)

            else:
                redshift_material_node.setInput(0, node, connections[0][0] + 1)

        else:
            redshift_material_node.setInput(0, node, 0)