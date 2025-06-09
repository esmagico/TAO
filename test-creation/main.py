import pandas as pd
from lxml import etree
from zipfile import ZipFile
import os
import shutil
import sys
import re

# --- QTI 2.1 XML Generation Functions ---

def sanitize_identifier(name):
    """Sanitizes a string to be a valid QTI identifier."""
    # Convert to string first
    name_str = str(name)
    # Replace non-alphanumeric characters (except underscore and hyphen) with underscore
    s = re.sub(r'[^\w-]', '_', name_str)
    # Ensure it doesn't start with a number or hyphen (QTI identifier rules)
    if s and (s[0].isdigit() or s[0] == '-'):
         s = '_' + s
    # Ensure it's not empty or just underscores/hyphens after cleaning
    s = s.strip('_').strip('-')
    if not s:
        s = "unspecified_id" + re.sub(r'[^\w]', '', name_str) # Add some cleaned characters from original if possible
        if not s or s == "unspecified_id":
             s = "unspecified_id" + str(abs(hash(name_str))) # Fallback to hash if still empty
        s = s[:64] # Limit length to avoid issues with file paths etc.
    return s


def create_qti_item_xml(item_identifier, item_title, item_stimulus, question_text, options, correct_answer_id):
    """
    Creates a QTI 2.1 assessmentItem XML element.

    Args:
        item_identifier (str): Unique identifier for the item.
        item_title (str): Title for the item.
        item_stimulus (str): Optional introductory text/stimulus for the question.
        question_text (str): The main question stem.
        options (list of tuple): List of (option_id, option_text) for choice interaction.
        correct_answer_id (str): The identifier of the correct option.
    Returns:
        etree.Element: The assessmentItem XML element.
    """
    # QTI 2.1 Namespaces
    nsmap = {
        None: "http://www.imsglobal.org/xsd/imsqti_v2p1",
        'xsi': "http://www.w3.org/2001/XMLSchema-instance"
    }

    assessmentItem = etree.Element(
        "assessmentItem",
        identifier=item_identifier,
        title=item_title,
        adaptive="false",
        timeDependent="false",
        nsmap=nsmap,
        attrib={
            "{http://www.w3.org/2001/XMLSchema-instance}schemaLocation":
            "http://www.imsglobal.org/xsd/imsqti_v2p1 http://www.imsglobal.org/xsd/qti/qtiv2p1/imsqti_v2p1p1.xsd"
        }
    )

    # --- responseDeclaration ---
    responseDeclaration = etree.SubElement(
        assessmentItem,
        "responseDeclaration",
        identifier="RESPONSE",
        baseType="identifier",
        cardinality="single"
    )
    correctResponse = etree.SubElement(responseDeclaration, "correctResponse")
    value = etree.SubElement(correctResponse, "value")
    value.text = correct_answer_id

    # --- outcomeDeclaration ---
    # Item outcome for score - typically float max 1 for correct answer
    outcomeDeclaration_score = etree.SubElement(
        assessmentItem,
        "outcomeDeclaration",
        identifier="SCORE",
        cardinality="single",
        baseType="float",
        normalMaximum="1",
        normalMinimum="0"
    )
    defaultValue_score = etree.SubElement(outcomeDeclaration_score, "defaultValue")
    value_score = etree.SubElement(defaultValue_score, "value")
    value_score.text = "0"

    # --- itemBody ---
    itemBody = etree.SubElement(assessmentItem, "itemBody")
    
    # Add Item Stimulus if present and not empty/N/A
    if item_stimulus and str(item_stimulus).strip().lower() not in ["n/a", ""]:
        # Use <p> for stimulus.
        p_stimulus = etree.SubElement(itemBody, "p")
        # Basic HTML escaping might be needed if stimulus contains XML special chars
        p_stimulus.text = str(item_stimulus).strip()

    # Prompt for the question (Item Stem)
    p_prompt = etree.SubElement(itemBody, "p")
    # Basic HTML escaping might be needed if stem contains XML special chars
    p_prompt.text = str(question_text).strip()

    # Choice Interaction
    choiceInteraction = etree.SubElement(
        itemBody,
        "choiceInteraction",
        responseIdentifier="RESPONSE",
        shuffle="false", # Or "true" if option order doesn't matter
        maxChoices="1"
    )

    for option_id, option_text in options:
        simpleChoice = etree.SubElement(
            choiceInteraction,
            "simpleChoice",
            identifier=option_id
        )
        # Basic HTML escaping might be needed for option text
        p_choice = etree.SubElement(simpleChoice, "p")
        p_choice.text = str(option_text).strip()

    # --- responseProcessing ---
    # Use a standard template for item processing
    responseProcessing = etree.SubElement(
        assessmentItem,
        "responseProcessing",
        template="http://www.imsglobal.org/question/qti_v2p1/rptemplates/match_correct"
    )

    return assessmentItem

def create_qti_test_xml(test_identifier, test_title, item_references):
    """
    Creates a QTI 2.1 assessmentTest XML element referencing multiple items.

    Args:
        test_identifier (str): Unique identifier for the test.
        test_title (str): Title of the assessment test.
        item_references (list of tuple): List of (item_identifier, item_ref_path).
    Returns:
        etree.Element: The assessmentTest XML element.
    """
    nsmap = {
        None: "http://www.imsglobal.org/xsd/imsqti_v2p1",
        'xsi': "http://www.w3.org/2001/XMLSchema-instance"
    }

    assessmentTest = etree.Element(
        "assessmentTest",
        identifier=test_identifier,
        title=test_title,
        nsmap=nsmap,
        attrib={
            "{http://www.w3.org/2001/XMLSchema-instance}schemaLocation":
            "http://www.imsglobal.org/xsd/imsqti_v2p1 http://www.imsglobal.org/xsd/qti/qtiv2p1/imsqti_v2p1p1.xsd"
        }
    )

    # Outcome Declarations (Standard QTI Test outcomes)
    # The total score outcome is necessary for the test level
    outcome_declarations = [
        ("TOTAL_SCORE", "integer", "0"),
        ("TOTAL_MAXSCORE", "float", str(len(item_references))), # Max score is sum of item max scores (1 per item)
        ("TOTAL_MINSCORE", "float", "0"),
    ]
    for identifier, baseType, defaultValue in outcome_declarations:
        outcomeDeclaration = etree.SubElement(
            assessmentTest,
            "outcomeDeclaration",
            identifier=identifier,
            cardinality="single",
            baseType=baseType
        )
        default_val_elem = etree.SubElement(outcomeDeclaration, "defaultValue")
        val_elem = etree.SubElement(default_val_elem, "value")
        val_elem.text = defaultValue

    # Test Part
    testPart = etree.SubElement(
        assessmentTest,
        "testPart",
        identifier=f"{test_identifier}-TPRT-01",
        navigationMode="linear", # Sequential navigation
        submissionMode="individual" # Items submitted individually
    )

    # Assessment Section
    assessmentSection = etree.SubElement(
        testPart,
        "assessmentSection",
        identifier=f"{test_identifier}-SEC-01",
        title=f"Questions for: {test_title}",
        visible="true",
        required="true", # Section is required
        keepTogether="false", # Items can be split across pages
        fixed="false" # Items can be reordered within the section
    )

    # --- Remove Selection and Ordering blocks entirely ---
    # This relies on the platform's default behavior to select all items
    # and present them in the order they appear in the XML.
    # This is a common and minimal approach.

    # Assessment Item References (Add a reference for each item)
    # These must be added directly under the assessmentSection when selection/ordering are omitted
    for item_identifier, item_ref_path in item_references:
        etree.SubElement(
            assessmentSection,
            "assessmentItemRef",
            identifier=item_identifier, # This is the item identifier
            href=item_ref_path,
            required="true", # Item must be included
            fixed="false" # Item position is not fixed (allows section shuffling if configured elsewhere, but likely default is order in XML)
        )

    # --- outcomeProcessing is omitted as discussed in previous fix ---
    # Relying on the QTI player's default aggregation (usually sums item scores)

    return assessmentTest


def create_imsmanifest_xml_for_test_package(
    package_identifier, test_identifier, test_filename_relative_path, item_references_for_manifest, media_files=None, css_files=None
):
    """
    Creates an imsmanifest.xml for a QTI 2.1 package that contains multiple items
    and a test that references them. The primary resource is the test.

    Args:
        package_identifier (str): The overall identifier for this package (e.g., Assessment Code).
        test_identifier (str): The identifier of the QTI Test.
        test_filename_relative_path (str): The relative path to the QTI Test XML file.
        item_references_for_manifest (list of tuple): List of (item_identifier, item_filename_relative_path).
        media_files (list): Optional list of relative paths to media files (e.g., images).
        css_files (list): Optional list of relative paths to CSS files.
    Returns:
        etree.Element: The manifest XML element.
    """
    if media_files is None:
        media_files = []
    if css_files is None:
        css_files = []

    nsmap = {
        None: "http://www.imsglobal.org/xsd/imscp_v1p1",
        'xsi': "http://www.w3.org/2001/XMLSchema-instance",
        'lom': "http://ltsc.ieee.org/xsd/LOM",
        'qtiMetadata': "http://www.imsglobal.org/xsd/imsqti_metadata_v2p1"
    }

    # Ensure paths use forward slashes for XML
    test_filename_relative_path = test_filename_relative_path.replace(os.sep, '/')
    item_references_for_manifest = [(id, path.replace(os.sep, '/')) for id, path in item_references_for_manifest]
    media_files = [path.replace(os.sep, '/') for path in media_files]
    css_files = [path.replace(os.sep, '/') for path in css_files]


    manifest = etree.Element(
        "manifest",
        identifier=f"MANIFEST-{package_identifier}",
        nsmap=nsmap,
        attrib={
            "{http://www.w3.org/2001/XMLSchema-instance}schemaLocation":
            "http://www.imsglobal.org/xsd/imscp_v1p1 http://www.imsglobal.org/xsd/qti/qtiv2p1/qtiv2p1_imscpv1p2_v1p0.xsd "
            "http://ltsc.ieee.org/xsd/LOM http://www.imsglobal.org/xsd/imsmd_loose_v1p3p2.xsd "
            "http://www.imsglobal.org/xsd/imsqti_metadata_v2p1 http://www.imsglobal.org/xsd/qti/qtiv2p1/imsqti_metadata_v2p1p1.xsd"
        }
    )

    metadata = etree.SubElement(manifest, "metadata")
    schema = etree.SubElement(metadata, "schema")
    schema.text = "QTIv2.1 Package"
    schemaversion = etree.SubElement(metadata, "schemaversion")
    schemaversion.text = "1.0.0"

    # Optional LOM metadata for the overall package
    lom = etree.SubElement(metadata, "{http://ltsc.ieee.org/xsd/LOM}lom")
    general = etree.SubElement(lom, "{http://ltsc.ieee.org/xsd/LOM}general")
    identifier_elem = etree.SubElement(general, "{http://ltsc.ieee.org/xsd/LOM}identifier")
    entry = etree.SubElement(identifier_elem, "{http://ltsc.ieee.org/xsd/LOM}entry")
    entry.text = package_identifier
    title_elem = etree.SubElement(general, "{http://ltsc.ieee.org/xsd/LOM}title")
    string_elem = etree.SubElement(title_elem, "{http://ltsc.ieee.org/xsd/LOM}string")
    string_elem.text = f"QTI 2.1 Package: {package_identifier}"

    organizations = etree.SubElement(manifest, "organizations")
    # It's good practice to declare the test as the primary organization resource
    organization = etree.SubElement(organizations, "organization", identifier=f"ORG-{package_identifier}")
    title_org = etree.SubElement(organization, "title")
    title_org.text = f"Test: {package_identifier}"
    # Add the test as an item in the organization structure
    item_org = etree.SubElement(organization, "item", identifier=f"ITEMREF-{test_identifier}", identifierref=f"RESOURCE-{test_identifier}")
    title_item_org = etree.SubElement(item_org, "title")
    title_item_org.text = f"Test: {package_identifier}"


    resources = etree.SubElement(manifest, "resources")

    # Resources for Assessment Items
    for item_identifier, item_filename_relative_path in item_references_for_manifest:
        item_resource = etree.SubElement(
            resources,
            "resource",
            type="imsqti_item_xmlv2p1",
            identifier=f"RESOURCE-{item_identifier}",
            href=item_filename_relative_path
        )
        # Add basic item metadata if available/necessary
        item_resource_metadata = etree.SubElement(item_resource, "metadata")
        qti_metadata = etree.SubElement(item_resource_metadata, "{http://www.imsglobal.org/xsd/imsqti_metadata_v2p1}qtiMetadata")
        interactionType = etree.SubElement(qti_metadata, "{http://www.imsglobal.org/xsd/imsqti_metadata_v2p1}interactionType")
        interactionType.text = "choiceInteraction" # Assuming all are choice interactions
        
        # Add the item XML file itself
        etree.SubElement(item_resource, "file", href=item_filename_relative_path)
        # Add any shared media/CSS files to item resources too (optional, depends on player)
        for media_file_path in media_files:
             etree.SubElement(item_resource, "file", href=media_file_path)
        for css_file_path in css_files:
             etree.SubElement(item_resource, "file", href=css_file_path)


    # Resource for the Assessment Test (Primary Resource for the package)
    test_resource = etree.SubElement(
        resources,
        "resource",
        type="imsqti_test_xmlv2p1",
        identifier=f"RESOURCE-{test_identifier}",
        href=test_filename_relative_path
    )
    # Add basic test metadata
    test_resource_metadata = etree.SubElement(test_resource, "metadata")
    # Can add test-specific LOM or QTI metadata here if needed

    # Add the test XML file itself
    etree.SubElement(test_resource, "file", href=test_filename_relative_path)
    
    # The test resource DEPENDS on ALL the item resources
    for item_identifier, _ in item_references_for_manifest:
        etree.SubElement(test_resource, "dependency", identifierref=f"RESOURCE-{item_identifier}")

    # Add any shared media/CSS files to the test resource too
    for media_file_path in media_files:
        etree.SubElement(test_resource, "file", href=media_file_path)
    for css_file_path in css_files:
        etree.SubElement(test_resource, "file", href=css_file_path)


    return manifest

# --- Main Package Creation Logic (Grouped by Assessment Code) ---

def create_qti_packages_by_assessment_code(input_df, output_base_dir="qti_grouped_packages_generated"):
    """
    Reads an Excel DataFrame, groups items by 'Assessment Code', and generates
    a QTI 2.1 package for each Assessment Code containing all its items and a test.
    """
    if not os.path.exists(output_base_dir):
        os.makedirs(output_base_dir)

    print(f"Generating QTI Packages Grouped by Assessment Code in: '{os.path.abspath(output_base_dir)}'")

    # Group the DataFrame by 'Assessment Code'
    grouped_by_assessment = input_df.groupby('Assessment Code')

    if grouped_by_assessment.ngroups == 0:
        print("No groups found in the DataFrame. Is the 'Assessment Code' column present and populated?")
        return

    for assessment_code, group_df in grouped_by_assessment:
        # Sanitize the assessment code for use in filenames and identifiers
        assessment_identifier = sanitize_identifier(assessment_code)
        if not assessment_identifier or "unspecified_id" in assessment_identifier: # Check for the default identifier
             print(f"  ⚠️ Skipping group with invalid or empty Assessment Code: '{assessment_code}' (Sanitized: {assessment_identifier})")
             continue

        temp_package_root = None # Initialize for cleanup
        try:
            print(f"\nProcessing Assessment Code: '{assessment_code}' (Sanitized: {assessment_identifier}) with {len(group_df)} items.")

            # --- Prepare Temporary Directory Structure for this package ---
            temp_package_root = os.path.join(output_base_dir, f"temp_{assessment_identifier}_package")

            # Subdirectories for different file types
            items_dir = os.path.join(temp_package_root, "Items")
            tests_dir = os.path.join(temp_package_root, "Tests")
            # Add directories for media, css if needed in the future
            # media_dir = os.path.join(temp_package_root, "Media")
            # css_dir = os.path.join(temp_package_root, "CSS")

            os.makedirs(items_dir, exist_ok=True)
            os.makedirs(tests_dir, exist_ok=True)
            # os.makedirs(media_dir, exist_ok=True)
            # os.makedirs(css_dir, exist_ok=True)

            item_references_for_test = [] # To build the test XML (identifier, path from test dir)
            item_references_for_manifest = [] # To build the manifest XML (identifier, path from package root)
            
            # --- Generate QTI Item XMLs for all items in this group ---
            print("  Generating item XMLs...")
            for index, row in group_df.iterrows():
                 try:
                    # Ensure Item code is treated as string and sanitized
                    item_code_raw = str(row['Item code']).strip()
                    item_identifier = sanitize_identifier(item_code_raw)
                    
                    if not item_identifier or "unspecified_id" in item_identifier: # Check for the default identifier
                        print(f"    ⚠️ Skipping row {index+2} due to invalid Item Code: '{item_code_raw}' (Sanitized: {item_identifier})")
                        continue

                    item_title = f"Item: {item_code_raw}" # Use raw code for title if preferred
                    item_stimulus = str(row.get('Item Stimulus', '')).strip()
                    question_text = str(row['Item Stem']).strip()

                    options_data = []
                    option_cols = ['Option A', 'Option B', 'Option C', 'Option D']
                    valid_options_letters = []
                    for i, col in enumerate(option_cols):
                        option_letter = chr(65+i)
                        option_id = f"option_{option_letter}"
                        if col in row and pd.notna(row[col]) and str(row[col]).strip():
                            options_data.append((option_id, str(row[col]).strip()))
                            valid_options_letters.append(option_letter)

                    if not options_data:
                         print(f"    ⚠️ Skipping item '{item_code_raw}' (row {index+2}) due to no valid options found.")
                         continue

                    correct_answer_letter = str(row.get('Correct Answer', '')).strip().upper()
                    if not correct_answer_letter or correct_answer_letter not in valid_options_letters:
                         print(f"    ⚠️ Skipping item '{item_code_raw}' (row {index+2}) due to invalid or missing 'Correct Answer' value '{correct_answer_letter}'. Must be one of {valid_options_letters}.")
                         continue
                    correct_answer_id = f"option_{correct_answer_letter}"

                    # Define item XML path relative to package root and absolute path
                    item_xml_filename = f"item_{item_identifier}.xml" # Use sanitized ID in filename
                    item_xml_path_in_package = os.path.join("Items", item_xml_filename)
                    full_item_xml_path = os.path.join(temp_package_root, item_xml_path_in_package)

                    # Generate QTI Item XML
                    qti_xml_tree = create_qti_item_xml(
                        item_identifier, item_title, item_stimulus, question_text, options_data, correct_answer_id
                    )
                    with open(full_item_xml_path, 'wb') as f:
                        f.write(etree.tostring(qti_xml_tree, pretty_print=True, encoding='UTF-8', xml_declaration=True))

                    # Calculate relative path from the tests directory to this item XML
                    item_ref_path_from_test = os.path.relpath(full_item_xml_path, tests_dir).replace(os.sep, '/')

                    # Store info for test and manifest
                    item_references_for_test.append((item_identifier, item_ref_path_from_test))
                    item_references_for_manifest.append((item_identifier, item_xml_path_in_package.replace(os.sep, '/')))
                    # print(f"    ✅ Generated item: {item_identifier}") # Keep this quieter

                 except Exception as e:
                     print(f"    ❌ Error processing item row {index+2} ('{row.get('Item code', 'N/A')}'): {e}", file=sys.stderr)
                     # Continue processing other items in the group

            # --- Check if any valid items were processed ---
            if not item_references_for_test:
                 print(f"  Skipping test and package generation for Assessment Code '{assessment_code}' - No valid items found.")
                 # Ensure temp directory is cleaned up before continuing to next group
                 if temp_package_root and os.path.exists(temp_package_root):
                    shutil.rmtree(temp_package_root)
                 continue # Move to the next assessment code group

            # --- Generate QTI Test XML for this group ---
            print(f"  Generating test XML for {len(item_references_for_test)} items...")
            test_identifier = f"{assessment_identifier}_Test" # Use assessment ID for test ID
            test_title = f"Test for Assessment Code: {assessment_code}" # Use raw code for title

            test_qti_filename = f"test_{test_identifier}.xml" # Use sanitized test ID in filename
            test_xml_path_in_package = os.path.join("Tests", test_qti_filename)
            full_test_xml_path = os.path.join(temp_package_root, test_xml_path_in_package)

            test_xml_tree = create_qti_test_xml(
                test_identifier, test_title, item_references_for_test
            )
            with open(full_test_xml_path, 'wb') as f:
                f.write(etree.tostring(test_xml_tree, pretty_print=True, encoding='UTF-8', xml_declaration=True))
            print(f"    ✅ Generated test: {test_identifier}")

            # --- Generate imsmanifest.xml for the package ---
            print("  Generating manifest XML...")
            manifest_filepath = os.path.join(temp_package_root, "imsmanifest.xml")

            # No media/CSS handling implemented yet, pass empty lists
            imsmanifest_xml_tree = create_imsmanifest_xml_for_test_package(
                package_identifier=assessment_identifier, # Use assessment_identifier as the main package ID
                test_identifier=test_identifier,
                test_filename_relative_path=test_xml_path_in_package, # Path relative to package root
                item_references_for_manifest=item_references_for_manifest
            )
            with open(manifest_filepath, 'wb') as f:
                f.write(etree.tostring(imsmanifest_xml_tree, pretty_print=True, encoding='UTF-8', xml_declaration=True))
            print(f"    ✅ Generated manifest.")

            # --- Create ZIP File for the entire package ---
            zip_filename = os.path.join(output_base_dir, f"{assessment_identifier}.zip")
            
            print(f"  Creating package ZIP: {assessment_identifier}.zip...")
            # Use shutil.make_archive for robust zipping of the directory structure
            shutil.make_archive(
                base_name=os.path.join(output_base_dir, assessment_identifier), # Creates <assessment_identifier>.zip
                format='zip',
                root_dir=temp_package_root # Zips the content of this directory
            )
            print(f"  ✅ Successfully created package: {assessment_identifier}.zip")

        except KeyError as ke:
             # This error indicates a missing column, which should ideally be caught earlier by read_exam_data,
             # but good to have a fallback.
            print(f"  ❌ Error: Missing expected column '{ke}' while processing group '{assessment_code}'.")
        except Exception as e:
            print(f"  ❌ An unexpected error occurred while processing Assessment Code '{assessment_code}': {e}", file=sys.stderr)
            # Optionally print traceback for debugging
            # import traceback
            # traceback.print_exc()
        finally:
            # --- Clean up temporary directory ---
            if temp_package_root and os.path.exists(temp_package_root):
                # print(f"  Cleaning up temporary directory: {temp_package_root}")
                shutil.rmtree(temp_package_root)

    print("\nFinished processing all Assessment Codes.")


def read_exam_data(file_path: str) -> pd.DataFrame:
    """
    Reads exam data from a CSV or XLSX file and returns it as a DataFrame.
    Includes validation for required columns.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file '{file_path}' does not exist.")

    file_extension = os.path.splitext(file_path)[1].lower()
    df = pd.DataFrame()

    try:
        if file_extension == '.csv':
            # Add encoding detection if needed, or specify common encodings
            try:
                df = pd.read_csv(file_path, encoding='utf-8')
            except UnicodeDecodeError:
                 print("UTF-8 encoding failed, trying 'latin-1'.")
                 df = pd.read_csv(file_path, encoding='latin-1')
            except FileNotFoundError: # Catch FileNotFoundError again for robustness
                 raise FileNotFoundError(f"The file '{file_path}' was not found.")
        elif file_extension == '.xlsx':
            try:
                 df = pd.read_excel(file_path)
            except FileNotFoundError: # Catch FileNotFoundError again for robustness
                 raise FileNotFoundError(f"The file '{file_path}' was not found.")
        else:
            raise ValueError(
                f"Unsupported file format: '{file_extension}'. "
                "Please provide a .csv or .xlsx file."
            )
    except pd.errors.EmptyDataError:
        print(f"Warning: The file '{file_path}' is empty or has no data.")
        return pd.DataFrame()
    except Exception as e:
        # Catch other pandas read errors or general exceptions during file reading
        raise ValueError(f"Error reading file '{file_path}': {e}") from e


    expected_columns = [
        'Item code', 'Assessment Code', 'Difficulty Level', 'Bloom\'s Taxonomy',
        'Action Words', 'Item Stimulus', 'Item Stem', 'Option A',
        'Rationale for Option A', 'Option B', 'Rationale for Option B',
        'Option C', 'Rationale for Option C', 'Option D',
        'Rationale for Option D', 'Correct Answer'
    ]

    # Check for missing columns case-insensitively, but use the specified case for access later
    # Create a mapping of lowercased column names to actual column names
    col_map = {str(col).lower(): col for col in df.columns} # Ensure column names are strings
    missing_columns = [col for col in expected_columns if col.lower() not in col_map]

    if missing_columns:
        raise ValueError(
            f"The file '{file_path}' is missing expected columns: {missing_columns}. "
            f"Please ensure the following columns exist: {expected_columns}"
        )

    # Ensure the DataFrame only contains the expected columns and in their specified order,
    # using the actual column names from the file based on the lowercased match
    actual_cols_in_order = [col_map[col.lower()] for col in expected_columns]
    df = df[actual_cols_in_order].copy() # Use .copy() to avoid SettingWithCopyWarning later

    # Clean up Assessment Code - convert to string and handle potential NaNs
    df['Assessment Code'] = df['Assessment Code'].astype(str).replace('nan', '').str.strip()

    # Filter out rows where Assessment Code is empty after cleanup
    initial_rows = len(df)
    df = df[df['Assessment Code'] != ''].copy()
    if len(df) < initial_rows:
        print(f"Warning: Filtered out {initial_rows - len(df)} rows with empty 'Assessment Code'.")

    if df.empty:
         print("Warning: No rows remaining after filtering for valid 'Assessment Code'.")

    return df

def print_usage():
    print("Usage: python your_script_name.py <path_to_excel_file> <output_folder_for_packages>")
    print("Example: python main.py test.xlsx qti_assessment_packages")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("❌ Error: Invalid number of arguments.")
        print_usage()
        sys.exit(1)

    excel_file_path = sys.argv[1]
    output_dir = sys.argv[2]

    if not os.path.isfile(excel_file_path):
        print(f"❌ Error: File '{excel_file_path}' does not exist.")
        sys.exit(1)

    try:
        df_exam_data = read_exam_data(excel_file_path)
        if df_exam_data.empty:
            print("No valid data found in the input file to process.")
            sys.exit(0)

        # Create QTI packages grouped by Assessment Code
        create_qti_packages_by_assessment_code(df_exam_data, output_base_dir=output_dir)

        print(f"\n✅ All QTI packages generation complete in: '{os.path.abspath(output_dir)}'")

    except ValueError as ve:
        print(f"❌ ValueError: {ve}")
        sys.exit(1)
    except FileNotFoundError as fnf:
         print(f"❌ File Error: {fnf}")
         sys.exit(1)
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}", file=sys.stderr)
        # import traceback
        # traceback.print_exc() # Uncomment for more detailed error info
        sys.exit(1)
