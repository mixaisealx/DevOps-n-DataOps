using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.IO;

namespace Double_Permutation_Cipher {
    class Program {

        static void Main(string[] args) {
            try {
                string[] input = File.ReadAllLines("input.txt", Encoding.UTF8);

                bool encrypt = true;
                string text = null, key1 = null, key2 = null;
                string alphabet = DoublePermutation.ALPHABET;

                if (input.Length == 4) {
                    ParseIntentAndText(input, ref encrypt, ref text, ref key1, ref key2);
                } else if (input.Length == 5) {
                    ParseIntentAndText(input, ref encrypt, ref text, ref key1, ref key2);
                    alphabet = input[4];
                } else {
                    throw new Exception();
                }

                string result = null;
                if (encrypt) {
                    result = DoublePermutation.Encrypt(text, key1, key2, alphabet);
                } else {
                    result = DoublePermutation.Decrypt(text, key1, key2, alphabet);
                }

                File.WriteAllText("output.txt", result, Encoding.UTF8);
            } catch { 
                Console.WriteLine("Uncorrect input data!"); 
            }
        }

        static void ParseIntentAndText(string[] array, ref bool encrypt, ref string text, ref string key1, ref string key2) {
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
            key1 = array[2];
            key2 = array[3];
        }

        static class DoublePermutation {
            public const string ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";

            private static int[] KeyToEncKeymap(IEnumerable<char> key) {
                return key.Select((c, i) => new KeyValuePair<char, int>(c, i))
                    .OrderBy(p => p.Key)
                    .Select((kv, i) => new KeyValuePair<int, int>(kv.Value, i))
                    .OrderBy(p => p.Key)
                    .Select(p => p.Value)
                    .ToArray();
            }

            private static int[] KeyToDecKeymap(IEnumerable<char> key) {
                return key.Select((c, i) => new KeyValuePair<char, int>(c, i))
                    .OrderBy(p => p.Key)
                    .Select(p => p.Value)
                    .ToArray();
            }

            private static ushort IndexToMappedIndex(ref int[] mask, ushort i) {
                var reminder = i % mask.Length;
                return (ushort)(i - reminder + mask[reminder]);
            }

            public static string Encrypt(string data, string column_key, string row_key, string alphabet = ALPHABET) {
                var keyc_filtered = column_key.Distinct().ToArray();
                var keyr_filtered = row_key.Distinct().ToArray();

                if (alphabet.Distinct().Count() != alphabet.Length ||
                    keyc_filtered.Length < 2 || 
                    keyr_filtered.Length < 2 ||
                    keyc_filtered.Except(alphabet).Any() ||
                    keyr_filtered.Except(alphabet).Any() ||
                    data.Distinct().Except(alphabet).Any()) {
                    throw new ArgumentException();
                }

                ushort rowsc = (ushort)(data.Length / keyc_filtered.Length);
                {
                    short reminder = (short)(data.Length - (rowsc * keyc_filtered.Length));
                    if (reminder > 0) { 
                        ++rowsc;
                        reminder = (short)(keyc_filtered.Length - reminder);
                    } else {
                        reminder = (short)(-reminder);
                    }

                    Random rnd = new((int)DateTime.Now.Ticks);
                    StringBuilder appendix = new(reminder);
                    for (; reminder != 0; --reminder) {
                        appendix.Append(alphabet[rnd.Next(alphabet.Length)]);
                    }
                    data += appendix.ToString();
                }
                
                var mask_column = KeyToEncKeymap(keyc_filtered);
                var mask_row = KeyToEncKeymap(keyr_filtered);

                var rowsc_reminder = rowsc % keyr_filtered.Length;
                var mask_row_small = mask_row.Where(p => p < rowsc_reminder).ToArray();

                List<string> text_mutated = new(rowsc);
                {
                    StringBuilder row_builder = new(keyc_filtered.Length);
                    ushort i = 0;
                    for (ushort maxr = (ushort)(rowsc - rowsc_reminder); i != maxr; ++i) {
                        var row_pos = IndexToMappedIndex(ref mask_row, i) * keyc_filtered.Length; //Start position of needed row
                        for (ushort j = 0; j != keyc_filtered.Length; ++j) {
                            row_builder.Append(data[row_pos + mask_column[j]]);
                        }
                        text_mutated.Add(row_builder.ToString());
                        row_builder.Clear();
                    }
                    for (; i != rowsc; ++i) {
                        var row_pos = IndexToMappedIndex(ref mask_row_small, i) * keyc_filtered.Length; //Start position of needed row
                        for (ushort j = 0; j != keyc_filtered.Length; ++j) {
                            row_builder.Append(data[row_pos + mask_column[j]]);
                        }
                        text_mutated.Add(row_builder.ToString());
                        row_builder.Clear();
                    }
                }

                StringBuilder diagonal_text = new();
                for (int column = 0; column != keyc_filtered.Length; ++column) {
                    int col = column;
                    for (ushort row = 0; row != rowsc && col >= 0; ++row, --col) {
                        diagonal_text.Append(text_mutated[row][col]);
                    }
                }
                for (ushort row = 1; row != rowsc; ++row) {
                    ushort crow = row;
                    for (int col = keyc_filtered.Length - 1; crow != rowsc && col >= 0; ++crow, --col) {
                        diagonal_text.Append(text_mutated[crow][col]);
                    }
                }

                return diagonal_text.ToString();
            }

            public static string Decrypt(string data, string column_key, string row_key, string alphabet = ALPHABET) {
                var keyc_filtered = column_key.Distinct().ToArray();
                var keyr_filtered = row_key.Distinct().ToArray();

                if (alphabet.Distinct().Count() != alphabet.Length ||
                    keyc_filtered.Length < 2 ||
                    keyr_filtered.Length < 2 ||
                    keyc_filtered.Except(alphabet).Any() ||
                    keyr_filtered.Except(alphabet).Any() ||
                    data.Distinct().Except(alphabet).Any()) {
                    throw new ArgumentException();
                }

                ushort rowsc = (ushort)(data.Length / keyc_filtered.Length);
                if (data.Length - (rowsc * keyc_filtered.Length) != 0) {
                    throw new ArgumentOutOfRangeException();
                }

                string[] text_sequental = Enumerable.Range(0, rowsc).Select(p => "").ToArray();
                {
                    StringReader stread = new(data);
                    for (int column = 0; column != keyc_filtered.Length; ++column) {
                        int col = column;
                        for (ushort row = 0; row != rowsc && col >= 0; ++row, --col) {
                            text_sequental[row] += (char)stread.Read();
                        }
                    }
                    for (ushort row = 1; row != rowsc; ++row) {
                        ushort crow = row;
                        for (int col = keyc_filtered.Length - 1; crow != rowsc && col >= 0; ++crow, --col) {
                            text_sequental[crow] += (char)stread.Read();
                        }
                    }
                }

                var mask_column = KeyToDecKeymap(keyc_filtered);
                var mask_row = KeyToDecKeymap(keyr_filtered);

                var rowsc_reminder = rowsc % keyr_filtered.Length;
                var mask_row_small = mask_row.Where(p => p < rowsc_reminder).ToArray();

                StringBuilder text_unmutated = new(rowsc);
                {
                    StringBuilder row_builder = new(keyc_filtered.Length);
                    ushort i = 0;
                    for (ushort maxr = (ushort)(rowsc - rowsc_reminder); i != maxr; ++i) {
                        var row_pos = IndexToMappedIndex(ref mask_row, i); //Start position of needed row
                        for (ushort j = 0; j != keyc_filtered.Length; ++j) {
                            row_builder.Append(text_sequental[row_pos][mask_column[j]]);
                        }
                        text_unmutated.Append(row_builder.ToString());
                        row_builder.Clear();
                    }
                    for (; i != rowsc; ++i) {
                        var row_pos = IndexToMappedIndex(ref mask_row_small, i); //Start position of needed row
                        for (ushort j = 0; j != keyc_filtered.Length; ++j) {
                            row_builder.Append(text_sequental[row_pos][mask_column[j]]);
                        }
                        text_unmutated.Append(row_builder.ToString());
                        row_builder.Clear();
                    }
                }

                return text_unmutated.ToString();
            }

        }
    }
}
