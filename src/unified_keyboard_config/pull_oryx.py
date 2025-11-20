import json
import os
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
import zipfile
from pathlib import Path


def main():
    # 1. Get configuration from environment variables
    layout_id = os.environ.get("ORYX_LAYOUT_ID")
    geometry = os.environ.get("ORYX_GEOMETRY")

    if not layout_id or not geometry:
        print(
            "Error: ORYX_LAYOUT_ID and ORYX_GEOMETRY environment variables must be set."
        )
        sys.exit(1)

    print(f"Fetching latest layout for ID: {layout_id}, Geometry: {geometry}")

    # 2. Query Oryx GraphQL API
    url = "https://oryx.zsa.io/graphql"
    query = """
    query getLayout($hashId: String!, $revisionId: String!, $geometry: String) {
      layout(hashId: $hashId, geometry: $geometry, revisionId: $revisionId) {
        revision {
          hashId
          qmkVersion
          title
        }
      }
    }
    """
    variables = {"hashId": layout_id, "geometry": geometry, "revisionId": "latest"}
    data = json.dumps({"query": query, "variables": variables}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
    )

    try:
        with urllib.request.urlopen(req) as response:
            response_data = json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as e:
        print(f"Error querying Oryx API: {e}")
        sys.exit(1)

    revision = response_data.get("data", {}).get("layout", {}).get("revision")
    if not revision:
        print("Error: Could not retrieve layout revision information.")
        print(f"Response: {response_data}")
        sys.exit(1)

    latest_hash = revision["hashId"]
    title = revision["title"]
    print(f"Found latest hash: {latest_hash}")
    print(f"Layout title: {title}")

    # 3. Download source zip
    download_url = f"https://oryx.zsa.io/source/{latest_hash}"
    zip_filename = "source.zip"
    print(f"Downloading source from: {download_url}")

    try:
        urllib.request.urlretrieve(download_url, zip_filename)
    except urllib.error.URLError as e:
        print(f"Error downloading source: {e}")
        sys.exit(1)

    # 4. Extract and organize files
    target_dir = Path("submodule/Moonlander-Mk1-QMK")
    if not target_dir.exists():
        print(f"Error: Target directory {target_dir} does not exist.")
        sys.exit(1)

    print(f"Extracting to {target_dir}...")
    try:
        with zipfile.ZipFile(zip_filename, "r") as zip_ref:
            zip_ref.extractall(target_dir)
    except zipfile.BadZipFile:
        print("Error: Downloaded file is not a valid zip file.")
        sys.exit(1)
    finally:
        if os.path.exists(zip_filename):
            os.remove(zip_filename)

    # Cleanup and move files
    # The zip extracts to a folder like 'moonlander_layout_name_source'
    # We need to find that folder and move its contents to target_dir/src

    # First, remove existing artifacts in target_dir
    for pattern in ["build.log", "*.bin", "*.bin.md5"]:
        for f in target_dir.glob(pattern):
            f.unlink()

    # Remove existing src dir if it exists
    src_dir = target_dir / "src"
    if src_dir.exists():
        shutil.rmtree(src_dir)

    # Find the extracted source directory
    extracted_source_dir = None
    for item in target_dir.iterdir():
        if item.is_dir() and item.name.endswith("_source"):
            extracted_source_dir = item
            break

    if extracted_source_dir:
        print(f"Moving contents of {extracted_source_dir.name} to src...")
        extracted_source_dir.rename(src_dir)
    else:
        print("Warning: Could not find extracted source directory (ending in _source).")

    # 5. Git commit
    print("Committing changes...")
    commit_message = title
    try:
        subprocess.run(["git", "add", "."], cwd=target_dir, check=True)
        # Check if there are changes to commit
        status = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=target_dir,
            capture_output=True,
            text=True,
        )
        if status.stdout.strip():
            subprocess.run(
                ["git", "commit", "-m", commit_message],
                cwd=target_dir,
                check=True,
            )
            print(f"Committed with message: '{commit_message}'")
        else:
            print("No changes to commit.")
    except subprocess.CalledProcessError as e:
        print(f"Error during git operations: {e}")
        sys.exit(1)

    print("Update complete!")


if __name__ == "__main__":
    main()
