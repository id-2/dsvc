""" The module to visualize/report the results of CAD file analyses"""
from typing import Dict, List, Union
from xml.etree import ElementTree as ET

from pandas.plotting import table
import matplotlib.pyplot as plt


from dsvc.cad_parser_xml import CADFeatures, FeatureDifferences

# Define data classes or necessary functions
def is_number(s: str) -> bool:
    try:
        float(s)
        return True
    except ValueError:
        return False

def pretty_print_features(features: CADFeatures) -> None:
    for feature_name, instances in features.items():
        print(f"Feature: {feature_name}")
        for index, instance in enumerate(instances, start=1):
            print(f"  Instance {index}:")
            for attr, value in instance.items():
                if isinstance(value, dict):  # Check if value is a Point-like dictionary
                    formatted_value = f"({value['x']}, {value['y']}, {value['z']})"
                else:
                    formatted_value = value
                print(f"    {attr}: {formatted_value}")
        print("\n")

#====================================================================================================
def dataframe_to_image(df, title_fontsize=14, title_color='black', title_bgcolor='lightgray',
                       row_fontsize=12, row_color='black', row_bgcolor='white',
                       text_margin=10, save_path='output.jpg'):
    """
    Render a pandas DataFrame to a JPG image with customizable options and dynamic cell sizing.

    Args:
    df (DataFrame): The pandas DataFrame to render.
    title_fontsize (int): Font size of the DataFrame's column names.
    title_color (str): Color of the font for the DataFrame's column names.
    title_bgcolor (str): Background color for the DataFrame's column names.
    row_fontsize (int): Font size of the DataFrame's rows.
    row_color (str): Color of the font for the DataFrame's rows.
    row_bgcolor (str): Background color for the DataFrame's rows.
    text_margin (int): Extra space in pixels added around the longest text in each cell.
    save_path (str): Path to save the image file.
    """
    # Calculate max text length in each column and set column width
    col_widths = {col: max(df[col].astype(str).apply(lambda x: len(x))) + text_margin for col in df.columns}

    # Estimate figure size based on text length
    fig_width = sum(col_widths.values()) / 5  # Assuming avg character width can be approximated
    fig_height = len(df) + 2  # dynamic height based on the number of rows
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    ax.axis('tight')
    ax.axis('off')

    the_table = table(ax, df, loc='center', cellLoc='center', colWidths=[w / 100 for w in col_widths.values()])

    # Customize the font and background colors for the title row and data rows
    for (i, key), cell in the_table.get_celld().items():
        if i == 0:
            cell.set_fontsize(title_fontsize)
            cell.set_text_props(color=title_color)
            cell.set_facecolor(title_bgcolor)
        else:
            cell.set_fontsize(row_fontsize)
            cell.set_text_props(color=row_color)
            cell.set_facecolor(row_bgcolor)

    plt.savefig(save_path, dpi=300)  # Save as high resolution image
    plt.close()

def print_differences(differences: FeatureDifferences) -> None:
    """
    Prints the differences between two CAD feature sets in a human-readable format.

    Args:
        differences (dict): The dictionary containing 'additions', 'modifications', and 'removals' keys.
                            Each key maps to a dictionary that holds the details of the differences.
    """
    def print_heading(text: str):
        print("\n" + "=" * len(text))
        print(text)
        print("=" * len(text))

    def print_subheading(text: str):
        print("\n" + "-" * len(text))
        print(text)
        print("-" * len(text))

    # Additions
    additions = differences.get('additions', {})
    if additions:
        print_heading("Additions")
        for feature, instances in additions.items():
            print_subheading(f"Feature: {feature}")
            for instance in instances:
                print(f"- Name: {instance.get('Name', 'Unknown')}")
                for field, value in instance.items():
                    if field != 'Name':
                        print(f"  {field}: {value}")
            print("\n")
    else:
        print_heading("No Additions")

    # Modifications
    modifications = differences.get('modifications', {})
    if modifications:
        print_heading("Modifications")
        for feature, instances in modifications.items():
            print_subheading(f"Feature: {feature}")
            for instance in instances:
                print(f"- Name: {instance['name']}")
                for field, changes in instance['fields'].items():
                    print(f"  {field}:")
                    print(f"    Old: {changes['old']}")
                    print(f"    New: {changes['new']}")
            print("\n")
    else:
        print_heading("No Modifications")

    # Removals
    removals = differences.get('removals', {})
    if removals:
        print_heading("Removals")
        for feature, instances in removals.items():
            print_subheading(f"Feature: {feature}")
            for instance in instances:
                print(f"- Name: {instance.get('Name', 'Unknown')}")
                for field, value in instance.items():
                    if field != 'Name':
                        print(f"  {field}: {value}")
            print("\n")
    else:
        print_heading("No Removals")
