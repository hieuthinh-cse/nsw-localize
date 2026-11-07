using System;
using System.IO;
using System.Linq;
using System.Text;
using System.Collections.Generic;
using UndertaleModLib;
using UndertaleModLib.Models;

EnsureDataLoaded();

string donorPath = @"C:\Users\MintO\code\localize\welldweller\original-1.0.2\game.win";
string reportPath = @"C:\Users\MintO\code\localize\welldweller\compare-utmt\diff-report.txt";

UndertaleData donor;
using (var stream = new FileStream(donorPath, FileMode.Open, FileAccess.Read))
{
    donor = UndertaleIO.Read(stream, (w, _) => {});
}

StringBuilder sb = new StringBuilder();
sb.AppendLine("=== SO SÁNH GIỮA BẢN ATMOSPHERE VÀ BẢN GỐC (ORIGINAL 1.0.2) ===");
sb.AppendLine($"Atmosphere Data File: {FilePath}");
sb.AppendLine($"Original Data File:   {donorPath}");
sb.AppendLine();

// 1. Strings
sb.AppendLine($"--- 1. STRINGS ---");
sb.AppendLine($"Original Strings:   {donor.Strings.Count}");
sb.AppendLine($"Atmosphere Strings: {Data.Strings.Count}");

int stringDiffCount = 0;
int minStrings = Math.Min(donor.Strings.Count, Data.Strings.Count);
for (int i = 0; i < minStrings; i++)
{
    if (donor.Strings[i].Content != Data.Strings[i].Content)
    {
        stringDiffCount++;
        if (stringDiffCount <= 30)
        {
            sb.AppendLine($"  [Diff #{i}]");
            sb.AppendLine($"    Orig: {donor.Strings[i].Content}");
            sb.AppendLine($"    Mod:  {Data.Strings[i].Content}");
        }
    }
}
if (stringDiffCount > 30)
    sb.AppendLine($"  ... tổng cộng {stringDiffCount} chuỗi khác nhau.");
else if (stringDiffCount == 0)
    sb.AppendLine("  -> Không có chuỗi nào bị thay đổi nội dung ở cùng index.");

// Check new strings
if (Data.Strings.Count > donor.Strings.Count)
{
    sb.AppendLine($"  -> Thêm {Data.Strings.Count - donor.Strings.Count} chuỗi mới:");
    for (int i = donor.Strings.Count; i < Data.Strings.Count; i++)
    {
        sb.AppendLine($"    [New #{i}] {Data.Strings[i].Content}");
    }
}

// 2. Embedded Textures
sb.AppendLine();
sb.AppendLine($"--- 2. EMBEDDED TEXTURES ---");
sb.AppendLine($"Original Textures:   {donor.EmbeddedTextures.Count}");
sb.AppendLine($"Atmosphere Textures: {Data.EmbeddedTextures.Count}");
if (Data.EmbeddedTextures.Count > donor.EmbeddedTextures.Count)
{
    sb.AppendLine($"  -> Có {Data.EmbeddedTextures.Count - donor.EmbeddedTextures.Count} embedded texture mới được thêm vào (Index từ {donor.EmbeddedTextures.Count} đến {Data.EmbeddedTextures.Count - 1}).");
}

// 3. Texture Page Items
sb.AppendLine();
sb.AppendLine($"--- 3. TEXTURE PAGE ITEMS ---");
sb.AppendLine($"Original TPItems:   {donor.TexturePageItems.Count}");
sb.AppendLine($"Atmosphere TPItems: {Data.TexturePageItems.Count}");
if (Data.TexturePageItems.Count > donor.TexturePageItems.Count)
{
    sb.AppendLine($"  -> Thêm {Data.TexturePageItems.Count - donor.TexturePageItems.Count} texture page items mới:");
    for (int i = donor.TexturePageItems.Count; i < Data.TexturePageItems.Count; i++)
    {
        var item = Data.TexturePageItems[i];
        sb.AppendLine($"    [TPItem #{i}] TargetX: {item.TargetX}, TargetY: {item.TargetY}, Width: {item.TargetWidth}, Height: {item.TargetHeight}, Tex: {item.TexturePage?.Name?.Content}");
    }
}

// 4. Fonts
sb.AppendLine();
sb.AppendLine($"--- 4. FONTS ---");
sb.AppendLine($"Original Fonts:   {donor.Fonts.Count}");
sb.AppendLine($"Atmosphere Fonts: {Data.Fonts.Count}");

var origFontNames = donor.Fonts.Select(f => f.Name?.Content).ToHashSet();
var modFontNames = Data.Fonts.Select(f => f.Name?.Content).ToHashSet();

foreach (var f in Data.Fonts)
{
    if (f == null) continue;
    string name = f.Name?.Content ?? "<unnamed>";
    var origF = donor.Fonts.FirstOrDefault(x => x?.Name?.Content == name);
    if (origF == null)
    {
        sb.AppendLine($"  [Font MỚI]: {name} (DisplayName: {f.DisplayName?.Content}, EmSize: {f.EmSize})");
    }
    else
    {
        bool changed = false;
        string changes = "";
        if (f.Glyphs.Count != origF.Glyphs.Count)
        {
            changed = true;
            changes += $" Glyphs: {origF.Glyphs.Count} -> {f.Glyphs.Count};";
        }
        if (f.Texture?.Name?.Content != origF.Texture?.Name?.Content)
        {
            changed = true;
            changes += $" Texture: {origF.Texture?.Name?.Content} -> {f.Texture?.Name?.Content};";
        }
        if (f.EmSize != origF.EmSize)
        {
            changed = true;
            changes += $" EmSize: {origF.EmSize} -> {f.EmSize};";
        }
        if (changed)
        {
            sb.AppendLine($"  [Font THAY ĐỔI]: {name} -{changes}");
            // Print new glyph sample
            var origChars = origF.Glyphs.Select(g => (char)g.Character).ToHashSet();
            var newChars = f.Glyphs.Select(g => (char)g.Character).Where(c => !origChars.Contains(c)).ToList();
            if (newChars.Count > 0)
            {
                sb.AppendLine($"    -> Thêm {newChars.Count} ký tự mới: {new string(newChars.Take(50).ToArray())}...");
            }
        }
    }
}

// 5. Sprites
sb.AppendLine();
sb.AppendLine($"--- 5. SPRITES ---");
sb.AppendLine($"Original Sprites:   {donor.Sprites.Count}");
sb.AppendLine($"Atmosphere Sprites: {Data.Sprites.Count}");

foreach (var s in Data.Sprites)
{
    if (s == null) continue;
    string name = s.Name?.Content ?? "<unnamed>";
    var origS = donor.Sprites.FirstOrDefault(x => x?.Name?.Content == name);
    if (origS == null)
    {
        sb.AppendLine($"  [Sprite MỚI]: {name}");
    }
    else
    {
        // check texture page items
        if (s.Textures.Count != origS.Textures.Count)
        {
            sb.AppendLine($"  [Sprite Khác texture count]: {name} ({origS.Textures.Count} -> {s.Textures.Count})");
        }
        else
        {
            for (int t = 0; t < s.Textures.Count; t++)
            {
                var curTex = s.Textures[t]?.Texture;
                var origTex = origS.Textures[t]?.Texture;
                if (curTex?.Name?.Content != origTex?.Name?.Content ||
                    curTex?.SourceX != origTex?.SourceX ||
                    curTex?.SourceY != origTex?.SourceY ||
                    curTex?.SourceWidth != origTex?.SourceWidth ||
                    curTex?.SourceHeight != origTex?.SourceHeight)
                {
                    sb.AppendLine($"  [Sprite Texture Đổi]: {name} frame {t}");
                    break;
                }
            }
        }
    }
}

// 6. Audio / Sounds
sb.AppendLine();
sb.AppendLine($"--- 6. SOUNDS ---");
sb.AppendLine($"Original Sounds:   {donor.Sounds.Count}");
sb.AppendLine($"Atmosphere Sounds: {Data.Sounds.Count}");

// 7. Translations.ini check
sb.AppendLine();
sb.AppendLine("=== SO SÁNH TRANSLATIONS.INI ===");
string iniOrig = @"C:\Users\MintO\code\localize\welldweller\Well Dweller [0100217023F6C000][v0][Base]\romfs\translations.ini";
string iniAtmo = @"C:\Users\MintO\code\localize\welldweller\atmosphere\contents\0100217023F6C000\romfs\translations.ini";
if (File.Exists(iniOrig) && File.Exists(iniAtmo))
{
    var linesOrig = File.ReadAllLines(iniOrig);
    var linesAtmo = File.ReadAllLines(iniAtmo);
    sb.AppendLine($"Original translations.ini: {linesOrig.Length} dòng ({new FileInfo(iniOrig).Length} bytes)");
    sb.AppendLine($"Atmosphere translations.ini: {linesAtmo.Length} dòng ({new FileInfo(iniAtmo).Length} bytes)");
}

File.WriteAllText(reportPath, sb.ToString(), Encoding.UTF8);
ScriptMessage("Comparison completed! Report saved to " + reportPath);
