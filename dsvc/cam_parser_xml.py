from xml.etree import ElementTree as ET
from collections import defaultdict
import csv

# The folowing list could be relpaced by a data file/table/database:
TOOLSTYPELIST = ["TurningToolStandard", "Drill", "SpotDrill"]  

# Type aliases for clarity
CAMOperations = dict[str, list[dict[str, any]]]
ToolsDict = dict[str, dict[str, any]]
             
def parse_xml_file(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    return root

def parse_cam_xml(file_path: str) -> CAMOperations:
    '''
    Parse the CAM XML file and extract all machining operations.

    Args:
        file_path (str): Path to the XML file containing CAM instructions.

    Returns:
        CAMOperations: Dictionary where each key is an operation type and each value is a list of dictionaries
                       containing attributes of that particular machining operation, including tool information.
    '''
    root = parse_xml_file(file_path)

    operations = {}
    # Traverse all direct children of the root element
    for operation in root:
        operation_type = operation.tag
        operation_details = {}

        # Iterate through each sub-element within the operation and collect its attributes
        for attribute in operation:
            if attribute.tag in TOOLSTYPELIST:  
                # Extract tool information for each specified tool type
                tool_info = {}
                for tool_attr in attribute:
                    tool_info[tool_attr.tag] = tool_attr.text.strip()
                operation_details[attribute.tag] = tool_info
            else:
                attribute_text = attribute.text.strip()
                if attribute.tag in ('Step', 'SurfaceSpeed', 'FeedRate', 'Stock', 'NoseRadius'):
                    operation_details[attribute.tag] = float(attribute_text)
                else:
                    operation_details[attribute.tag] = attribute_text

        # Append the parsed operation details to the appropriate type in the dictionary
        if operation_type not in operations:
            operations[operation_type] = []
        operations[operation_type].append(operation_details)

    return operations

def print_cam_operations(operations: CAMOperations) -> None:
    """
    Prints a list of CAM operations in a readable format.

    Args:
        operations (dict[str, list[dict[str, any]]]): A dictionary containing CAM operations extracted from an XML file.
            Each key represents the operation type, and each value is a list of dictionaries with operation attributes.
    """
    def print_heading(text: str):
        print("\n" + "=" * len(text))
        print(text)
        print("=" * len(text))

    def print_subheading(text: str):
        print("\n" + "-" * len(text))
        print(text)
        print("-" * len(text))

    # Print each operation type
    for operation_type, instances in operations.items():
        print_heading(f"Operation Type: {operation_type}")
        for index, instance in enumerate(instances, start=1):
            print_subheading(f"Instance {index}:")
            for attribute, value in instance.items():
                print(f"  {attribute}: {value}")


def required_tools(operations: CAMOperations) -> ToolsDict:
    """
    Analyze the CAM operations and identify the required tools.

    Args:
        operations (CAMOperations): Dictionary containing machining operations and their details.

    Returns:
        Dict[str, Dict[str, Any]]: Dictionary where each key is a tool type, and each value is another
                                   dictionary mapping each tool name to its details and a list of operations
                                   using that tool.
    """
    tools_usage = {tool_type: defaultdict(lambda: {"ToolDetails": {}, "OperationsList": []}) for tool_type in TOOLSTYPELIST}

    for operation_type, op_list in operations.items():
        for op in op_list:
            for tool_type in TOOLSTYPELIST:
                if tool_type in op:
                    tool_info = op[tool_type]
                    tool_name = tool_info["Name"]  # Assuming every tool has a unique "Name" attribute
                    tools_usage[tool_type][tool_name]["ToolDetails"] = tool_info
                    tools_usage[tool_type][tool_name]["OperationsList"].append(operation_type)

    # Convert defaultdicts to regular dicts for better readability and handling
    return {tool_type: dict(tool_map) for tool_type, tool_map in tools_usage.items()}


def extract_geometry_to_operation_mapping_from_dict(operations: CAMOperations, output_csv_path: str) -> None:
    """
    Extract geometry to operation mapping from a parsed CAM operations dictionary and save to a CSV file.

    Args:
        operations (CAMOperations): Parsed dictionary containing machining operations and their details.
        output_csv_path (str): Path to the output CSV file containing the mappings.
    """
    mappings = []
    for operation_name, op_list in operations.items():
        for op in op_list:
            geometry = op.get('Geometry', None)
            if geometry is not None:
                mappings.append({'Geometry': geometry, 'Operation': operation_name})
    
    # Write mappings to CSV
    with open(output_csv_path, mode='w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Geometry', 'Operation']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for mapping in mappings:
            writer.writerow(mapping)
    
def read_geometry_to_operation_mapping(csv_path: str) -> dict[str, list[str]]:
    """
    Read the geometry to operation mapping from a CSV file.

    Args:
        csv_path (str): Path to the CSV file containing the mappings.

    Returns:
        Dict[str, List[str]]: A dictionary where each key is a geometry, and each value is a list of associated operations.
    """
    geometry_to_operations = {}
    
    with open(csv_path, mode='r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            geometry = row['Geometry']
            operation = row['Operation']
            if geometry not in geometry_to_operations:
                geometry_to_operations[geometry] = []
            geometry_to_operations[geometry].append(operation)
    
    return geometry_to_operations

