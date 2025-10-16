# Analytic Transform Cipher Encryption and Decryption

You need to implement an **analytic cipher** that performs encryption and decryption of text using matrix transformations defined by a square key.
The transformation operates over numeric representations of symbols within a custom alphabet.

The program must read input data from a file `input.txt` and write the result to `output.txt`.

## Cipher Algorithm

Given:
- A text string $T = t_1 t_2 \ldots t_n$.
- A key string $K$.
- An alphabet $A$ - a sequence of unique symbols.

The cipher constructs a **square transformation matrix** from the key and uses it to linearly transform blocks of plaintext into numeric ciphertext.

### Encryption

1. Ensure the key length is a perfect square, i.e. $|K| = m^2$.
2. Map each alphabet symbol to an integer starting from 1:
   $A = {a_1, a_2, \ldots, a_{|A|}}, \quad map(a_i) = i$
3. Form a square matrix $M$ of size $m \times m$ by filling it row-wise with values $map(K_i)$.
4. Verify that the matrix determinant $\det(M)$ is nonzero (so that $M$ is invertible).
5. Divide the plaintext into blocks of length $m$. For the last block, if its length is less than $m$, pad it with random symbols from $A$.
6. For each block $P = (p_1, p_2, \ldots, p_m)$, where each $p_i = map(t_i)$, compute: $C = M \cdot P$
7. Round each component of $C$ to the nearest integer and output all resulting values separated by commas.

### Decryption

1. Construct matrix $M$ from the key and compute its inverse $M^{-1}$.
2. Split the numeric ciphertext into blocks of size $m$.
3. For each block $C = (c_1, c_2, \ldots, c_m)$, compute: $P = M^{-1} \cdot C$
4. Round each component of $P$ to the nearest integer and map it back to characters using $A[p_i - 1]$.

The resulting text is written to `output.txt`.

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

- For **encryption**, the program outputs a sequence of integers separated by commas.
- For **decryption**, it outputs the restored plaintext string.

## Constraints

Let: $A$ - the alphabet, $K$ - the key string, $T$ - the text string, $M$ - the matrix constructed from $K$, $m = \sqrt{|K|}$.

Then the following conditions must hold:
1. Alphabet uniqueness: $\forall i \ne j \Rightarrow A_i \ne A_j$
2. Key validity: $K \subseteq A \quad \text{and} \quad |K| \ge 2$
3. Perfect-square key length: $\exists m \in \mathbb{N} : |K| = m^2$
4. Invertibility: $\det(M) \ne 0$
5. Text validity: $T \subseteq A$
6. Padding rule (if needed): $\text{If } |T| \bmod m \ne 0, \text{ then pad with random symbols from } A$
7. Block length constraint: $|T| = q \cdot m + r, \quad 0 \le r < m   $

## Examples

### Example 1 (encryption)

**input.txt**
```
encrypt
GAME
KeyValueAB
ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789
```

**output.txt**
```
1875,3802,5730,7658,3143,6363,9584,12805,4411,8934
```

### Example 2 (decryption)

**input.txt**
```
decrypt
1875,3802,5730,7658,3143,6363,9584,12805,4411,8934
KeyValueAB
ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789
```

**output.txt**
```
GAME
```

## Notes

- The same key and alphabet must produce consistent results between encryption and decryption.
- Any invalid key (non-square length or non-invertible matrix) must raise an exception.
- The implementation must be self-contained and require no network access.

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
