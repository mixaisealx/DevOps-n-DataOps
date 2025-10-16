using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.IO;

namespace Vigenere_Cipher {
    class Program {

        static void Main(string[] args) {
            try {
                string[] input = File.ReadAllLines("input.txt", Encoding.UTF8);

                bool encrypt = true;
                string text = null, key = null;
                string alphabet = Vigenere.ALPHABET;

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
                    result = Vigenere.Encrypt(text, key, alphabet);
                } else {
                    result = Vigenere.Decrypt(text, key, alphabet);
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

        static class Vigenere {
            public const string ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";

            public static string Encrypt(string data, string key, string alphabet = ALPHABET) {
                var key_filtered = key.Distinct().ToArray();

                if (alphabet.Distinct().Count() != alphabet.Length ||
                    key_filtered.Except(alphabet).Any() ||
                    data.Distinct().Except(alphabet).Any()) {
                    throw new ArgumentException();
                }

                List<string> alphas = new(key_filtered.Length);
                foreach (var letter in key) {
                    var vi = alphabet.IndexOf(letter);
                    alphas.Add(string.Join("", alphabet.Skip(vi).Concat(alphabet.Take(vi))));
                }

                StringBuilder sb = new();
                int alpha_slice = 0;
                foreach (var letter in data) {
                    sb.Append(alphas[alpha_slice++][alphabet.IndexOf(letter)]);
                    alpha_slice %= alphas.Count;
                }

                return sb.ToString();
            }

            public static string Decrypt(string data, string key, string alphabet = ALPHABET) {
                var key_filtered = key.Distinct().ToArray();

                if (alphabet.Distinct().Count() != alphabet.Length ||
                    key_filtered.Except(alphabet).Any() ||
                    data.Distinct().Except(alphabet).Any()) {
                    throw new ArgumentException();
                }

                List<string> alphas = new(key_filtered.Length);
                foreach (var letter in key) {
                    var vi = alphabet.IndexOf(letter);
                    alphas.Add(string.Join("", alphabet.Skip(vi).Concat(alphabet.Take(vi))));
                }

                StringBuilder sb = new();
                int alpha_slice = 0;
                foreach (var letter in data) {
                    sb.Append(alphabet[alphas[alpha_slice++].IndexOf(letter)]);
                    alpha_slice %= alphas.Count;
                }

                return sb.ToString();
            }

        }
    }
}
