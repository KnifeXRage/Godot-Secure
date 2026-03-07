# Godot Secure - Enhanced Asset Protection For Godot
[![Godot Engine 4.x](https://img.shields.io/badge/Godot_Engine-4.x-blue)](https://godotengine.org/)
[![MIT License](https://img.shields.io/badge/license-MIT-blue)](https://github.com/KnifeXRage/Godot-Secure/blob/main/LICENSE)
<a href='https://ko-fi.com/V7V41FR21F' target='_blank'><img height='21' style='border:0px;height:21px;' src='https://storage.ko-fi.com/cdn/kofi5.png?v=6' border='0' alt='Buy Me a Coffee at ko-fi.com' /></a>

![Godot Secure Logo](/Logos/PNGs/Godot%20Secure.png)

## Description

**Godot Secure** is a Simple Python Script That modify the Godot Source Code Automatically, to integrate **Camellia-256 / AES-256** encryption with a **unique security token system**. This solution creates a cryptographically **unique engine build** that prevents generic decryption tools from accessing your game assets.

### *Effortless Security for Godot Games*
>This script enhances your Godot engine with Camellia/AES encryption and a unique security token system with just one command. Unlike standard encryption, this creates a custom Godot build that's cryptographically unique to you, preventing universal decryption tools from working with your game assets.

## Key Features

- 🎲 **Randomized Magic Headers**: Unique file signatures per engine's build (Not Game)
- 🔑 **Security Token System**: 32-byte token embedded directly in engine's binary
- 🛡️ **Per-Build Uniqueness**: Each compilation of engine and templates is cryptographically distinct from others
- ⚡ **Automated Setup**: One-command modification of Godot source
- 💾 **No external dependencies**: Everything included

## Difference

Standard Godot encryption has known vulnerabilities. Our solution:

| Feature | Standard Godot | Godot Secure |
|---------|----------------|--------------|
| Encryption Algorithm | AES-256 | Camellia-256 / AES-256 |
| Universal Decryption Tools | Vulnerable | **Protected** |
| Per Engine-Build Uniqueness | No | **Yes** |
| Key Obfuscation | No | **Yes** |
| Magic Header | Fixed | **Randomized** |
| Required Reverse Engineering | Generic | **Per-Build** |

## Requirements

1. **Godot Source Code** (4.x recommended)
2. **Python 3.6+**
3. **OpenSSL** (for key generation)
4. **Build Tools** (SCons, compilers)

## Download Godot Secure: 🔗[Download](https://github.com/KnifeXRage/Godot-Secure/releases/)


#### Pro Tip:
> Directly Run The Script inside Godot Source and Build your `Engine and Templates` as usual with encryption Key!!


## Installation & Usage

>Must Read Godot's Official Documentation:
>🔗[View Official Documentation](https://docs.godotengine.org/en/stable/contributing/development/compiling/index.html)

### Step 1: Prepare Environment
```bash
git clone https://github.com/godotengine/godot.git
cd godot
```

### Step 2: Generate Encryption Key

```bash
# Generate 256-bit key (KEEP THIS SECURE!)
openssl rand -hex 32 > godot.gdkey

## Set environment variable

# For Linux/macOS:
export SCRIPT_AES256_ENCRYPTION_KEY=$(cat godot.gdkey)

# For Windows (PowerShell):
$env:SCRIPT_AES256_ENCRYPTION_KEY = Get-Content godot.gdkey

# Or Set it Permanently from Control Panel (Windows)
```

### Step 3: Run Setup Script
> You Can the Script directly inside Godot Source folder without using arguments!
> Using: `python godot_secure.py`
```bash
# Run The Godot Secure Script
python godot_secure.py /path/to/godot_source/

#Example:
python godot_secure.py godot/
```

### Step 4: Compile Godot Engine and Export Templates
```bash
# For Engine (Must REQUIRED):
scons platform=windows target=editor use_mingw=yes # Example for Windows
scons platform=linuxbsd target=editor use_mingw=yes # Example for Linux BSD
scons platform=macos target=editor use_mingw=yes # Example for MacOS

# For Export Templates (Must REQUIRED):
scons platform=windows target=template_debug use_mingw=yes
scons platform=windows target=template_release use_mingw=yes
...

```
> Build others Templates like these too and use `platform=macos` or `platform=linuxbsd` to build for *MacOS* or *Linux BSD*, Also use `use_llvm=yes`  or `use_mingw=yes` for faster builds!


# How It Works

The script makes these key modifications:

1. **Unique Identifiers**
   - Generates random magic headers for file signatures
   - Creates security token embedded in engine binary

2. **Key Protection**
   - Without Advanced Key Derivation Enabled: 
       - `token_key.write[i] = key_ptr[i] ^ Security::TOKEN[i];`
         OR
         `Actual Key = (Input Key) XOR (Security Token)`
   - Token exists only in compiled binary
3. **If Advanced Key Derivation Enabled**
   - Script creates a long totally unique key derivation formula using different mathematical operations.
   - That formula will be used for both encryption and decryption and is totally unique each time you compile engine and templates with it.
   - Examples of some generated formulas using this algorithm:
      ```bash
      1. token_key.write[i] = (uint8_t)(((((key_ptr[i] & Security::TOKEN[i]) + key_ptr[i]) ^ 151) ^ key_ptr[i]));
      2. token_key.write[i] = (uint8_t)(((((((((key_ptr[i] ^ Security::TOKEN[i]) + key_ptr[i]) ^ 106) + key_ptr[i]) ^ 138) << 6) | ((((((key_ptr[i] ^ Security::TOKEN[i]) + key_ptr[i]) ^ 106) + key_ptr[i]) ^ 138) >> 2)) | Security::TOKEN[i]));
      3. token_key.write[i] = (uint8_t)(((((Security::TOKEN[i] & key_ptr[i]) + Security::TOKEN[i]) ^ Security::TOKEN[i]) ^ Security::TOKEN[i]));
      4. token_key.write[i] = (uint8_t)((((((((((((key_ptr[i] << 7) | (key_ptr[i] >> 1)) ^ Security::TOKEN[i]) + key_ptr[i]) ^ 242) << 2) | ((((((key_ptr[i] << 7) | (key_ptr[i] >> 1)) ^ Security::TOKEN[i]) + key_ptr[i]) ^ 242) >> 6)) + Security::TOKEN[i]) ^ 126) << 6) | ((((((((((key_ptr[i] << 7) | (key_ptr[i] >> 1)) ^ Security::TOKEN[i]) + key_ptr[i]) ^ 242) << 2) | ((((((key_ptr[i] << 7) | (key_ptr[i] >> 1)) ^ Security::TOKEN[i]) + key_ptr[i]) ^ 242) >> 6)) + Security::TOKEN[i]) ^ 126) >> 2)));
      ```
   - _NOTE:_ This may increase your Game Loading time a little bit but it will make your actual key `MUCH HARDER` to obtain using automated tools. And it will make your Engine build completely unique.

## Troubleshooting

**Script not working?**
- Ensure Python 3.6+ installed
- Verify correct Godot source path
- Run with absolute path if needed:  
  `python godot_secure.py /path/to/godot_source`

**Compilation errors?**
- Clean build: `scons --clean`
- Ensure all submodules: `git submodule update --init`
- Use `Godot-Secure` Script only once on _Godot Source Code_. Using script multiple times on same source code can cause **Compilation Errors!**. So, always refresh Your Godot source code before running the script on it.

### Common Issues
1. **File not found errors**: Ensure correct Godot source path
2. **Compilation errors**: Verify Mbed TLS is properly included
3. **Encryption/decryption mismatch**: Always use matching engine builds with matching template(s) builds

### Verification Steps
1. Check script output for success messages
2. Confirm `security_token.h` exists in `core/crypto/`
3. Search for `CamelliaContext / AESContext` in modified files
4. Verify magic header values in file headers

## Disclaimer

❗ **Use at Your Own Risk**  
This script modifies core Godot engine files. Always:
- Back up your source code before running
- Test builds thoroughly before deployment
- Maintain secure copies of security tokens
- Understand that enhanced security increases complexity

### Security Disclaimer

🪧 **Important Considerations**
   - This creates a **custom Godot engine**
   - Standard export templates won't work
   - Always test builds before deployment
   - Maintain backups of security tokens

### Rebuild Protocol
🔄 **Always rebuild when:**
   - Updating Godot source
   - Changing security parameters
   - Creating new game versions
   - Suspecting key compromise

# License
- MIT License - Free for Personal and Commercial use with attribution: 
🔗[View License](https://github.com/KnifeXRage/Godot-Secure/blob/main/LICENSE)
---

## 💖 Support Me
**Hi there! I'm a college student passionate about game development and programming. While this project will always remain free, your support would mean the world as I balance studies and financial challenges.**
- If you've found this security tool valuable, I'd sincerely appreciate any support as I work through my studies.

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/V7V41FR21F)

Every contribution helps maintain and improve this project. And encourage me to make more projects like this!

*This is optional support. The tool remains free and open-source regardless.*

---

**Created with ❤️ for Godot Developers**  
For contributions, please open issues on GitHub
