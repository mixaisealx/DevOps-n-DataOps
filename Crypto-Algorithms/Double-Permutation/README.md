# Double Permutation Cipher Encryption and Decryption

You must implement a program that encrypts and decrypts text using a **double permutation cipher** based on two distinct keys and an optional custom alphabet.

This cipher rearranges the plaintext in a rectangular grid and performs two independent permutations - one by columns and one by rows - followed by reading the characters along diagonals to form the ciphertext.
The decryption reverses this process to restore the original text.

## Task Description

The program must read input data from a file named `input.txt`, process it according to the specified mode (encryption or decryption), and write the result to `output.txt`.
If the input data format is incorrect or contains invalid characters, the program must print:
```
Uncorrect input data!
```
and terminate gracefully.

## Cipher Rules

Let:
- $A$ be the alphabet string containing **unique** characters.
- $K_c$ be the **column key** and $K_r$ be the **row key**, each consisting of characters from $A$.
- $T$ be the text to encrypt or decrypt.

### Key Processing

Each key defines a permutation mask based on the lexicographic order of its characters:
- For encryption, characters of the key are sorted alphabetically, and their original indices define the permutation order.
- For decryption, the inverse mapping is used.

### Encryption Procedure

1. Compute the number of rows: $R = \left\lceil \frac{|T|}{|K_c|} \right\rceil$. If $|T|$ is not divisible by $|K_c|$, pad $T$ with random characters from $A$ to fill the last row.
2. Arrange the text into a matrix with $R$ rows and $|K_c|$ columns.
3. Apply the **row permutation** based on $K_r$ and the **column permutation** based on $K_c$.
4. Read the matrix diagonally from top-left to bottom-right:
   - First, read diagonals starting from the top row.
   - Then, read diagonals starting from the leftmost column (excluding the top-left corner already read).
5. The resulting string is the **ciphertext**.

### Decryption Procedure

1. Compute the number of rows: $R = \frac{|C|}{|K_c|}$ If this is not an integer, input is invalid.
2. Refill the matrix diagonally using the same reading order as encryption.
3. Apply the inverse row and column permutations.
4. Read the text row by row to reconstruct the plaintext.

## Input Format

The file `input.txt` must contain **4 or 5 lines**:
- Line **1**: operation mode - either `encrypt` or `decrypt`
- Line **2**: text to be processed
- Line **3**: first key (column key)
- Line **4**: second key (row key)
- Line **5** (optional): custom alphabet (must consist of unique characters)

If the alphabet is not provided, use the default alphabet:
```
ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789
```

## Output Format

The processed text (encrypted or decrypted) must be written to `output.txt` encoded in UTF-8. No extra spaces or line breaks are allowed.

## Example 1 (encryption)

**input.txt**
```
encrypt
HELLODOUBLE
KEY
WORD
ABCDEFGHIJKLMNOPQRSTUVWXYZ
```

**output.txt**
```
ELOHLDBUOLE
```

## Example 2 (decryption)

**input.txt**
```
decrypt
ELOHLDBUOLE
KEY
WORD
ABCDEFGHIJKLMNOPQRSTUVWXYZ
```

**output.txt**
```
HELLODOUBLE
```

## Example 3 (using the default alphabet)

**input.txt**
```
encrypt
Secret123
lock
door
```

**output.txt**
```
S3et21rce
```

## Validation Rules

The program must detect and reject invalid input if:
- The alphabet contains duplicate characters.
- Any character in the text or keys is not found in the alphabet.
- Either key is shorter than 2 characters.
- The total number of lines is not 4 or 5.
- During decryption, the ciphertext length is not divisible by the column-key length.

When invalid, print to the console:
```
Uncorrect input data!
```
and terminate execution.

## Constraints

- $1 \le |T| \le 10^6$
- $2 \le |K_c|, |K_r| \le 256$
- $2 \le |A| \le 256$
- Alphabet characters must be unique.
- All input data must be UTF-8 encoded.

## Notes

- Encryption and decryption must be exact inverses: applying decryption to the ciphertext must return the original text.
- Random padding characters during encryption can be arbitrary but must belong to the alphabet.
- The order of operations (column and row permutation, then diagonal traversal) must be strictly followed.
- Diagonal traversal begins at the top-left corner and alternates between column and row.

This assignment evaluates:
- Correct implementation of double permutation logic.
- Proper handling of file I/O and UTF-8 encoding.
- Error handling and input validation.

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
