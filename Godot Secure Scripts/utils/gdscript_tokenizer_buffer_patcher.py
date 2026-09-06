# THIS FILE IS PART OF GODOT-SECURE PROJECT
# This script is used to patch gdscript_tokenizer_buffer.cpp to scramble the token mapping for security purposes.

import os
import sys
import re
import random
import secrets
import hashlib

class LogColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def generate_random_gdtokenizer_seed(length: int = 64) -> str:
    
    # secrets.token_hex(n) returns a string of 2 * n hex characters
    return secrets.token_hex(length // 2)

def get_actual_tk_max(tokenizer_h_path):
    if not os.path.exists(tokenizer_h_path):
        raise FileNotFoundError(f"Could not locate gdscript_tokenizer.h at: {tokenizer_h_path}")

    with open(tokenizer_h_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Locate the enum Type block
    match = re.search(r"enum\s+Type\s*\{([\s\S]*?)\bTK_MAX\b", content)
    if not match:
        raise ValueError("Could not find 'enum Type' containing 'TK_MAX' in gdscript_tokenizer.h")

    body = re.sub(r"//.*", "", match.group(1))
    tokens = [item.strip() for item in body.split(",") if item.strip()]
    return len(tokens)


def apply_buffer_scramble(filepath, buffer_seed):
    
    seed_hash = int(hashlib.md5(buffer_seed.encode()).hexdigest(), 16)
    random.seed(seed_hash)
    
    if not os.path.exists(filepath):
        print(f"File not found at {filepath}")
        return False
    
    # Locate gdscript_tokenizer.h in the same directory
    dir_name = os.path.dirname(filepath)
    tokenizer_h_path = os.path.join(dir_name, "gdscript_tokenizer.h")

    try:
        actual_tk_max = get_actual_tk_max(tokenizer_h_path)
        print(f"Auto-detected Token::TK_MAX = {actual_tk_max}")
    except Exception as e:
        print(f"Error parsing TK_MAX: {e}")
        return False

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Create Backup of the original file
    backup_path = filepath + ".backup"
    try:
        with open(backup_path, 'w', encoding='utf-8') as backup_file:
            backup_file.write(content)
        print(f"Backup created at: {backup_path}")
    except Exception as e:
        print(f"Failed to create backup: {e}")

    # 1. Total buffer capacity is 128 to match TOKEN_MASK
    buffer_capacity = 128
    if actual_tk_max > buffer_capacity:
        print(f"TK_MAX ({actual_tk_max}) exceeds TOKEN_MASK limit (127).")
        return False

    # We only shuffle tokens from 1 to actual_tk_max - 1.
    active_tokens = list(range(1, actual_tk_max))
    random.shuffle(active_tokens)

    # 3. Reconstruct the full scrambled list with 0 pinned at the start
    scrambled_tokens = [0] + active_tokens

    # 4. Fill the remainder up to 128 with identity mappings
    unused_padding = list(range(actual_tk_max, buffer_capacity))
    scrambled_tokens += unused_padding

    # 5. Construct the inverse map
    inverse_map = [0] * buffer_capacity
    for orig, scram in enumerate(scrambled_tokens):
        inverse_map[scram] = orig

    write_map_str = "static const uint8_t token_write_map[] = {" + ", ".join(map(str, scrambled_tokens)) + "};"
    read_map_str = "static const uint8_t token_read_map[] = {" + ", ".join(map(str, inverse_map)) + "};"
    map_injection = (
        f"\n// Godot-Secure: Injected Token Maps (Auto-detected TK_MAX = {actual_tk_max})\n"
        f"{write_map_str}\n{read_map_str}\n"
    )

    # 6. Inject Maps
    version_pattern = r"(#define TOKENIZER_VERSION \d+)"
    include_pattern = r'(#include\s+["<]gdscript_tokenizer_buffer\.h[">])'

    if re.search(version_pattern, content):
        content = re.sub(version_pattern, r"\1\n" + map_injection, content, count=1)
    elif re.search(include_pattern, content):
        content = re.sub(include_pattern, r"\1\n" + map_injection, content, count=1)
    else:
        print("Could not find suitable injection point (neither TOKENIZER_VERSION nor header include found).")
        return False

    # 7. Scramble Write Stream
    target_write = "int token_type = p_token.type & TOKEN_MASK;"
    replace_write = "int token_type = token_write_map[p_token.type] & TOKEN_MASK;"
    if target_write not in content:
        print("Could not find write stream target.")
        return False
    content = content.replace(target_write, replace_write)

    # 8. Scramble Read Stream
    target_read = "token.type = (Token::Type)(token_type & TOKEN_MASK);"
    replace_read = "token.type = (Token::Type)token_read_map[token_type & TOKEN_MASK];"
    if target_read not in content:
        print("Could not find read stream target.")
        return False
    content = content.replace(target_read, replace_read)

    # 9. Save the modified file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    print("Successfully patched gdscript_tokenizer_buffer.cpp!")
    print(f"Used Randomizer Tokenizer Seed: {buffer_seed}")
    print(f"\n[✓] Generated Write Map: {write_map_str}\n\n[✓] Generated Read Map: {read_map_str}")
    return True

if __name__ == "__main__":
    if len(sys.argv) == 1:
        godot_root = os.getcwd()
        print("\nNo directory specified. Using current directory as Godot Source Root.")
    elif len(sys.argv) == 2:
        godot_root = sys.argv[1]
    else:
        print("\nUsage: python Godot_Secure.py <godot_source_root>")
        sys.exit(1)
    
    gdtokenizer_seed = generate_random_gdtokenizer_seed()
    confirm = input(f"\n[ℹ]  {LogColors.OKBLUE}Randomize GDScript Tokenizer [READ DOCUMENTATION]{LogColors.ENDC}{LogColors.FAIL}(y/n)?{LogColors.ENDC}: ").strip().lower()
    if (confirm == 'y' or confirm == 'yes'):
        confirm = str(input(f"[ℹ] Use Custom Seed for Randomization{LogColors.FAIL}(y/n)?{LogColors.ENDC}: "))
        if (confirm == 'y' or confirm == 'yes'):
            gdtokenizer_seed = str(input("  Enter Custom Seed: "))
        apply_buffer_scramble(os.path.join(godot_root,"modules/gdscript/gdscript_tokenizer_buffer.cpp"),gdtokenizer_seed)
    
    print(f"\n\n{LogColors.OKGREEN}Now Compile both {LogColors.FAIL}Engine {LogColors.OKGREEN}and {LogColors.FAIL}Templates {LogColors.OKGREEN} and Export your game as usual!{LogColors.ENDC}\n")
    