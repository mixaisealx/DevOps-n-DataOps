# Crypto Algorithms

This folder contains implementations of four classic cryptographic algorithms in C#. Each algorithm is provided as a separate folder with a fully working console application.

## Folders and Algorithms

- [Vigenere Algorithm](./Vigenere-Algorithm) – Implements the Vigenere (generalized Vigenère) cipher with arbitrary alphabets.
- [Double Permutation](./Double-Permutation) – Implements a double permutation cipher using column and row keys with diagonal traversal.
- [Gamming](./Gamming-Cipher) – Implements a stream (gamma) cipher using a pseudorandom sequence derived from a key and CRC-32 seeding.
- [Analytic Transform](./Analytic-Transform) – Implements an analytic (matrix-based) cipher using square key matrices for linear transformations of text blocks.

Each folder includes:
- Full task description.
- Complete C# source code.
- Instructions for compilation and execution on Windows and Linux.

## Technologies

- C# language and .NET (dotnet SDK 6.0+)
- System libraries: `LINQ`, collections, dictionaries
- MathNet.Numerics (matrix and vector operations, determinants, inverses)
- Force.Crc32 (CRC-32/CRC-32C)
- Concepts & algorithms: modular arithmetic and wrap-around indexing, permutation masks and inverse permutations, block vs stream processing, matrix linear transforms and invertibility checks, diagonal traversal and non-standard reading orders, padding strategies for block alignment, pseudorandom generation & seeding, mapping/encoding with custom alphabets, input validation and error handling, deterministic test vectors and reproducibility
