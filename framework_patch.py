import os
import re
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def find_all_files(rootdirs, relpath):
    """Tüm rootdirs altında relpath'e uyan tüm dosya yollarını bulur."""
    found = []
    for rootdir in rootdirs:
        for dirpath, _, files in os.walk(rootdir):
            for file in files:
                full_path = os.path.join(dirpath, file)
                if full_path.endswith(relpath):
                    found.append(full_path)
    return found

def patch_package_parser(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    pattern1 = re.compile(
        r'invoke-static \{v2, v0, v1\}, Landroid/util/apk/ApkSignatureVerifier;->unsafeGetCertsWithoutVerification\(Landroid/content/pm/parsing/result/ParseInput;Ljava/lang/String;I\)Landroid/content/pm/parsing/result/ParseResult;')
    out = []
    for line in lines:
        if pattern1.search(line):
            out.append("    const/4 v1, 0x1\n")
            logging.info(f"Patched: const/4 v1, 0x1 before unsafeGetCertsWithoutVerification in {file_path}")
        out.append(line)
    lines = out

    target_string = "\"<manifest> specifies bad sharedUserId name \\\"\""
    if_nez_pattern = re.compile(r'if-nez v5, :cond_\w+')
    indexes = [i for i, l in enumerate(lines) if target_string in l]
    for idx in indexes:
        for j in range(idx-1, -1, -1):
            if if_nez_pattern.search(lines[j]):
                lines.insert(j, "    const/4 v5, 0x1\n")
                logging.info(f"Patched: const/4 v5, 0x1 above if-nez v5 before sharedUserId error in {file_path}")
                break
    with open(file_path, 'w') as file:
        file.writelines(lines)

def patch_package_parser_exception(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    out = []
    for line in lines:
        if re.search(r'iput p1, p0, Landroid/content/pm/PackageParser\$PackageParserException;->error:I', line):
            out.append("    const/4 p1, 0x0\n")
            logging.info(f"Patched: const/4 p1, 0x0 above iput p1 in {file_path}")
        out.append(line)
    with open(file_path, 'w') as file:
        file.writelines(out)

def patch_signingdetails(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    out = []
    method_patterns = {
        "checkCapability": re.compile(r'\.method.*checkCapability\(.*\)Z'),
        "hasAncestorOrSelf": re.compile(r'\.method.*hasAncestorOrSelf\(.*\)Z'),
    }
    in_method = False
    method_type = None
    method_start_line = ""
    registers_line = ""
    for line in lines:
        if in_method:
            if line.strip().startswith('.registers'):
                registers_line = line
                continue
            if line.strip() == '.end method':
                out.append(method_start_line)
                out.append(registers_line)
                out.append("    const/4 v0, 0x1\n")
                out.append("    return v0\n")
                out.append(line)
                in_method = False
                method_type = None
                method_start_line = ""
                registers_line = ""
                continue
            continue
        found = False
        for key, pattern in method_patterns.items():
            if pattern.search(line):
                in_method = True
                method_type = key
                method_start_line = line
                found = True
                break
        if not found and not in_method:
            out.append(line)
    with open(file_path, 'w') as file:
        file.writelines(out)
    logging.info(f"Patched: {file_path}")

def patch_apksignatureverifier(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    out = []
    in_method = False
    method_pattern = re.compile(r'\.method.*getMinimumSignatureSchemeVersionForTargetSdk\(I\)I')
    method_start_line = ""
    registers_line = ""
    for idx, line in enumerate(lines):
        if in_method:
            if line.strip().startswith('.registers'):
                registers_line = line
                continue
            if line.strip() == '.end method':
                out.append(method_start_line)
                out.append(registers_line)
                out.append("    const/4 v0, 0x0\n")
                out.append("    return v0\n")
                out.append(line)
                in_method = False
                method_start_line = ""
                registers_line = ""
                continue
            continue
        if method_pattern.search(line):
            in_method = True
            method_start_line = line
            continue
        out.append(line)
    lines = out

    out = []
    pattern = re.compile(
        r'invoke-static \{p0, p1, p3\}, Landroid/util/apk/ApkSignatureVerifier;->verifyV1Signature\(Landroid/content/pm/parsing/result/ParseInput;Ljava/lang/String;Z\)Landroid/content/pm/parsing/result/ParseResult;')
    for line in lines:
        if pattern.search(line):
            out.append("    const/4 p3, 0x0\n")
            logging.info(f"Patched: const/4 p3, 0x0 above verifyV1Signature in {file_path}")
        out.append(line)
    with open(file_path, 'w') as file:
        file.writelines(out)

def patch_apksignatureschemeV2V3(file_path, register='v0'):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    out = []
    is_next_move_result = False
    for line in lines:
        if 'Ljava/security/MessageDigest;->isEqual([B[B)Z' in line:
            is_next_move_result = True
            out.append(line)
            continue
        if is_next_move_result and re.match(r'\s*move-result\s+(' + register + r')', line):
            out.append(f"    const/4 {register}, 0x1\n")
            logging.info(f"Patched: const/4 {register}, 0x1 after isEqual in {file_path}")
            is_next_move_result = False
            continue
        out.append(line)
        is_next_move_result = False
    with open(file_path, 'w') as file:
        file.writelines(out)

def patch_apksigningblockutils(file_path):
    patch_apksignatureschemeV2V3(file_path, register='v7')

def patch_strictjarverifier(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    out = []
    in_method = False
    method_pattern = re.compile(r'\.method.*verifyMessageDigest\(\[B\[B\)Z')
    method_start_line = ""
    registers_line = ""
    for line in lines:
        if in_method:
            if line.strip().startswith('.registers'):
                registers_line = line
                continue
            if line.strip() == '.end method':
                out.append(method_start_line)
                out.append(registers_line)
                out.append("    const/4 v0, 0x1\n")
                out.append("    return v0\n")
                out.append(line)
                in_method = False
                method_start_line = ""
                registers_line = ""
                continue
            continue
        if method_pattern.search(line):
            in_method = True
            method_start_line = line
            continue
        out.append(line)
    with open(file_path, 'w') as file:
        file.writelines(out)

def patch_strictjarfile(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    out = []
    i = 0
    invoke_virtual_pattern = re.compile(
        r'invoke-virtual \{p0, v5\}, Landroid/util/jar/StrictJarFile;->findEntry\(Ljava/lang/String;\)Ljava/util/zip/ZipEntry;')
    if_eqz_pattern = re.compile(r'if-eqz v6, :cond_\w+')
    label_pattern = re.compile(r':cond_\w+')
    while i < len(lines):
        if invoke_virtual_pattern.search(lines[i]):
            out.append(lines[i])
            i += 1
            removed_if = False
            while i < len(lines) and (if_eqz_pattern.search(lines[i]) or label_pattern.search(lines[i])):
                logging.info(f"Patched: Removed if-eqz v6, :cond_x or label after findEntry in {file_path}")
                i += 1
                removed_if = True
            if removed_if:
                continue
        if i < len(lines):
            out.append(lines[i])
        i += 1
    with open(file_path, 'w') as file:
        file.writelines(out)

def patch_parsingpackageutils(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    target_string = "\"<manifest> specifies bad sharedUserId name \\\"\""
    if_eqz_pattern = re.compile(r'if-eqz v4, :cond_\w+')
    indexes = [i for i, l in enumerate(lines) if target_string in l]
    for idx in indexes:
        for j in range(idx-1, -1, -1):
            if if_eqz_pattern.search(lines[j]):
                lines.insert(j, "    const/4 v4, 0x0\n")
                logging.info(f"Patched: const/4 v4, 0x0 above if-eqz v4 before sharedUserId error in {file_path}")
                break
    with open(file_path, 'w') as file:
        file.writelines(lines)

def main():
    rootdirs = ["classes", "classes2", "classes3", "classes4", "classes5"]
    # Tüm dosyalarda recursive bul-patch uygula
    # 1
    for file_path in find_all_files(rootdirs, 'android/content/pm/PackageParser.smali'):
        patch_package_parser(file_path)
    # 2
    for file_path in find_all_files(rootdirs, 'android/content/pm/PackageParser$PackageParserException.smali'):
        patch_package_parser_exception(file_path)
    # 3
    for file_path in find_all_files(rootdirs, 'android/content/pm/SigningDetails.smali'):
        patch_signingdetails(file_path)
    # 4
    for file_path in find_all_files(rootdirs, 'android/content/pm/PackageParser$SigningDetails.smali'):
        patch_signingdetails(file_path)
    # 5
    for file_path in find_all_files(rootdirs, 'android/util/apk/ApkSignatureSchemeV2Verifier.smali'):
        patch_apksignatureschemeV2V3(file_path, register='v0')
    # 6
    for file_path in find_all_files(rootdirs, 'android/util/apk/ApkSignatureSchemeV3Verifier.smali'):
        patch_apksignatureschemeV2V3(file_path, register='v0')
    # 7
    for file_path in find_all_files(rootdirs, 'android/util/apk/ApkSignatureVerifier.smali'):
        patch_apksignatureverifier(file_path)
    # 8
    for file_path in find_all_files(rootdirs, 'android/util/apk/ApkSigningBlockUtils.smali'):
        patch_apksigningblockutils(file_path)
    # 9
    for file_path in find_all_files(rootdirs, 'android/util/jar/StrictJarVerifier.smali'):
        patch_strictjarverifier(file_path)
    # 10
    for file_path in find_all_files(rootdirs, 'android/util/jar/StrictJarFile.smali'):
        patch_strictjarfile(file_path)
    # 11
    for file_path in find_all_files(rootdirs, 'com/android/internal/pm/pkg/parsing/ParsingPackageUtils.smali'):
        patch_parsingpackageutils(file_path)

if __name__ == "__main__":
    main()
