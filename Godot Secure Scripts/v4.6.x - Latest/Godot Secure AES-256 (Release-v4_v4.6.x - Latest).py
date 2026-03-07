import os
import sys
import random
import string
import binascii
import secrets
import datetime

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

def hex_to_bytes(hex_string: str) -> bytes:
    return bytes.fromhex(hex_string)

def generate_magic_header(tag: str, endian='little') -> str:
    if len(tag) != 4:
        raise ValueError("Tag must be exactly 4 characters.")
    
    if endian == 'little':
        tag = tag[::-1]  # Reverse for little-endian

    hex_value = "0x" + ''.join(f"{ord(c):02X}" for c in tag)
    return hex_value

def build_random_key_derivation():
    operands = ["key_ptr[i]", "Security::TOKEN[i]"]

    base_ops = [
        "({a} ^ {b})",
        "({a} + {b})",
        "({a} | {b})",
        "({a} & {b})",
        "(({a} << {shift}) | ({a} >> {rshift}))",
        "(({a} ^ {b}) + {const})",
        "(({a} + {b}) ^ {const})",
    ]

    chain_ops = [
        "({expr} ^ {value})",
        "({expr} + {value})",
        "({expr} | {value})",
        "(({expr} << {shift}) | ({expr} >> {rshift}))",
        "(({expr} ^ {value}) + {const})",
        "(({expr} + {value}) ^ {const})",
    ]

    def rotation():
        shift = secrets.randbelow(7) + 1
        return shift, 8 - shift

    def rand_const():
        return secrets.randbelow(255) + 1  # never zero

    layers = secrets.randbelow(5) + 2

    a = secrets.choice(operands)
    b = operands[1] if a == operands[0] else operands[0]
    shift, rshift = rotation()

    expression = secrets.choice(base_ops).format(a=a,b=b,shift=shift,rshift=rshift,const=rand_const())

    for _ in range(layers - 1):
        shift, rshift = rotation()
        value = secrets.choice(operands)

        # never allow identical cancellation
        if value == expression:
            value = secrets.choice(operands)

        expression = secrets.choice(chain_ops).format(expr=expression,value=value,shift=shift,rshift=rshift,const=rand_const())

    return f"token_key.write[i] = (uint8_t)({expression});"

def save_log(message):
    if not str(message).find("\033[") > 0:
        with open(logFileName,"a", encoding="utf-8") as logf: logf.write(f"{message}\n")
    return message

def print_success(message):
    save_log(f"      [✓] {message}")
    print(f"{LogColors.OKGREEN}      ✓{LogColors.ENDC} {message}")

def print_error(message):
    save_log(f"      [✗] {message}\n")
    print(f"{LogColors.FAIL}      ✗{LogColors.ENDC} {message}")

def print_info(message):
    save_log(f"\n[INFO] -   {message}")
    print(f"\n{LogColors.OKBLUE} ℹ {LogColors.ENDC} {message}")
    
def print_operation(message):
    save_log(f"   [=>] {message}")
    print(f"{LogColors.HEADER}   =>{LogColors.ENDC} {message}")

def print_warning(message):
    save_log(f"\n[WARN] -   {message}")
    print(f"\n{LogColors.WARNING} ⚠ {LogColors.ENDC} {message}")


# Generate unique identifiers
global godot_root
global encKey

baseTag = generate_random_tag()
encTag = generate_random_tag()
security_token = generate_random_token()
token_hex = binascii.hexlify(security_token).decode('utf-8')
token_c_array = ', '.join([f'0x{b:02X}' for b in security_token])
baseHeader = generate_magic_header(baseTag)
encHeader = generate_magic_header(encTag)
key_derivation_algorithm = "token_key.write[i] = key_ptr[i] ^ Security::TOKEN[i];"

fileCreated = True
backup_path = None
current_dt = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")
logFileName = f"Log-{current_dt}-Godot-Secure-AES.txt"


# Start Script Startup Operations
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
    try:
        exit = input("\nPress Enter key to exit...")
    except EOFError:
        pass
    sys.exit(1)
    

# Log File Creation
with open(logFileName, "w", encoding="utf-8") as logf: logf.write(f"Created On - {current_dt}\nThis is Godot-Secure Log file, SAVE IT to secure place for later getting values.\n\n")

# Check for required Godot source components
core_dir = os.path.join(godot_root, "core")
sconstruct_file = os.path.join(godot_root, "SConstruct")

# Get Current Encryption Key From Enviroment
try:
    encKey = os.environ["SCRIPT_AES256_ENCRYPTION_KEY"]
except:
    encKey = "Can't Fetch Your Enviroment Variable \"SCRIPT_AES256_ENCRYPTION_KEY\""

if not (os.path.isdir(core_dir) and os.path.isfile(sconstruct_file)):
    print(f"{LogColors.FAIL}{save_log("Error: No valid Godot Source Detected in the Specified Directory.")}{LogColors.ENDC}")
    try:
        exit = input("\nPress Enter key to exit...")
    except EOFError:
        pass
    sys.exit(1)

print(save_log(f"\nUsing Godot Source Root: {godot_root}"))
confirm = input(f"\n\n ⚠   {LogColors.WARNING}Start Godot Secure Operations on Godot Source Root {LogColors.ENDC}{LogColors.FAIL}(y/n)?{LogColors.ENDC}: ").strip().lower()
if not (confirm == 'y' or confirm == 'yes'):
    print(save_log("Closing Setup..."))
    try:
        exit = input("\nPress Enter key to exit...")
    except EOFError:
        pass
    sys.exit(1)
    
save_log(f"Start Godot Secure Operations on Godot Source Root (y/n)?: {confirm}")

confirm = input(f"\n\n ℹ  {LogColors.OKBLUE}Use Custom Headers {LogColors.ENDC}{LogColors.FAIL}(y/n)?{LogColors.ENDC}: ").strip().lower()
save_log(f"\n[INFO] - Use Custom Headers (y/n)?: {confirm}")
if (confirm == 'y' or confirm == 'yes'):
    baseTag = input("    Enter Custom Magic Header (e.g. GDPC): ").upper()
    baseHeader = generate_magic_header(baseTag)
    encTag = input("    Enter Custom Encrypted Magic Header (e.g. GDEC): ").upper()
    encHeader = generate_magic_header(encTag)
    save_log(f"    Enter Custom Magic Header (e.g. GDPC): {baseTag}\n    Enter Custom Encrypted Magic Header (e.g. GDEC): {encTag}")

confirm = input(f"\n\n ℹ  {LogColors.OKBLUE}Use Custom Token {LogColors.ENDC}{LogColors.FAIL}(y/n)?{LogColors.ENDC}: ").strip().lower()
save_log(f"\n[INFO] - Use Custom Token (y/n)?: {confirm}")
if (confirm == 'y' or confirm == 'yes'):
    token_hex = str(input("    Enter Custom Security Token: ")).lower()
    security_token = hex_to_bytes(token_hex)
    token_c_array = ', '.join([f'0x{b:02X}' for b in security_token])
    save_log(f"    Enter Custom Security Token: {token_hex}")

confirm = input(f"\n\n ℹ  {LogColors.OKBLUE}Use Advanced Key Derivation {LogColors.ENDC}{LogColors.FAIL}(y/n)?{LogColors.ENDC}: ").strip().lower()
save_log(f"\n[INFO] - Use Advanced Key Derivation (y/n)?: {confirm}")
if (confirm == 'y' or confirm == 'yes'):
    key_derivation_algorithm = build_random_key_derivation()
    save_log(f"    Generated Advanced Key Derivation Algorithm:\n            {key_derivation_algorithm}")

# Modifications to be made in source
MODIFICATIONS = [
    #Pre -Steps:
    {
        "file": "version.py",
        "operations": [
            {
                "type": "replace_line",
                "description": "Modify Godot title To add Godot Secure",
                "find": "name = \"Godot Engine\"",
                "replace": "name = \"Godot Engine (With Godot Secure)\""
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
                "replace": "set_title(TTR(\"Export With Godot Secure (AES-256)\"));"
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
    # Step 3: Modify AES Decryption + Token Integration
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
                    "CryptoCore::AESContext ctx;",
                    "",
                    "    // Apply security token to key",
                    "    Vector<uint8_t> token_key;",
                    "    token_key.resize(32);",
                    "    const uint8_t *key_ptr = key.ptr();",
                    "    for (int i = 0; i < 32; i++) {",
                    f"        {key_derivation_algorithm}",
                    "    }",
                    "",
                    "    ctx.set_encode_key(token_key.ptrw(), 256); // Due to the nature of CFB, same key schedule is used for both encryption and decryption!",
                    "    ctx.decrypt_cfb(ds, iv.ptrw(), data.ptrw(), data.ptrw());",
                    "}"
                ]
            }
        ]
    },
    # Step 4: Modify AES Encryption + Token Integration
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
                    "    file->store_32(ENCRYPTED_HEADER_MAGIC);",
                    "}",
                    "",
                    "file->store_buffer(hash, 16);",
                    "file->store_64(data.size());",
                    "file->store_buffer(iv.ptr(), 16);",
                    "",
                    "ctx.encrypt_cfb(len, iv.ptrw(), compressed.ptr(), compressed.ptr());"
                ],
                "replace": [
                    "CryptoCore::AESContext ctx;",
                    "",
                    "    // Apply security token to key",
                    "    Vector<uint8_t> token_key;",
                    "    token_key.resize(32);",
                    "    const uint8_t *key_ptr = key.ptr();",
                    "    for (int i = 0; i < 32; i++) {",
                    f"        {key_derivation_algorithm}",
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
                    "ctx.encrypt_cfb(len, iv.ptrw(), compressed.ptr(), compressed.ptr());"
                ]
            }
        ]
    }
]

def apply_modifications(root_dir):
    print_info(f"Generated PACK_HEADER_MAGIC : {baseHeader} //Tag : {baseTag}")
    print_info(f"Generated ENCRYPTED_HEADER_MAGIC : {encHeader} //Tag : {encTag}")
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
    print(f"\n\n{LogColors.HEADER}{save_log("\n=== Applying Enhanced AES Encryption For Godot ===")}{LogColors.ENDC}")
    apply_modifications(godot_root)
    print(f"\n{LogColors.HEADER}=== Operation Complete (View Logs For Info) ==={LogColors.ENDC}\n")
    if fileCreated == True:
        print(f"{LogColors.BOLD} Security Token:{LogColors.ENDC} {token_hex}\n")
        print(f"{LogColors.WARNING} Encryption Key: {LogColors.FAIL}{encKey}{LogColors.ENDC}")
        print_warning(f"{LogColors.WARNING} Security Token and Encryption Key are different. Use {LogColors.FAIL}\"Encryption Key\"{LogColors.WARNING} During Export!{LogColors.ENDC}")
        print_success(f"{LogColors.OKGREEN} Build is now Cryptographically Unique{LogColors.ENDC}")
        save_log(f"\nSecurity Token: {token_hex}\nEncryption Key: {encKey}")
        save_log(f"\n[WARN] - Security Token and Encryption Key are different. Use Encryption Key During Export!")
        if not (backup_path == None):
            save_log(f"\n[INFO] - Old Key Backup Created at: {backup_path}")
            print_info(f"{LogColors.OKGREEN} Old Key Backup Created at: {LogColors.ENDC}{LogColors.BOLD}{backup_path}{LogColors.ENDC}\n")
    
    try:
        exit = input("\nPress Enter key to exit...")
    except EOFError:
        pass
    sys.exit(1)
