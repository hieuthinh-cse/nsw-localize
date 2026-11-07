using System.IO;
using System.Linq;
using Newtonsoft.Json;

EnsureDataLoaded();

var strings = Data.Strings
    .Select((value, index) => new { Index = index, Content = value.Content })
    .ToArray();

File.WriteAllText(
    @"C:\Users\MintO\code\localize\welldweller\compare-utmt\original-strings.json",
    JsonConvert.SerializeObject(strings, Formatting.Indented));
