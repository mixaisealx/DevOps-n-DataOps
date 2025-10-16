# Vigenere Cipher Encryption and Decryption

You must implement a program that encrypts or decrypts text using the **Vigenere cipher**, a variant of the classical Vigenère cipher generalized to an arbitrary alphabet. The cipher shifts each letter of the text by an amount determined by the position of a corresponding key character within the alphabet.

The alphabet is cyclic: after the last character, it continues from the beginning.

## Task Description

The program must read input data from a text file named `input.txt` and write the result to a file named `output.txt`.
Depending on the first input line, the program must either **encrypt** or **decrypt** the given text using the provided key and alphabet.

### Cipher rules

1. Let the alphabet be a string of unique characters `A` of length `L`.
2. Each character in the key defines a rotated version of the alphabet:
   - For key character `k`, find its position `p = A.indexOf(k)`.
   - The rotated alphabet for that key character is `A[p:] + A[:p]`.
3. For **encryption**:
   - For each character $c_i$ of the plaintext, find its index $j$ in `A`.
   - Replace it with the character at index $j$ of the current rotated alphabet.
   - After each substitution, advance to the next key character (cyclically).
4. For **decryption**, perform the inverse operation:
   - For each character $c_i$ of the ciphertext, find its position $j$ in the current rotated alphabet.
   - Replace it with the character at index $j$ in the original alphabet.
   - Advance through the key cyclically as in encryption.

If the alphabet is not given, use the default alphabet:
```
ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789
```

## Input Format

The file `input.txt` contain either 3 or 4 lines encoded in UTF-8:
- Line **1**: the operation mode - one of
   - `"encrypt"` – to encrypt the text, or
   - `"decrypt"` – to decrypt it.
- Line **2**: the text to process (string containing only alphabet characters).
- Line **3**: the key (non-empty string, characters must belong to the alphabet).
- Line **4** (optional): the alphabet to use (must contain only unique characters). If omitted, use the default alphabet.

If the number of lines or their contents are invalid, the program must output
`Uncorrect input data!` to the console and stop execution.

## Output Format

The resulting string after encryption or decryption must be written to `output.txt` encoded in UTF-8.

## Example 1 (encryption)

**input.txt**
```
encrypt
HELLO
KEY
ABCDEFGHIJKLMNOPQRSTUVWXYZ
```

**output.txt**
```
RIJVS
```

## Example 2 (decryption)

**input.txt**
```
decrypt
RIJVS
KEY
ABCDEFGHIJKLMNOPQRSTUVWXYZ
```

**output.txt**
```
HELLO
```

## Validation Rules

The program must:

- Print `"Uncorrect input data!"` if
  - the alphabet contains duplicate characters,
  - any character in the text or key is not in the alphabet, or
  - the file format is incorrect (wrong number of lines or invalid command).
- Process input and output files using **UTF-8** encoding.
- Handle both encryption and decryption symmetrically (i.e., decrypting an encrypted text must return the original text).

## Implementation Requirements

- Implement all logic inside a `static` class that provides two public methods:
  - `Encrypt(string data, string key, string alphabet)`
  - `Decrypt(string data, string key, string alphabet)`

### Constraints

- Input length $\leq 10^6$ characters.
- Key length $\geq 2$.
- Alphabet length $\leq 256$ characters.
- The alphabet must consist of unique characters only.

### Notes

- The encryption and decryption procedures must be exact inverses.
- The alphabet defines the complete character space - all text and key characters must belong to it.
- The key is used cyclically; when it ends, it repeats from the beginning.
- The cipher must preserve letter casing and support alphanumeric characters if using the default alphabet.

## How to Run

### Windows

1. Install the **.NET SDK** (minimum version **.NET 6.0**):
   Download from [https://dotnet.microsoft.com/download](https://dotnet.microsoft.com/download)
2. Save a code in a `*.cs` file inside a new folder.
3. Open **Command Prompt** or **PowerShell** in that folder and run (This creates and compiles a C# console project):
   ```
   dotnet new console --force
   dotnet build
   ```
4. Place `input.txt` in the same directory as the compiled binary (`bin/Debug/net6.0/`).
5. Run the program: `dotnet run`. The result will be written to `output.txt`.

### Linux

1. Open a terminal.
2. Install the **.NET SDK** (if not already installed):
   
   **Ubuntu / Debian:**
   ```
   sudo apt update
   sudo apt install dotnet-sdk-6.0
   ```
   **Fedora:**
   ```
   sudo dnf install dotnet-sdk-6.0
   ```
3. Save a code in a `*.cs` file inside a new folder.
4. In the terminal, compile and run:
   ```
   dotnet new console --force
   dotnet build
   dotnet run
   ```
5. Check the generated `output.txt` file in the same directory.

### Alternative (no SDK, only C# compiler)

If you only want to compile without a full SDK:

- **Windows (using CSC):**
  ```
  csc Program.cs
  Program.exe
  ```

- **Linux (Mono):**
  ```
  sudo apt install mono-devel
  mcs Program.cs
  mono Program.exe
  ```
