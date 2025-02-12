import os
import re
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def patch(filepath):
    with open(filepath, 'r') as file:
        lines = file.readlines()

    if not any('invoke-custom' in line for line in lines):
        return
    modified_lines = []
    in_method = False
    method_type = None
    method_patterns = {
        "equals": re.compile(r'\.method.*equals\(Ljava/lang/Object;\)Z'),
        "hashCode": re.compile(r'\.method.*hashCode\(\)I'),
        "toString": re.compile(r'\.method.*toString\(\)Ljava/lang/String;')
    }
    registers_line = ""

    for line in lines:
        if in_method:
            if line.strip().startswith('.registers'):
                registers_line = line
                continue

            if line.strip() == '.end method':
                if method_type in method_patterns:
                    logging.info(f"Clearing method body for {method_type}")
                    modified_lines.append(registers_line)
                    if method_type == "hashCode":
                        modified_lines.append("    const/4 v0, 0x0\n")
                        modified_lines.append("    return v0\n")
                    elif method_type == "equals":
                        modified_lines.append("    const/4 v0, 0x0\n")
                        modified_lines.append("    return v0\n")
                    elif method_type == "toString":
                        modified_lines.append("     const/4 v0, 0x0\n")
                        modified_lines.append("    return-object v0\n")
                in_method = False
                method_type = None
                registers_line = ""
            else:
                continue

        for key, pattern in method_patterns.items():
            if pattern.search(line):
                logging.info(f"Found method {key}. Clearing method content.")
                in_method = True
                method_type = key
                modified_lines.append(line)  # Add method declaration to output
                break

        if not in_method:
            modified_lines.append(line)

    with open(filepath, 'w') as file:
        file.writelines(modified_lines)
    logging.info(f"Completed modification for file: {filepath}")

def modify_updateDefaultPkgInstallerLocked(file_path):
    logging.info(f"Modifying updateDefaultPkgInstallerLocked method in file: {file_path}")
    with open(file_path, 'r') as file:
        lines = file.readlines()

    modified_lines = []
    in_method = False
    for line in lines:
        if in_method:
            if 'sget-boolean v0, Lcom/android/server/pm/PackageManagerServiceImpl;->IS_INTERNATIONAL_BUILD:Z' in line:
                modified_lines.append('    const/4 v0, 0x0\n')
            else:
                modified_lines.append(line)
            if line.strip() == '.end method':
                in_method = False
        elif '.method private updateDefaultPkgInstallerLocked()Z' in line:
            in_method = True
            modified_lines.append(line)
        else:
            modified_lines.append(line)

    with open(file_path, 'w') as file:
        file.writelines(modified_lines)
    logging.info(f"Completed modification for updateDefaultPkgInstallerLocked method in file: {file_path}")

def modify_smali_files(directories):
    for directory in directories:
        updateDefaultPkgInstallerLocked = os.path.join(directory, 'com/android/server/pm/PackageManagerServiceImpl.smali')

        logging.info(f"Scanning directory: {directory}")
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith(".smali"):
                    filepath = os.path.join(root, file)
                    patch(filepath)

        if os.path.exists(updateDefaultPkgInstallerLocked):
            logging.info(f"Found file: {updateDefaultPkgInstallerLocked}")
            modify_updateDefaultPkgInstallerLocked(updateDefaultPkgInstallerLocked)
        else:
            logging.warning(f"File not found: {updateDefaultPkgInstallerLocked}")

if __name__ == "__main__":
    directories = ["miui_services_classes"]
    modify_smali_files(directories)
