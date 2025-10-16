using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.IO;
using MathNet.Numerics.LinearAlgebra;

namespace Analytic_Transform_Cipher {
    class Program {

        static void Main(string[] args) {
            try {
                string[] input = File.ReadAllLines("input.txt", Encoding.UTF8);

                bool encrypt = true;
                string text = null, key = null;
                string alphabet = AnalyticTransform.ALPHABET;

                if (input.Length == 3) {
                    ParseIntentAndText(input, ref encrypt, ref text, ref key);
                } else if (input.Length == 4) {
                    ParseIntentAndText(input, ref encrypt, ref text, ref key);
                    alphabet = input[3];
                } else {
                    throw new Exception();
                }

                string result = null;
                if (encrypt) {
                    result = string.Join(",", AnalyticTransform.Encrypt(text, key, alphabet).Select(i => i.ToString()));
                } else {
                    result = AnalyticTransform.Decrypt(text.Split(',').Select(p => p.Trim()).Where(p => p != "").Select(p => uint.Parse(p)).ToArray(), key, alphabet);
                }

                File.WriteAllText("output.txt", result, Encoding.UTF8);
            } catch {
                Console.WriteLine("Uncorrect input data!");
            }
        }

        static void ParseIntentAndText(string[] array, ref bool encrypt, ref string text, ref string key) {
            switch (array[0].Trim().ToLower()) {
                case "encrypt":
                    encrypt = true;
                    break;
                case "decrypt":
                    encrypt = false;
                    break;
                default:
                    throw new Exception();
            }
            text = array[1];
            key = array[2];
        }

        static class AnalyticTransform {
            public const string ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";

            public static uint[] Encrypt(string data, string key, string alphabet = ALPHABET) {
                if (alphabet.Distinct().Count() != alphabet.Length ||
                    key.Length < 2 ||
                    key.Except(alphabet).Any() ||
                    data.Distinct().Except(alphabet).Any()) {
                    throw new ArgumentException();
                }
                ushort sqrted = (ushort)Math.Sqrt(key.Length);
                if (sqrted * sqrted != key.Length) {
                    throw new ArgumentException();
                }

                var alphamap = new Dictionary<char, double>(alphabet.Select((v, i) => new KeyValuePair<char, double>(v, i + 1)));
                Matrix<double> transformer = CreateMatrix.Dense(sqrted, sqrted, key.Select(i => alphamap[i]).ToArray());

                if (Math.Abs(transformer.Determinant()) - 1e-15 < 0) {
                    throw new ArgumentException();
                }

                List<uint> result = new();

                ushort i = 0;
                for (ushort maxr = (ushort)(data.Length - (data.Length % sqrted)); i != maxr; i += sqrted) {
                    var tt = data.Skip(i).Take(sqrted).Select(i => alphamap[i]);
                    var encrypted = transformer * CreateVector.DenseOfEnumerable(tt);
                    result.AddRange(encrypted.Select(i => (uint)Math.Round(i)));
                }

                if (i != data.Length) {
                    Random rnd = new((int)DateTime.Now.Ticks);
                    StringBuilder appendix = new(sqrted);
                    appendix.Append(data.Skip(i).ToArray());
                    for (ushort reminder = (ushort)(data.Length - i); reminder != 0; --reminder) {
                        appendix.Append(alphabet[rnd.Next(alphabet.Length)]);
                    }
                    var encrypted = transformer * CreateVector.DenseOfEnumerable(appendix.ToString().Select(i => alphamap[i]));
                    result.AddRange(encrypted.Select(i => (uint)Math.Round(i)));
                }

                return result.ToArray();
            }

            public static string Decrypt(uint[] data, string key, string alphabet = ALPHABET) {
                if (alphabet.Distinct().Count() != alphabet.Length ||
                    key.Length < 2 ||
                    key.Except(alphabet).Any()) {
                    throw new ArgumentException();
                }
                ushort sqrted = (ushort)Math.Sqrt(key.Length);
                if (sqrted * sqrted != key.Length
                    || data.Length % sqrted != 0) {
                    throw new ArgumentException();
                }

                var alphamap = new Dictionary<char, double>(alphabet.Select((v, i) => new KeyValuePair<char, double>(v, i + 1)));
                Matrix<double> transformer = CreateMatrix.Dense(sqrted, sqrted, key.Select(i => alphamap[i]).ToArray()).Inverse();

                StringBuilder result = new();

                ushort i = 0;
                for (ushort maxr = (ushort)(data.Length - (data.Length % sqrted)); i != maxr; i += sqrted) {
                    var decrypted = transformer * CreateVector.DenseOfEnumerable(data.Skip(i).Take(sqrted).Select(i => (double)i));
                    result.Append(decrypted.Select(i => alphabet[(int)Math.Round(i) - 1]).ToArray()); //Throw if can't decrypt
                }

                if (i != data.Length) {
                    Random rnd = new((int)DateTime.Now.Ticks);
                    StringBuilder appendix = new(sqrted);
                    appendix.Append(data.Skip(i).ToArray());
                    for (ushort reminder = (ushort)(data.Length - i); reminder != 0; --reminder) {
                        appendix.Append(alphabet[rnd.Next(alphabet.Length)]);
                    }
                    var decrypted = transformer * CreateVector.DenseOfEnumerable(appendix.ToString().Select(i => (double)i));
                    result.Append(decrypted.Select(i => alphabet[(int)Math.Round(i) - 1]).ToArray()); //Throw if can't decrypt
                }

                return result.ToString();
            }

        }
    }
}
