import xml.etree.ElementTree as ET


FeatureDifferences = dict[str, dict[str, any]]
ToolsDict = dict[str, dict[str, any]]

# Lookup Tables
feature_to_operation = {
    'FACE': 'ROUGH_FACE',
    'TURN': 'ROUGH_TURN_OD',
    # Add more mappings as needed
}

operation_to_tool_type = {
    'ROUGH_FACE': 'TurningToolStandard',
    'ROUGH_TURN_OD': 'TurningToolStandard',
    # Add more mappings as needed
}

def find_tool_for_operation(tool_type: str, tools: ToolsDict) -> dict[str, any]:
    """
    Find the first available tool matching the specified type.

    Args:
        tool_type (str): Type of the tool to search for.
        tools (ToolsDict): Dictionary containing available tools.

    Returns:
        dict: Tool details for the matching tool type, or an empty dict if not found.
    """
    return next((tool_info for tool_info in tools.get(tool_type, {}).values()), {})

def regenerate_cam_xml(feature_differences: FeatureDifferences, tools: ToolsDict, output_path: str) -> None:
    """
    Regenerate the CAM XML file based on feature differences and available tools using a systematic approach.

    Args:
        feature_differences (FeatureDifferences): Differences between the blank and final CAD files.
        tools (ToolsDict): Dictionary containing the available tools and their usage information.
        output_path (str): Path to the output XML file.
    """
    # Root element for the new CAM XML
    root = ET.Element('ARTC_CAMOperationCollection')

    # Generate operations based on feature differences
    for feature, diff_details in feature_differences.get('modifications', {}).items():
        operation_name = feature_to_operation.get(feature, 'UNKNOWN_OPERATION')
        operation_element = ET.SubElement(root, operation_name)

        # Add geometry information if applicable (example placeholder)
        ET.SubElement(operation_element, 'Geometry').text = f"{feature} Feature Geometry"

        # Find the appropriate tool type for this operation
        tool_type = operation_to_tool_type.get(operation_name)
        if tool_type:
            tool_info = find_tool_for_operation(tool_type, tools)
            if tool_info:
                tool_element = ET.SubElement(operation_element, tool_type)
                for attr, value in tool_info['ToolDetails'].items():
                    ET.SubElement(tool_element, attr).text = str(value)

        # Example operation-specific data (replace with actual values)
        ET.SubElement(operation_element, 'Step').text = "1.25"
        ET.SubElement(operation_element, 'SurfaceSpeed').text = "200"
        ET.SubElement(operation_element, 'FeedRate').text = "0.2"
        ET.SubElement(operation_element, 'Stock').text = "0.25"

    # Write the output XML to file
    tree = ET.ElementTree(root)
    tree.write(output_path, encoding='utf-8', xml_declaration=True)