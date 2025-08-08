import os
import re
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def patch_package_parser(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Patch 1: invoke-static ... unsafeGetCertsWithoutVerification
    pattern1 = re.compile(
        r'invoke-static \{v2, v0, v1\}, Landroid/util/apk/ApkSignatureVerifier;->unsafeGetCertsWithoutVerification\(Landroid/content/pm/parsing/result/ParseInput;Ljava/lang/String;I\)Landroid/content/pm/parsing/result/ParseResult;')
    modified_lines = []
    for line in lines:
        if pattern1.search(line):
            modified_lines.append("    const/4 v1, 0x1\n")
            logging.info("Patched: const/4 v1, 0x1 before unsafeGetCertsWithoutVerification")
        modified_lines.append(line)
    lines = modified_lines

    # Patch 2: const/4 v5, 0x1 above if-nez v5, :cond_x before sharedUserId error
    target_string = "\"<manifest> specifies bad sharedUserId name \\\"\""
    if_nez_pattern = re.compile(r'if-nez v5, :cond_\w+')
    modified_lines = []
    i = 0
    while i < len(lines):
        if target_string in lines[i]:
            # Geriye doğru if-nez v5, :cond_x bul
            for j in range(i-1, -1, -1):
                if if_nez_pattern.search(lines[j]):
                    modified_lines = lines[:j] + ["    const/4 v5, 0x1\n"] + lines[j:]
                    logging.info("Patched: const/4 v5, 0x1 above if-nez v5 before sharedUserId error")
                    break
            else:
                modified_lines = lines
            break
        i += 1
    if modified_lines:
        lines = modified_lines
    with open(file_path, 'w') as file:
        file.writelines(lines)

def patch_package_parser_exception(file_path):
    # Add const/4 p1, 0x0 above iput p1, ...
    with open(file_path, 'r') as file:
        lines = file.readlines()
    modified_lines = []
    for line in lines:
        if re.search(r'iput p1, p0, Landroid/content/pm/PackageParser\$PackageParserException;->error:I', line):
            modified_lines.append("    const/4 p1, 0x0\n")
            logging.info("Patched: const/4 p1, 0x0 above iput p1 in PackageParser$PackageParserException")
        modified_lines.append(line)
    with open(file_path, 'w') as file:
        file.writelines(modified_lines)

def patch_signingdetails(file_path):
    # checkCapability, hasAncestorOrSelf: return 1
    with open(file_path, 'r') as file:
        lines = file.readlines()
    modified_lines = []
    in_method = False
    method_type = None
    method_patterns = {
        "checkCapability": re.compile(r'\.method.*checkCapability\(.*\)Z'),
        "hasAncestorOrSelf": re.compile(r'\.method.*hasAncestorOrSelf\(.*\)Z'),
    }
    original_registers_line = ""
    method_start_line = ""
    for line in lines:
        if in_method:
            if line.strip().startswith('.registers'):
                original_registers_line = line
                continue
            if line.strip() == '.end method':
                modified_lines.append(method_start_line)
                modified_lines.append(original_registers_line)
                modified_lines.append("    const/4 v0, 0x1\n")
                modified_lines.append("    return v0\n")
                modified_lines.append(line)
                in_method = False
                method_type = None
                original_registers_line = ""
                method_start_line = ""
            else:
                continue
        for key, pattern in method_patterns.items():
            if pattern.search(line):
                in_method = True
                method_type = key
                method_start_line = line
                break
        if not in_method:
            modified_lines.append(line)
    with open(file_path, 'w') as file:
        file.writelines(modified_lines)
    logging.info(f"Patched: {file_path}")

def patch_apksignatureverifier(file_path):
    # getMinimumSignatureSchemeVersionForTargetSdk: return 0
    # Patch invoke-static {p0, p1, p3} ... above: const/4 p3, 0x0
    with open(file_path, 'r') as file:
        lines = file.readlines()
    # Patch method
    modified_lines = []
    in_method = False
    method_type = None
    method_patterns = {
        "getMinimumSignatureSchemeVersionForTargetSdk": re.compile(r'\.method.*getMinimumSignatureSchemeVersionForTargetSdk\(I\)I'),
    }
    original_registers_line = ""
    method_start_line = ""
    for line in lines:
        if in_method:
            if line.strip().startswith('.registers'):
                original_registers_line = line
                continue
            if line.strip() == '.end method':
                modified_lines.append(method_start_line)
                modified_lines.append(original_registers_line)
                modified_lines.append("    const/4 v0, 0x0\n")
                modified_lines.append("    return v0\n")
                modified_lines.append(line)
                in_method = False
                method_type = None
                original_registers_line = ""
                method_start_line = ""
            else:
                continue
        for key, pattern in method_patterns.items():
            if pattern.search(line):
                in_method = True
                method_type = key
                method_start_line = line
                break
        if not in_method:
            modified_lines.append(line)
    lines = modified_lines
    # Patch invoke-static
    modified_lines = []
    pattern = re.compile(
        r'invoke-static \{p0, p1, p3\}, Landroid/util/apk/ApkSignatureVerifier;->verifyV1Signature\(Landroid/content/pm/parsing/result/ParseInput;Ljava/lang/String;Z\)Landroid/content/pm/parsing/result/ParseResult;')
    for line in lines:
        if pattern.search(line):
            modified_lines.append("    const/4 p3, 0x0\n")
            logging.info("Patched: const/4 p3, 0x0 above verifyV1Signature")
        modified_lines.append(line)
    with open(file_path, 'w') as file:
        file.writelines(modified_lines)

def patch_apksignatureschemeV2V3(file_path, register='v0'):
    # Patch invoke-static ... MessageDigest->isEqual ... move-result vX -> const/4 vX, 0x1
    with open(file_path, 'r') as file:
        lines = file.readlines()
    modified_lines = []
    is_next_move_result = False
    for line in lines:
        if 'Ljava/security/MessageDigest;->isEqual([B[B)Z' in line:
            is_next_move_result = True
            modified_lines.append(line)
            continue
        if is_next_move_result and re.match(r'\s*move-result\s+(' + register + r')', line):
            modified_lines.append(f"    const/4 {register}, 0x1\n")
            logging.info(f"Patched: const/4 {register}, 0x1 after isEqual in {file_path}")
            is_next_move_result = False
            continue
        modified_lines.append(line)
        is_next_move_result = False
    with open(file_path, 'w') as file:
        file.writelines(modified_lines)

def patch_apksigningblockutils(file_path):
    # Patch invoke-static ... MessageDigest->isEqual ... move-result v7 -> const/4 v7, 0x1
    patch_apksignatureschemeV2V3(file_path, register='v7')

def patch_strictjarverifier(file_path):
    # Patch verifyMessageDigest method: return 1
    with open(file_path, 'r') as file:
        lines = file.readlines()
    modified_lines = []
    in_method = False
    method_pattern = re.compile(r'\.method.*verifyMessageDigest\(\[B\[B\)Z')
    original_registers_line = ""
    method_start_line = ""
    for line in lines:
        if in_method:
            if line.strip().startswith('.registers'):
                original_registers_line = line
                continue
            if line.strip() == '.end method':
                modified_lines.append(method_start_line)
                modified_lines.append(original_registers_line)
                modified_lines.append("    const/4 v0, 0x1\n")
                modified_lines.append("    return v0\n")
                modified_lines.append(line)
                in_method = False
                original_registers_line = ""
                method_start_line = ""
            else:
                continue
        if method_pattern.search(line):
            in_method = True
            method_start_line = line
            continue
        if not in_method:
            modified_lines.append(line)
    with open(file_path, 'w') as file:
        file.writelines(modified_lines)

def patch_strictjarfile(file_path):
    # Remove if-eqz v6, :cond_x and the next :cond_x label after findEntry
    with open(file_path, 'r') as file:
        lines = file.readlines()
    modified_lines = []
    i = 0
    invoke_virtual_pattern = re.compile(
        r'invoke-virtual \{p0, v5\}, Landroid/util/jar/StrictJarFile;->findEntry\(Ljava/lang/String;\)Ljava/util/zip/ZipEntry;')
    if_eqz_pattern = re.compile(r'if-eqz v6, :cond_\w+')
    label_pattern = re.compile(r':cond_\w+')
    while i < len(lines):
        if invoke_virtual_pattern.search(lines[i]):
            modified_lines.append(lines[i])
            i += 1
            if i < len(lines) and if_eqz_pattern.search(lines[i]):
                logging.info("Patched: Removed if-eqz v6, :cond_x after findEntry")
                i += 1
                if i < len(lines) and label_pattern.search(lines[i]):
                    logging.info("Patched: Removed :cond_x after if-eqz v6")
                    i += 1
            continue
        modified_lines.append(lines[i])
        i += 1
    with open(file_path, 'w') as file:
        file.writelines(modified_lines)

def patch_parsingpackageutils(file_path):
    # const/4 v4, 0x0 above if-eqz v4, :cond_x before sharedUserId error
    with open(file_path, 'r') as file:
        lines = file.readlines()
    target_string = "\"<manifest> specifies bad sharedUserId name \\\"\""
    if_eqz_pattern = re.compile(r'if-eqz v4, :cond_\w+')
    modified_lines = []
    i = 0
    while i < len(lines):
        if target_string in lines[i]:
            for j in range(i-1, -1, -1):
                if if_eqz_pattern.search(lines[j]):
                    modified_lines = lines[:j] + ["    const/4 v4, 0x0\n"] + lines[j:]
                    logging.info("Patched: const/4 v4, 0x0 above if-eqz v4 before sharedUserId error")
                    break
            else:
                modified_lines = lines
            break
        i += 1
    if modified_lines:
        lines = modified_lines
    with open(file_path, 'w') as file:
        file.writelines(lines)

def main():
    directories = ["classes", "classes2", "classes3", "classes4", "classes5"]
    for directory in directories:
        logging.info(f"Scanning directory: {directory}")
        # Patch android/content/pm/PackageParser.smali
        pkg_parser = os.path.join(directory, 'android/content/pm/PackageParser.smali')
        if os.path.exists(pkg_parser):
            patch_package_parser(pkg_parser)
        # Patch android/content/pm/PackageParser$PackageParserException.smali
        pkg_parser_exc = os.path.join(directory, 'android/content/pm/PackageParser$PackageParserException.smali')
        if os.path.exists(pkg_parser_exc):
            patch_package_parser_exception(pkg_parser_exc)
        # Patch android/content/pm/SigningDetails.smali
        signingdetails = os.path.join(directory, 'android/content/pm/SigningDetails.smali')
        if os.path.exists(signingdetails):
            patch_signingdetails(signingdetails)
        # Patch android/content/pm/PackageParser$SigningDetails.smali
        pkg_parser_signingdetails = os.path.join(directory, 'android/content/pm/PackageParser$SigningDetails.smali')
        if os.path.exists(pkg_parser_signingdetails):
            patch_signingdetails(pkg_parser_signingdetails)
        # Patch android/util/apk/ApkSignatureSchemeV2Verifier.smali
        v2ver = os.path.join(directory, 'android/util/apk/ApkSignatureSchemeV2Verifier.smali')
        if os.path.exists(v2ver):
            patch_apksignatureschemeV2V3(v2ver, register='v0')
        # Patch android/util/apk/ApkSignatureSchemeV3Verifier.smali
        v3ver = os.path.join(directory, 'android/util/apk/ApkSignatureSchemeV3Verifier.smali')
        if os.path.exists(v3ver):
            patch_apksignatureschemeV2V3(v3ver, register='v0')
        # Patch android/util/apk/ApkSignatureVerifier.smali
        verifier = os.path.join(directory, 'android/util/apk/ApkSignatureVerifier.smali')
        if os.path.exists(verifier):
            patch_apksignatureverifier(verifier)
        # Patch android/util/apk/ApkSigningBlockUtils.smali
        signingblock = os.path.join(directory, 'android/util/apk/ApkSigningBlockUtils.smali')
        if os.path.exists(signingblock):
            patch_apksigningblockutils(signingblock)
        # Patch android/util/jar/StrictJarVerifier.smali
        jarverifier = os.path.join(directory, 'android/util/jar/StrictJarVerifier.smali')
        if os.path.exists(jarverifier):
            patch_strictjarverifier(jarverifier)
        # Patch android/util/jar/StrictJarFile.smali
        jarfile = os.path.join(directory, 'android/util/jar/StrictJarFile.smali')
        if os.path.exists(jarfile):
            patch_strictjarfile(jarfile)
        # Patch com/android/internal/pm/pkg/parsing/ParsingPackageUtils.smali
        parsingutils = os.path.join(directory, 'com/android/internal/pm/pkg/parsing/ParsingPackageUtils.smali')
        if os.path.exists(parsingutils):
            patch_parsingpackageutils(parsingutils)

if __name__ == "__main__":
    main()
