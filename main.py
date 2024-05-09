import pandas as pd
import json

import dsvc.cad_parser_xml as cad
import dsvc.cam_parser_xml as cam
import dsvc.cam_vis as cam_vis 
import dsvc.cam_gen_xml as cam_gen

from dsvc.cad_vis import (
    pretty_print_features,  
    print_differences
    #dataframe_to_image,
    #render_mpl_table
)

def main():
    blank_file_path = 'data/Blank-0001.xml'
    component_file_path = 'data/Component-0001.xml'
    cam_file_path = 'data/Machine-0001.xml'

    blank_root = cad.parse_xml_file(blank_file_path)
    component_root = cad.parse_xml_file(component_file_path)

    blank_features: cad.CADFeatures = cad.extract_features(blank_root)
    component_features: cad.CADFeatures = cad.extract_features(component_root)

    print("="*80)
    print("Blank Features:")
    print("="*80)
    #print(json.dumps(blank_features, indent=2))
    pretty_print_features(blank_features)

    print("="*80)
    print("Component Features:")
    print("="*80)
    # print(json.dumps(component_features, indent=2))
    pretty_print_features(component_features)
    

    blank_df : pd.DataFrame = cad.features_dict_to_dataframe(blank_features)
    print("="*80)
    print("Blank dataFrame:")
    print("="*80)
    print(blank_df)


    component_df : pd.DataFrame = cad.features_dict_to_dataframe(component_features)
    print("="*80)
    print("Component dataFrame:")
    print("="*80)
    print(component_df)
    
    #dataframe_to_pdf(df)

    #render_dataframe_to_image(df, save_path="dataframe_report.jpg")


    # dataframe_to_image(df, title_fontsize=20, title_color='white', title_bgcolor='lightblue',
    #                row_fontsize=18, row_color='black', row_bgcolor='white', 
    #                save_path='dataframe_report.jpg')
    
    #fig,ax = render_mpl_table(df, header_columns=0)
    #fig.savefig("table_mpl.png")
    
    
    # Comparing features
    differences = cad.compare_features(blank_features, component_features)
    print("="*80)
    print("Component dataFrame:")
    print("Differences:")
    print("="*80)
    #print(json.dumps(differences, indent=2))
    print_differences(differences)
    
    cam_operations: cam.CAMOperations = cam.parse_cam_xml(cam_file_path)
    #print(json.dumps(cam_features, indent=2))
    cam.print_cam_operations(cam_operations)


    print("*"*80)
    print("Required CNC tools")
    print("*"*80)
    tools: cam.ToolsDict = cam.required_tools(cam_operations)
    cam_vis.print_tools_dict(tools)
    #print(json.dumps(tools, indent=2))

    """*****************************************************************************
    Working on CAM regeneration: First, constructing relaitnal tables
    ********************************************************************************"""
    # Example usage:
    # Assuming `operations` is a parsed CAMOperations dictionary:
    #mapping_csv_path = '/Users/mehdi/data/research/projects/dsvc/table_geometry_to_operation_map.csv'
    mapping_csv_path = 'data/table_geometry_to_operation_map.csv'
    cam.extract_geometry_to_operation_mapping_from_dict(cam_operations, mapping_csv_path)
    # Example usage to read the mapping back into a Python structure
    geometry_to_operations = cam.read_geometry_to_operation_mapping(mapping_csv_path)
    print(json.dumps(geometry_to_operations, indent=2))
    
    """


    """
    #cam_gen.regenerate_cam_xml(differences, tools, 'Machine-001-ReGen.xml')

if __name__ == "__main__":
    main()
