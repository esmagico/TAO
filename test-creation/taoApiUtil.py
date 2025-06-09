import requests
import os
import base64
import json
import sys
from dotenv import load_dotenv

load_dotenv()

base_url = os.getenv("TAO_BASE_URL")
username = os.getenv("TAO_USERNAME")
password = os.getenv("TAO_PASSWORD")

# Encode the credentials manually
auth_header = f"Basic {base64.b64encode(f'{username}:{password}'.encode()).decode()}"

def upload_zip_to_tao_api(zip_file_path: str) -> dict | str | None:
    url = f"{base_url}/taoQtiItem/RestQtiItem/import/"

    headers = {
        "Accept": "application/json",
        "Authorization": auth_header,  # Use encoded Basic Auth
    }

    if not os.path.exists(zip_file_path):
        print(f"Error: The file '{zip_file_path}' does not exist.")
        return None
    if not os.path.isfile(zip_file_path):
        print(f"Error: The path '{zip_file_path}' is not a file.")
        return None

    try:
        with open(zip_file_path, "rb") as f:
            # --- THE CRUCIAL CHANGE IS HERE ---
            # Provide the filename and optionally the MIME type explicitly
            files = {
                "content": (os.path.basename(zip_file_path), f, 'application/zip')
            }

            print(f"Uploading '{os.path.basename(zip_file_path)}' to {url}...")
            response = requests.post(
                url,
                headers=headers,
                files=files,
                timeout=30
            )
            response.raise_for_status() # This will raise an exception for 4xx/5xx responses

            print(f"Success! Status Code: {response.status_code}")
            try:
                return response.json()
            except json.JSONDecodeError:
                print("Warning: Response was not JSON.")
                print(f"Raw response content: {response.text}") # Print raw text for debugging
                return response.text

    except requests.exceptions.RequestException as e:
        print(f"Request Error: {e}")
        if hasattr(e, "response") and e.response is not None:
            print(f"Response content:\n{e.response.text}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

def upload_test_zip_to_tao_api(zip_file_path: str) -> dict | str | None:
    url = f"{base_url}/taoQtiTest/RestQtiTests/import/"

    headers = {
        "Accept": "application/json",
        "Authorization": auth_header,  # Use encoded Basic Auth
    }

    if not os.path.exists(zip_file_path):
        print(f"Error: The file '{zip_file_path}' does not exist.")
        return None
    if not os.path.isfile(zip_file_path):
        print(f"Error: The path '{zip_file_path}' is not a file.")
        return None

    try:
        with open(zip_file_path, "rb") as f:
            # --- THE CRUCIAL CHANGE IS HERE ---
            # Provide the filename and optionally the MIME type explicitly
            files = {
                "qtiPackage": (os.path.basename(zip_file_path), f, 'application/zip')
            }

            print(f"Uploading '{os.path.basename(zip_file_path)}' to {url}...")
            response = requests.post(
                url,
                headers=headers,
                files=files,
                timeout=30
            )
            response.raise_for_status() # This will raise an exception for 4xx/5xx responses

            print(f"Success! Status Code: {response.status_code}")
            try:
                return response.json()
            except json.JSONDecodeError:
                print("Warning: Response was not JSON.")
                print(f"Raw response content: {response.text}") # Print raw text for debugging
                return response.text

    except requests.exceptions.RequestException as e:
        print(f"Request Error: {e}")
        if hasattr(e, "response") and e.response is not None:
            print(f"Response content:\n{e.response.text}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

def print_usage():
    print("Usage: python import_qti.py <qti_packages_dir>")
    print("Example: python import_qti.py qti_output")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("❌ Error: Missing required argument.")
        print_usage()
        sys.exit(1)

    qti_packages_dir = sys.argv[1]

    if not os.path.isdir(qti_packages_dir):
        print(f"❌ Error: Directory '{qti_packages_dir}' not found.")
        sys.exit(1)

    zip_files = sorted([f for f in os.listdir(qti_packages_dir) if f.endswith(".zip")])

    if not zip_files:
        print(f"⚠️ No .zip files found in '{qti_packages_dir}'.")
        sys.exit(0)
        
    if not base_url or not username or not password:
        print(f"❌ Error: Environment variables not set. Create .env file with variables as per sample.env with proper values. Try to run source .env command if you are using bash.")
        sys.exit(1)

    item_successful_imports = []
    item_failed_imports = []

    test_successful_imports = []
    test_failed_imports = []

    for i, filename in enumerate(zip_files):
        file_path = os.path.join(qti_packages_dir, filename)
        print(f"\n--- Importing {i+1}/{len(zip_files)}: {filename} ---")

        #######ITEMS API HIT##########
        try:
            response_data = upload_zip_to_tao_api(zip_file_path=file_path)
            if isinstance(response_data, dict) and response_data.get('success') is True:
                item_successful_imports.append(filename)
                print(f"✅ SUCCESS: {filename} imported as item.")
            else:
                item_failed_imports.append(filename)
                print(f"❌ FAILURE: {filename} could not be imported as item.")
        except Exception as e:
            item_failed_imports.append(filename)
            print(f"❌ ERROR: Exception occurred while importing as item '{filename}': {e}")

        #######TESTS API HIT##########
        try:
            response_data = upload_test_zip_to_tao_api(zip_file_path=file_path)
            if isinstance(response_data, dict) and response_data.get('success') is True:
                test_successful_imports.append(filename)
                print(f"✅ SUCCESS: {filename} imported as test.")
            else:
                test_failed_imports.append(filename)
                print(f"❌ FAILURE: {filename} could not be imported as test.")
        except Exception as e:
            test_failed_imports.append(filename)
            print(f"❌ ERROR: Exception occurred while importing as test '{filename}': {e}")

    print("\n--- 📦 Import Summary ---")
    print(f"✅ Successful Item Imports: {item_successful_imports}")
    print(f"❌ Failed Item Imports: {item_failed_imports}")
    print(f"✅ Successful Test Imports: {item_successful_imports}")
    print(f"❌ Failed Test Imports: {item_failed_imports}")
