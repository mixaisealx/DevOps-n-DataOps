using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.IO;
using Force.Crc32;

namespace Gamming_Cipher {
    class Program {

        static void Main(string[] args) {
            try {
                string[] input = File.ReadAllLines("input.txt", Encoding.UTF8);

                bool encrypt = true;
                string text = null, key = null;
                string alphabet = Gamming.ALPHABET;

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
                    result = Gamming.Encrypt(text, key, alphabet);
                } else {
                    result = Gamming.Decrypt(text, key, alphabet);
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

        static class Gamming {
            public const string ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";

            public static string Encrypt(string data, string key, string alphabet = ALPHABET) {
                if (alphabet.Distinct().Count() != alphabet.Length ||
                    key.Length < 2 ||
                    key.Except(alphabet).Any() ||
                    data.Distinct().Except(alphabet).Any()) {
                    throw new ArgumentException();
                }

                Random rnd = new Random((int)Crc32CAlgorithm.Compute(Encoding.UTF8.GetBytes(key)));

                var alphamap = new Dictionary<char, ushort>(alphabet.Select((v, i) => new KeyValuePair<char, ushort>(v, (ushort)i)));

                StringBuilder result = new();
                for (ushort i = 0; i != data.Length; ++i) {
                    result.Append(alphabet[(alphamap[data[i]] + rnd.Next(alphabet.Length)) % alphabet.Length]);
                }

                return result.ToString();
            }

            public static string Decrypt(string data, string key, string alphabet = ALPHABET) {
                if (alphabet.Distinct().Count() != alphabet.Length ||
                    key.Length < 2 ||
                    key.Except(alphabet).Any() ||
                    data.Distinct().Except(alphabet).Any()) {
                    throw new ArgumentException();
                }

                Random rnd = new Random((int)Crc32CAlgorithm.Compute(Encoding.UTF8.GetBytes(key)));

                var alphamap = new Dictionary<char, ushort>(alphabet.Select((v, i) => new KeyValuePair<char, ushort>(v, (ushort)i)));

                StringBuilder result = new();
                for (ushort i = 0; i != data.Length; ++i) {
                    result.Append(alphabet[(alphabet.Length + alphamap[data[i]] - rnd.Next(alphabet.Length)) % alphabet.Length]);
                }

                return result.ToString();
            }

        }
    }
}
