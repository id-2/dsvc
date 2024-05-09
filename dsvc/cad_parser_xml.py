from xml.etree import ElementTree as ET
import pandas as pd

# Define a type alias using the built-in types
CADFeatures       = dict[str, list[dict[str, any]]]
FeatureDifferences = dict[str, dict[str, any]]

                         
def is_number(s):
    try:
        float(s)  # for int, float, etc.
        return True
    except ValueError:
        return False

def is_point(text: str) -> bool:
    parts = text.split()
    return len(parts) == 3 and all(is_number(part) for part in parts)

def parse_point(text: str) -> dict[str, float]:
    parts = text.split()
    return {'x': float(parts[0]), 'y': float(parts[1]), 'z': float(parts[2])}


def parse_xml_file(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    return root

def extract_features(root: ET.Element) -> CADFeatures:
    """
    Extracts features from an XML element, parsing and storing each feature's attributes.

    This function traverses through each child element of the provided XML root, extracting and
    parsing all sub-children attributes. Numeric values are converted to floats, coordinates in the
    format "x y z" are parsed into dictionaries, and other textual data is stored as strings.
    Each feature (child) is stored in a list under its tag name in the resulting dictionary.

    Args:
        root (ET.Element): The root XML element from which to start extracting features. This
                           element should contain child elements that represent individual features
                           with their respective attributes as sub-elements.

    Returns:
        dict[str, list[dict[str, any]]]: A dictionary where each key is a feature tag name from the
                                        XML and the value is a list of dictionaries. Each dictionary
                                        in the list corresponds to an instance of the feature, with
                                        keys as the attribute names and values as the parsed attribute
                                        data. Values can be of type float (for numeric attributes),
                                        dict (for point coordinates), or str (for other attributes).

    Examples:
        Given an XML element structure:
        <Component>
            <OUTER_DIAMETER>
                <Name>OUTER_DIAMETER(1of1){1of1}</Name>
                <Origin>0 0 0</Origin>
                <Vector>0 0 1</Vector>
            </OUTER_DIAMETER>
            <HOLES_ALONG_SURFACE>
                <Name>HOLES_ALONG_SURFACE(1of1){2of6}</Name>
                <Origin>119.55 69.0222 -32</Origin>
                <Diameter>3</Diameter>
            </HOLES_ALONG_SURFACE>
        </Component>

        The function would return:
        {
            'OUTER_DIAMETER': [{'Name': 'OUTER_DIAMETER(1of1){1of1}', 'Origin': {'x': 0, 'y': 0, 'z': 0}, 'Vector': {'x': 0, 'y': 0, 'z': 1}}],
            'HOLES_ALONG_SURFACE': [{'Name': 'HOLES_ALONG_SURFACE(1of1){2of6}', 'Origin': {'x': 119.55, 'y': 69.0222, 'z': -32}, 'Diameter': 3.0}]
        }
    """
    features = {}
    for child in root:
        feature_details = {}
        for sub_child in child:
            sub_child_text = sub_child.text.strip()
            # Check if the sub_child text is a number and convert if so
            if is_number(sub_child_text):
                feature_details[sub_child.tag] = float(sub_child_text)
            elif is_point(sub_child_text):
                feature_details[sub_child.tag] = parse_point(sub_child_text)
            else:
                feature_details[sub_child.tag] = sub_child_text
        if child.tag not in features:
            features[child.tag] = []
        features[child.tag].append(feature_details)
    return features


def features_dict_to_dataframe(features: CADFeatures) -> pd.DataFrame:
    """
    Converts a FeaturesDict to a pandas DataFrame.

    Each key in the FeaturesDict represents a feature type, and each list item under a key contains
    dictionaries of feature attributes. This function flattens the structure into a DataFrame where
    each row corresponds to a feature instance, including a new column for the feature type.

    Args:
        features (FeaturesDict): The dictionary containing feature data with multiple attributes.

    Returns:
        pd.DataFrame: A DataFrame where each row is a feature instance with columns for each attribute
                      and a column named 'FeatureType' indicating the type of feature.

    Example:
        Input FeaturesDict:
        {
            'OUTER_DIAMETER': [{'Name': 'OD1', 'Diameter': 10.0}],
            'HOLES_ALONG_SURFACE': [{'Name': 'Hole1', 'Diameter': 5.0, 'Depth': 2.0}]
        }

        Output DataFrame:
             FeatureType      Name  Diameter  Depth
        0  OUTER_DIAMETER       OD1      10.0    NaN
        1  HOLES_ALONG_SURFACE  Hole1      5.0    2.0
    """
    rows = []
    for feature_type, instances in features.items():
        for instance in instances:
            row = {'FeatureType': feature_type, **instance}
            rows.append(row)
    df = pd.DataFrame(rows)
    return df

# Example use
features_dict = {
    'OUTER_DIAMETER': [{'Name': 'OD1', 'Diameter': 10.0}],
    'HOLES_ALONG_SURFACE': [{'Name': 'Hole1', 'Diameter': 5.0, 'Depth': 2.0}]
}

def compare_features(cad1: CADFeatures, cad2: CADFeatures) -> FeatureDifferences:
    """
    Compares two sets of CAD features and identifies modifications, additions, and removals.

    Args:
        cad1 (FeaturesDict): The features extracted from the first CAD file (typically the initial blank).
        cad2 (FeaturesDict): The features extracted from the second CAD file (typically the final component).

    Returns:
        dict: A dictionary containing 'additions', 'modifications', and 'removals' keys, each pointing
              to a dictionary of differences. 'modifications' will include both old and new attributes
              for each changed field.
    """
    modifications = {
        'additions': {},
        'modifications': {},
        'removals': {}
    }

    # Check for additions and modifications
    for feature, cad2_details in cad2.items():
        if feature not in cad1:
            modifications['additions'][feature] = cad2_details
        else:
            cad2_list = cad2[feature]
            cad1_list = cad1.get(feature, [])
            feature_modifications = []
            for cad2_detail, cad1_detail in zip(cad2_list, cad1_list):
                changed_fields = {}
                for key, value in cad2_detail.items():
                    if key not in cad1_detail or cad1_detail[key] != value:
                        changed_fields[key] = {'old': cad1_detail.get(key, 'N/A'), 'new': value}
                if changed_fields:
                    feature_modifications.append({
                        'name': cad2_detail.get('Name', 'Unknown'),
                        'fields': changed_fields
                    })
            if feature_modifications:
                modifications['modifications'][feature] = feature_modifications

            # Additional instances present in cad2 that weren't in cad1
            if len(cad2_list) > len(cad1_list):
                modifications['additions'][feature] = cad2_list[len(cad1_list):]

    # Check for removals
    for feature, cad1_details in cad1.items():
        if feature not in cad2:
            modifications['removals'][feature] = cad1_details
        else:
            cad1_list = cad1[feature]
            cad2_list = cad2.get(feature, [])
            if len(cad1_list) > len(cad2_list):
                modifications['removals'][feature] = cad1_list[len(cad2_list):]

    return modifications