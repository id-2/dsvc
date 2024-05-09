""" The module to visualize/report the results of CAM file analyses"""
import dsvc.cam_parser_xml as cam_parser

def print_tools_dict(tools:  cam_parser.ToolsDict) -> None:
    """
    Print the tools information in a well-formatted and human-readable fashion.

    Args:
        tools (ToolsDict): A dictionary of tools, where each key is a tool type, and each value is
                           another dictionary mapping each tool name to its details and a list of operations
                           using that tool.
    # Example usage:
        # Assuming `tools_dict` is the result from `required_tools` function:
        # tools_dict = required_tools(operations)
        # print_tools_dict(tools_dict)
    """
    for tool_type, tool_map in tools.items():
        print(f"Tool Type: {tool_type}")
        for tool_name, tool_info in tool_map.items():
            tool_details = tool_info['ToolDetails']
            operations_list = tool_info['OperationsList']
            
            print(f"  Tool Name: {tool_name}")
            for detail, value in tool_details.items():
                print(f"    {detail}: {value}")
            
            print(f"  Used In Operations: {', '.join(operations_list)}")
            print()  # Blank line between tools
        print('-' * 40)  # Separator between tool types

