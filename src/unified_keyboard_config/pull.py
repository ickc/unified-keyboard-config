import json
import shutil
import subprocess
import tempfile
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

from .patch import patch_keymap


def pull_source(
    submodule_path: Path, layout_id: str, geometry: str, do_patch: bool = False
):
    """
    Pulls the latest Oryx layout source and updates the submodule.
    Optionally patches the keymap.
    """
    if not layout_id or not geometry:
        raise ValueError("layout_id and geometry must be provided.")

    print(f"Fetching latest layout for ID: {layout_id}, Geometry: {geometry}")

    # 1. Query Oryx GraphQL API
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
        raise RuntimeError(f"Error querying Oryx API: {e}") from e

    revision = response_data.get("data", {}).get("layout", {}).get("revision")
    if not revision:
        raise RuntimeError(
            f"Error: Could not retrieve layout revision information. Response: {response_data}"
        )

    latest_hash = revision["hashId"]
    title = revision["title"]
    print(f"Found latest hash: {latest_hash}")
    print(f"Layout title: {title}")

    # 2. Download source zip
    download_url = f"https://oryx.zsa.io/source/{latest_hash}"

    target_dir = submodule_path
    if not target_dir.exists():
        raise FileNotFoundError(f"Target directory {target_dir} does not exist.")

    # 3. Extract and organize files
    # Download into a temp dir so a failure never leaves a stray zip behind.
    with tempfile.TemporaryDirectory() as tmp_dir:
        zip_path = Path(tmp_dir) / "source.zip"
        print(f"Downloading source from: {download_url}")
        try:
            urllib.request.urlretrieve(download_url, zip_path)
        except urllib.error.URLError as e:
            raise RuntimeError(f"Error downloading source: {e}") from e

        print(f"Extracting to {target_dir}...")
        try:
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(target_dir)
        except zipfile.BadZipFile as e:
            raise RuntimeError("Error: Downloaded file is not a valid zip file.") from e

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

    # 4. Patch if requested
    commit_message = title
    if do_patch:
        keymap_path = src_dir / "keymap.c"
        print(f"Patching keymap at {keymap_path}...")
        try:
            patch_keymap(keymap_path, geometry)
            commit_message += " (patched)"
        except Exception as e:
            raise RuntimeError(f"Failed to patch keymap: {e}") from e

    # 5. Git commit
    print("Committing changes...")
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
        raise RuntimeError(f"Error during git operations: {e}") from e

    print("Update complete!")
