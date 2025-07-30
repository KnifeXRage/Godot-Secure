import os
import sys
import random
import string
import binascii

class LogColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    
def generate_random_tag(length=4):
    return ''.join(random.choices(string.ascii_uppercase, k=length))

def generate_random_token(length=32):
    return bytes([random.randint(0, 255) for _ in range(length)])

def generate_magic_header(tag: str, endian='little') -> str:
    if len(tag) != 4:
        raise ValueError("Tag must be exactly 4 characters.")
    
    if endian == 'little':
        tag = tag[::-1]  # Reverse for little-endian

    hex_value = "0x" + ''.join(f"{ord(c):02X}" for c in tag)
    return hex_value

def print_success(message):
    print(f"{LogColors.OKGREEN}      ✓{LogColors.ENDC} {message}")

def print_error(message):
    print(f"{LogColors.FAIL}      ✗{LogColors.ENDC} {message}")

def print_info(message):
    print(f"\n{LogColors.OKBLUE} ℹ {LogColors.ENDC} {message}")
    
def print_operation(message):
    print(f"{LogColors.HEADER}   =>{LogColors.ENDC} {message}")

def print_warning(message):
    print(f"\n{LogColors.WARNING} ⚠ {LogColors.ENDC} {message}")

# Generate unique identifiers
baseTag = generate_random_tag()
encTag = generate_random_tag()
security_token = generate_random_token()
token_hex = binascii.hexlify(security_token).decode('utf-8')
token_c_array = ', '.join([f'0x{b:02X}' for b in security_token])
baseHeader = generate_magic_header(baseTag)
encHeader = generate_magic_header(encTag)
fileCreated = True
backup_path = None

MODIFICATIONS = [
    #Pre -Steps:
    {
        "file": "core/core_builders.py",
        "operations": [
            {
                "type": "replace_line",
                "description": "Modify Godot title To add Godot Secure",
                "find": "#define GODOT_VERSION_NAME \"{name}\"",
                "replace": "#define GODOT_VERSION_NAME \"{name} (With Godot Secure)\""
            }
        ]
    },
    
    {
        "file": "editor/export/project_export.cpp",
        "operations": [
            {
                "type": "replace_line",
                "description": "Modify Godot export popup title To add Godot Secure",
                "find": "set_title(TTR(\"Export\"));",
                "replace": "set_title(TTR(\"Export With Godot Secure\"));"
            }
        ]
    },

    # Step 0: Create security token header
    {
        "file": "core/crypto/security_token.h",
        "operations": [
            {
                "type": "create_file",
                "description": "Create security token header",
                "content": [
                    "#ifndef SECURITY_TOKEN_H",
                    "#define SECURITY_TOKEN_H",
                    "",
                    "#include \"core/typedefs.h\"",
                    "",
                    "namespace Security {",
                    f"    //Security Token: {token_hex}",
                    f"    static const uint8_t TOKEN[32] = {{ {token_c_array} }};",
                    "};",
                    "",
                    "#endif // SECURITY_TOKEN_H"
                ]
            }
        ]
    },
    # Step 1: Magic Header Modification (Packed)
    {
        "file": "core/io/file_access_pack.h",
        "operations": [
            {
                "type": "replace_line",
                "description": "Modify Packed File Header Magic",
                "find": "#define PACK_HEADER_MAGIC 0x43504447",
                "replace": f"#define PACK_HEADER_MAGIC {baseHeader}  // Generated Tag: \"{baseTag}\""
            }
        ]
    },
    # Step 2: Magic Header Modification (Encrypted)
    {
        "file": "core/io/file_access_encrypted.h",
        "operations": [
            {
                "type": "replace_line",
                "description": "Modify Encrypted File Header Magic",
                "find": "#define ENCRYPTED_HEADER_MAGIC 0x43454447",
                "replace": f"#define ENCRYPTED_HEADER_MAGIC {encHeader}  // Generated Tag: \"{encTag}\""
            }
        ]
    },
    # Step 3: Replace AES with Camellia (Decrypt) + Token Integration
    {
        "file": "core/io/file_access_encrypted.cpp",
        "operations": [
            {
                "type": "insert_after",
                "description": "Include security token header",
                "find": "#include \"file_access_encrypted.h\"",
                "replace": "#include \"core/crypto/security_token.h\""
            },
            {
                "type": "replace_block",
                "description": "Add token obfuscation for decryption",
                "find": [
                    "{",
                    "CryptoCore::AESContext ctx;",
                    "",
                    "ctx.set_encode_key(key.ptrw(), 256); // Due to the nature of CFB, same key schedule is used for both encryption and decryption!",
                    "ctx.decrypt_cfb(ds, iv.ptrw(), data.ptrw(), data.ptrw());",
                    "}"
                ],
                "replace": [
                    "{",
                    "CryptoCore::CamelliaContext ctx;",
                    "",
                    "    // Apply security token to key",
                    "    Vector<uint8_t> token_key;",
                    "    token_key.resize(32);",
                    "    const uint8_t *key_ptr = key.ptr();",
                    "    for (int i = 0; i < 32; i++) {",
                    "        token_key.write[i] = key_ptr[i] ^ Security::TOKEN[i];",
                    "    }",
                    "",
                    "    ctx.set_encode_key(token_key.ptrw(), 256);",
                    "    ctx.decrypt_cfb(ds, iv.ptrw(), data.ptrw(), data.ptrw());",
                    "}"
                ]
            }
        ]
    },
    # Step 4: Replace AES with Camellia (Encrypt) + Token Integration
    {
        "file": "core/io/file_access_encrypted.cpp",
        "operations": [
            {
                "type": "replace_block",
                "description": "Add token obfuscation for encryption",
                "find": [
                    "CryptoCore::AESContext ctx;",
                    "ctx.set_encode_key(key.ptrw(), 256);",
                    "",
                    "if (use_magic) {",
                    "file->store_32(ENCRYPTED_HEADER_MAGIC);",
                    "}",
                    "",
                    "file->store_buffer(hash, 16);",
                    "file->store_64(data.size());",
                    "file->store_buffer(iv.ptr(), 16);",
                    "",
                    "ctx.encrypt_cfb(len, iv.ptrw(), compressed.ptrw(), compressed.ptrw());"
                ],
                "replace": [
                    "CryptoCore::CamelliaContext ctx;",
                    "",
                    "    // Apply security token to key",
                    "    Vector<uint8_t> token_key;",
                    "    token_key.resize(32);",
                    "    const uint8_t *key_ptr = key.ptr();",
                    "    for (int i = 0; i < 32; i++) {",
                    "        token_key.write[i] = key_ptr[i] ^ Security::TOKEN[i];",
                    "    }",
                    "",
                    "    ctx.set_encode_key(token_key.ptrw(), 256);",
                    "",
                    "if (use_magic) {",
                    "file->store_32(ENCRYPTED_HEADER_MAGIC);",
                    "}",
                    "",
                    "file->store_buffer(hash, 16);",
                    "file->store_64(data.size());",
                    "file->store_buffer(iv.ptr(), 16);",
                    "",
                    "ctx.encrypt_cfb(len, iv.ptrw(), compressed.ptrw(), compressed.ptrw());"
                ]
            }
        ]
    },
    # Step 5: Add Camellia Class
    {
        "file": "core/crypto/crypto_core.h",
        "operations": [
            {
                "type": "insert_after",
                "description": "Add CamelliaContext class",
                "find": "};",
                "replace": [
                    "// Camellia-256 (via Mbed TLS)",
                    "class CamelliaContext {",
                    "private:",
                    "    void *ctx = nullptr;",
                    "",
                    "public:",
                    "    CamelliaContext();",
                    "    ~CamelliaContext();",
                    "",
                    "    Error set_encode_key(const uint8_t *p_key, size_t p_bits);",
                    "    Error set_decode_key(const uint8_t *p_key, size_t p_bits);",
                    "    Error encrypt_ecb(const uint8_t p_src[16], uint8_t r_dst[16]);",
                    "    Error decrypt_ecb(const uint8_t p_src[16], uint8_t r_dst[16]);",
                    "    Error encrypt_cbc(size_t p_length, uint8_t r_iv[16], const uint8_t *p_src, uint8_t *r_dst);",
                    "    Error decrypt_cbc(size_t p_length, uint8_t r_iv[16], const uint8_t *p_src, uint8_t *r_dst);",
                    "    Error encrypt_cfb(size_t p_length, uint8_t p_iv[16], const uint8_t *p_src, uint8_t *r_dst);",
                    "    Error decrypt_cfb(size_t p_length, uint8_t p_iv[16], const uint8_t *p_src, uint8_t *r_dst);",
                    "};",
                    ""
                ]
            }
        ]
    },
    # Step 6: Add Camellia Implementation
    {
        "file": "core/crypto/crypto_core.cpp",
        "operations": [
            {
                "type": "insert_after",
                "description": "Add Camellia include",
                "find": "#include <mbedtls/aes.h>",
                "replace": "#include <mbedtls/camellia.h>"
            },
            {
                "type": "append",
                "description": "Add Camellia implementation",
                "replace": [
                    "// ----------------------------------------------------------------",
                    "// Camellia-256 implementation",
                    "",
                    "CryptoCore::CamelliaContext::CamelliaContext() {",
                    "    ctx = memalloc(sizeof(mbedtls_camellia_context));",
                    "    mbedtls_camellia_init((mbedtls_camellia_context *)ctx);",
                    "}",
                    "",
                    "CryptoCore::CamelliaContext::~CamelliaContext() {",
                    "    mbedtls_camellia_free((mbedtls_camellia_context *)ctx);",
                    "    memfree(ctx);",
                    "}",
                    "",
                    "Error CryptoCore::CamelliaContext::set_encode_key(const uint8_t *p_key, size_t p_bits) {",
                    "    int ret = mbedtls_camellia_setkey_enc((mbedtls_camellia_context *)ctx, p_key, p_bits);",
                    "    return ret ? FAILED : OK;",
                    "}",
                    "",
                    "Error CryptoCore::CamelliaContext::set_decode_key(const uint8_t *p_key, size_t p_bits) {",
                    "    int ret = mbedtls_camellia_setkey_dec((mbedtls_camellia_context *)ctx, p_key, p_bits);",
                    "    return ret ? FAILED : OK;",
                    "}",
                    "",
                    "Error CryptoCore::CamelliaContext::encrypt_ecb(const uint8_t p_src[16], uint8_t r_dst[16]) {",
                    "    int ret = mbedtls_camellia_crypt_ecb((mbedtls_camellia_context *)ctx, MBEDTLS_CAMELLIA_ENCRYPT, p_src, r_dst);",
                    "    return ret ? FAILED : OK;",
                    "}",
                    "",
                    "Error CryptoCore::CamelliaContext::decrypt_ecb(const uint8_t p_src[16], uint8_t r_dst[16]) {",
                    "    int ret = mbedtls_camellia_crypt_ecb((mbedtls_camellia_context *)ctx, MBEDTLS_CAMELLIA_DECRYPT, p_src, r_dst);",
                    "    return ret ? FAILED : OK;",
                    "}",
                    "",
                    "Error CryptoCore::CamelliaContext::encrypt_cbc(size_t p_length, uint8_t r_iv[16], const uint8_t *p_src, uint8_t *r_dst) {",
                    "    int ret = mbedtls_camellia_crypt_cbc((mbedtls_camellia_context *)ctx, MBEDTLS_CAMELLIA_ENCRYPT, p_length, r_iv, p_src, r_dst);",
                    "    return ret ? FAILED : OK;",
                    "}",
                    "",
                    "Error CryptoCore::CamelliaContext::decrypt_cbc(size_t p_length, uint8_t r_iv[16], const uint8_t *p_src, uint8_t *r_dst) {",
                    "    int ret = mbedtls_camellia_crypt_cbc((mbedtls_camellia_context *)ctx, MBEDTLS_CAMELLIA_DECRYPT, p_length, r_iv, p_src, r_dst);",
                    "    return ret ? FAILED : OK;",
                    "}",
                    "",
                    "Error CryptoCore::CamelliaContext::encrypt_cfb(size_t p_length, uint8_t p_iv[16], const uint8_t *p_src, uint8_t *r_dst) {",
                    "    size_t iv_off = 0;",
                    "    int ret = mbedtls_camellia_crypt_cfb128((mbedtls_camellia_context *)ctx, MBEDTLS_CAMELLIA_ENCRYPT, p_length, &iv_off, p_iv, p_src, r_dst);",
                    "    return ret ? FAILED : OK;",
                    "}",
                    "",
                    "Error CryptoCore::CamelliaContext::decrypt_cfb(size_t p_length, uint8_t p_iv[16], const uint8_t *p_src, uint8_t *r_dst) {",
                    "    size_t iv_off = 0;",
                    "    int ret = mbedtls_camellia_crypt_cfb128((mbedtls_camellia_context *)ctx, MBEDTLS_CAMELLIA_DECRYPT, p_length, &iv_off, p_iv, p_src, r_dst);",
                    "    return ret ? FAILED : OK;",
                    "}"
                ]
            }
        ]
    }
]

def apply_modifications(root_dir):
    print_info(f"Randomly Generated PACK_HEADER_MAGIC : {baseHeader} //Generated Tag : {baseTag}")
    print_info(f"Randomly Generated ENCRYPTED_HEADER_MAGIC : {encHeader} //Generated Tag : {encTag}")
    print_info(f"Security Token: {token_hex}")
    step = 0
    for mod in MODIFICATIONS:
        file_path = os.path.join(root_dir, mod["file"])
        step += 1
        
        # Handle file creation separately
        if any(op.get("type") == "create_file" for op in mod["operations"]):
            print_info(f"Step {step} (Creating: {file_path}):")
            for op in mod["operations"]:
                if op["type"] == "create_file":
                    print_operation(f"Operation: {op['description']}")
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    
                    if os.path.exists(file_path):
                        print_warning(f"File already exists: {file_path}")
                        choice = input("   Do you want to overwrite it? (y/n): ").strip().lower()
                        if not (choice == 'y' or choice == 'yes'):
                            global fileCreated
                            print_operation("Skipping file creation.")
                            fileCreated = False
                            continue

                        # Backup existing file
                        global backup_path
                        backup_path = file_path + ".backup"
                        try:
                            os.replace(file_path, backup_path)
                            print_operation(f"Backup created at: {backup_path}")
                        except Exception as e:
                            print_error(f"Failed to create backup: {e}")
                            print_operation("Skipping file creation.")
                            fileCreated = False
                            continue

                    try:
                        with open(file_path, "w") as f:
                            content = op["content"]
                            if isinstance(content, list):
                                content = "\n".join(content)
                            f.write(content)
                        print_success(f"File created: {file_path}")
                    except Exception as e:
                        print_error(f"Failed to write file: {e}")
            continue

        
        # Handle file modifications
        if not os.path.exists(file_path):
            print_error(f"File not found: {file_path}")
            continue
            
        print_info(f"Step {step} (Processing: {file_path}):")
        
        with open(file_path, "r") as f:
            lines = f.readlines()

        modified = False
        for op in mod["operations"]:
            op_type = op["type"]
            description = op.get("description", "")
            print_operation(f"Operation: {description}. (Type: {op_type})")

            if op_type == "replace_line":
                find = op["find"].strip()
                replace = op["replace"] + "\n"
                found = False

                for i in range(len(lines)):
                    if lines[i].strip() == find:
                        lines[i] = replace
                        print_success(f"Line replaced at line {i+1}")
                        found = True
                        modified = True
                        break

                if not found:
                    print_error(f"Target line not found: {find}")

            elif op_type == "replace_block":
                find_lines = [ln.strip() for ln in op["find"]]
                replace_lines = [ln + "\n" for ln in op["replace"]]
                block_found = False

                for i in range(len(lines) - len(find_lines) + 1):
                    match = True
                    for j in range(len(find_lines)):
                        if lines[i + j].strip() != find_lines[j]:
                            match = False
                            break
                    if match:
                        lines[i:i + len(find_lines)] = replace_lines
                        print_success(f"Block replaced starting at line {i+1}")
                        modified = True
                        block_found = True
                        break

                if not block_found:
                    print_error("Target block not found")

            elif op_type == "insert_after":
                find = op["find"].strip()
                replace_lines = [ln + "\n" for ln in op["replace"]] if isinstance(op["replace"], list) else [op["replace"] + "\n"]
                found = False

                for i in range(len(lines)):
                    if lines[i].strip() == find:
                        # Check if replacement already exists
                        already_present = True
                        for j, rep_line in enumerate(replace_lines):
                            if i + 1 + j >= len(lines) or lines[i + 1 + j] != rep_line:
                                already_present = False
                                break
                        
                        if not already_present:
                            lines[i+1:i+1] = replace_lines
                            print_success(f"Inserted after line {i+1}")
                            modified = True
                        else:
                            print_success("Content already present, skipping insertion")
                        found = True
                        break

                if not found:
                    print_error(f"Insertion point not found: {find}")

            elif op_type == "append":
                replace_lines = [ln + "\n" for ln in op["replace"]]
                already_present = False

                # Check if the ending lines match
                if len(lines) >= len(replace_lines):
                    already_present = all(
                        lines[-len(replace_lines) + i] == replace_lines[i]
                        for i in range(len(replace_lines))
                    )

                if not already_present:
                    lines.extend(replace_lines)
                    print_success("Appended to end of file")
                    modified = True
                else:
                    print_success("Content already present at end, skipping append")

        if modified:
            with open(file_path, "w") as f:
                f.writelines(lines)
            print_success(f"File updated: {file_path}")
        else:
            print_warning(f"No changes made to file (Step {step})")

if __name__ == "__main__":
    if len(sys.argv) == 1:
        # No argument provided, use current directory
        godot_root = os.getcwd()
        print("\nNo directory specified. Using current directory as Godot Source Root.")
    elif len(sys.argv) == 2:
        # One argument provided, use it as Godot root
        godot_root = sys.argv[1]
    else:
        # Too many arguments provided
        print("\nUsage: python Godot_Secure.py <godot_source_root>")
        exit = input("\nPress Enter key to exit...")
        sys.exit(1)
        

    # Check for required Godot source components
    core_dir = os.path.join(godot_root, "core")
    sconstruct_file = os.path.join(godot_root, "SConstruct")

    if not (os.path.isdir(core_dir) and os.path.isfile(sconstruct_file)):
        print(f"{LogColors.FAIL}Error: No valid Godot Source Detected in the Specified Directory.{LogColors.ENDC}")
        exit = input("\nPress Enter key to exit...")
        sys.exit(1)

    print(f"\nUsing Godot Source Root: {godot_root}")
    confirm = input(f"\n\n ⚠   {LogColors.WARNING}Start Godot Secure Operations on Godot Source Root {LogColors.ENDC}{LogColors.FAIL}(y/n)?{LogColors.ENDC}: ").strip().lower()
    if not (confirm == 'y' or confirm == 'yes'):
        print("Closing Setup...")
        exit = input("\nPress Enter key to exit...")
        sys.exit(1)
        
    print(f"\n\n{LogColors.HEADER}=== Applying Camellia Encryption For Godot ==={LogColors.ENDC}")
    apply_modifications(godot_root)
    print(f"\n{LogColors.HEADER}=== Operation Complete (View Logs For Info) ==={LogColors.ENDC}\n")
    if fileCreated == True:
        print(f"{LogColors.BOLD} Security Token:{LogColors.ENDC} {token_hex}")
        print_warning(f"{LogColors.WARNING} Keep this token secret - it's required for decryption!{LogColors.ENDC}")
        print_success(f"{LogColors.OKGREEN} Build is now cryptographically unique{LogColors.ENDC}")
        if not (backup_path == None):
            print_info(f"{LogColors.OKGREEN} Old Key Backup created at: {LogColors.ENDC}{LogColors.BOLD}{backup_path}{LogColors.ENDC}\n")
    
    exit = input("\nPress Enter key to exit...")
    sys.exit(1)
