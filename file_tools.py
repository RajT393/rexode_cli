import os
import shutil
import zipfile

def read_file(path: str) -> str:
    try:
        if not os.path.exists(path):
            return "⚠️ File not found."
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"❌ Error reading file: {str(e)}"


def write_file(text: str) -> str:
    """Writes content to a file. The first part of the input before '|||' is the filename and the rest is the content."""
    try:
        filename, content = text.split("|||", 1)
        with open(filename.strip(), "w", encoding="utf-8") as f:
            f.write(content)
        return f"✅ Wrote to {filename.strip()}"
    except Exception as e:
        return f"❌ Error writing to file: {str(e)}"


def list_directory(path: str = ".") -> str:
    try:
        return "\n".join(os.listdir(path))
    except Exception as e:
        return f"❌ Error listing directory: {str(e)}"


def summarize_file(path: str) -> str:
    try:
        content = read_file(path)
        return content[:1000] + ("..." if len(content) > 1000 else "")
    except Exception as e:
        return f"❌ Could not summarize file: {str(e)}"

def delete_file(path: str) -> str:
    try:
        if not os.path.exists(path):
            return "⚠️ File not found."
        os.remove(path)
        return f"✅ Deleted file: {path}"
    except Exception as e:
        return f"❌ Error deleting file: {str(e)}"

def move_file(text: str) -> str:
    try:
        source, destination = text.split("|||", 1)
        source = source.strip()
        destination = destination.strip()
        if not os.path.exists(source):
            return "⚠️ Source file not found."
        shutil.move(source, destination)
        return f"✅ Moved file from {source} to {destination}"
    except Exception as e:
        return f"❌ Error moving file: {str(e)}"

def copy_file(text: str) -> str:
    try:
        source, destination = text.split("|||", 1)
        source = source.strip()
        destination = destination.strip()
        if not os.path.exists(source):
            return "⚠️ Source file not found."
        shutil.copy2(source, destination)
        return f"✅ Copied file from {source} to {destination}"
    except Exception as e:
        return f"❌ Error copying file: {str(e)}"

def rename_item(text: str) -> str:
    try:
        old_path, new_path = text.split("|||", 1)
        old_path = old_path.strip()
        new_path = new_path.strip()
        if not os.path.exists(old_path):
            return "⚠️ Item not found."
        os.rename(old_path, new_path)
        return f"✅ Renamed {old_path} to {new_path}"
    except Exception as e:
        return f"❌ Error renaming item: {str(e)}"

def create_directory(path: str) -> str:
    try:
        os.makedirs(path, exist_ok=True)
        return f"✅ Created directory: {path}"
    except Exception as e:
        return f"❌ Error creating directory: {str(e)}"

def delete_directory(path: str) -> str:
    try:
        if not os.path.exists(path):
            return "⚠️ Directory not found."
        shutil.rmtree(path)
        return f"✅ Deleted directory: {path}"
    except Exception as e:
        return f"❌ Error deleting directory: {str(e)}"

def search_file_content(text: str) -> str:
    try:
        path, pattern = text.split("|||", 1)
        path = path.strip()
        pattern = pattern.strip()
        if not os.path.exists(path):
            return "⚠️ Path not found."
        
        matches = []
        for root, _, files in os.walk(path):
            for file in files:
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        for line_num, line in enumerate(f, 1):
                            if pattern in line:
                                matches.append(f"{filepath}:{line_num}: {line.strip()}")
                except Exception:
                    continue # Skip files that can't be read
        
        if matches:
            return "\n".join(matches)
        else:
            return "No matches found."
    except Exception as e:
        return f"❌ Error searching file content: {str(e)}"

def zip_item(text: str) -> str:
    try:
        path_to_zip, output_filename = text.split("|||", 1)
        path_to_zip = path_to_zip.strip()
        output_filename = output_filename.strip()

        if not os.path.exists(path_to_zip):
            return "⚠️ Item to zip not found."

        # Determine if it's a file or directory
        if os.path.isfile(path_to_zip):
            with zipfile.ZipFile(output_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(path_to_zip, os.path.basename(path_to_zip))
        elif os.path.isdir(path_to_zip):
            shutil.make_archive(os.path.splitext(output_filename)[0], 'zip', path_to_zip)
        else:
            return "⚠️ Invalid path provided for zipping."

        return f"✅ Successfully zipped {path_to_zip} to {output_filename}"
    except Exception as e:
        return f"❌ Error zipping item: {str(e)}"

def unzip_item(text: str) -> str:
    try:
        path_to_unzip, output_directory = text.split("|||", 1)
        path_to_unzip = path_to_unzip.strip()
        output_directory = output_directory.strip()

        if not os.path.exists(path_to_unzip):
            return "⚠️ Zip file not found."
        if not zipfile.is_zipfile(path_to_unzip):
            return "⚠️ Not a valid zip file."

        os.makedirs(output_directory, exist_ok=True)

        with zipfile.ZipFile(path_to_unzip, 'r') as zipf:
            zipf.extractall(output_directory)

        return f"✅ Successfully unzipped {path_to_unzip} to {output_directory}"
    except Exception as e:
        return f"❌ Error unzipping item: {str(e)}"