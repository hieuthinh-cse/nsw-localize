using System;
using System.IO;
using UndertaleModLib;
using UndertaleModLib.Util;
using UndertaleModLib.Models;

EnsureDataLoaded();

string outDir = @"C:\Users\MintO\code\localize\welldweller\compare-utmt\viet-hoa\fonts";
Directory.CreateDirectory(outDir);

using (var worker = new TextureWorker())
{
    foreach (var font in Data.Fonts)
    {
        if (font?.Texture != null)
        {
            string pngPath = Path.Combine(outDir, $"{font.Name.Content}.png");
            worker.ExportAsPNG(font.Texture, pngPath);
        }
    }
}

ScriptMessage("Exported fonts to " + outDir);
