# Gamming Cipher Encryption and Decryption

You need to implement a simple **stream (gamma) cipher** that performs encryption and decryption using pseudorandom shifts over a custom alphabet.

The program must read input data from a file `input.txt` and write the result to `output.txt`.

## Cipher Algorithm

Given:
- A text string $T = t_1 t_2 \ldots t_n$.
- A key string $K$.
- An alphabet $A$ - a sequence of unique symbols.

The cipher uses the following steps:
1. Initialize a pseudorandom number generator with seed $S$.
2. For each character $t_i$ in $T$, obtain a pseudorandom integer $r_i$ in the range $[0, |A|)$.
3. Map each character $t_i$ to its index in the alphabet:
   $p_i = A.indexOf(t_i)$.
4. Compute the ciphertext character index for encryption: $c_i = (p_i + r_i) \bmod |A|$ and for decryption: $p_i = (c_i - r_i + |A|) \bmod |A|$
5. Convert indices back to characters using $A[c_i]$ or $A[p_i]$.

The resulting string is written to `output.txt`.

## Input Format

The file `input.txt` must contain:
- Line *1*: the operation mode - either `encrypt` or `decrypt`.
- Line *2*: the text to process.
- Line *3*: the key.
- Line *4* (optional): a custom alphabet. If omitted, the default alphabet is used:
  ```
  ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789
  ```

## Output Format

The program writes a single line - the encrypted or decrypted text to `output.txt`.

## Implementation Requirements

- Define a static class `Gamming` that implements both `Encrypt` and `Decrypt` methods.
- Validation must ensure:
  - The alphabet contains unique characters.
  - The key and text contain only symbols from the alphabet.
  - The key length is at least 2.
- The **CRC-32** algorithm must be used to seed the pseudorandom generator ($S$).
- The pseudorandom sequence must be identical for encryption and decryption with the same key and alphabet.

## Examples

### Example 1 (encryption)

**input.txt**
```
encrypt
HELLO
MySecretKey
```
**output.txt**
```
IpQQNr
```

### Example 2 (decryption)

**input.txt**
```
decrypt
IpQQNr
MySecretKey
ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789
```

**output.txt**
```
HELLO
```

## Notes

- The same key and alphabet must reproduce the identical pseudorandom gamma sequence.
- Any mismatch between text, key, and alphabet symbols must cause an exception.
- The implementation should be self-contained and require no network access or external resources.

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
