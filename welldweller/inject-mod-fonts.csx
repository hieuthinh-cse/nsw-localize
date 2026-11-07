using System;
using System.IO;
using System.Linq;
using UndertaleModLib;
using UndertaleModLib.Models;
using UndertaleModLib.Util;
EnsureDataLoaded();
string donorPath = @"C:\Users\MintO\code\localize\welldweller\atmosphere\contents\0100217023F6C000\romfs\game.win";
string reportPath = @"C:\Users\MintO\code\localize\welldweller\font-inject-report.txt";
UndertaleData donor;
using (var stream = File.OpenRead(donorPath)) donor = UndertaleIO.Read(stream, (w, _) => {});
string[] names = { "fnt_default", "fnt_default2", "fnt_default3", "fnt_title" };
UndertaleString GetOrAddString(string value) {
    var found = Data.Strings.FirstOrDefault(s => s.Content == value);
    if (found != null) return found;
    var created = new UndertaleString(value); Data.Strings.Add(created); return created;
}
var report = new System.Text.StringBuilder();
report.AppendLine($"Target before: fonts={Data.Fonts.Count}, textures={Data.EmbeddedTextures.Count}, pages={Data.TexturePageItems.Count}");
foreach (string name in names) {
    var srcFont = donor.Fonts.First(f => f?.Name?.Content == name);
    var dstFont = Data.Fonts.First(f => f?.Name?.Content == name);
    var srcPage = srcFont.Texture;
    if (srcPage == null || srcPage.TexturePage == null) throw new Exception($"Source font texture missing: {name}");
    var srcTexture = srcPage.TexturePage;
    var newTexture = new UndertaleEmbeddedTexture {
        Name = GetOrAddString($"FontMod {srcTexture.Name.Content}"),
        Scaled = srcTexture.Scaled,
        GeneratedMips = srcTexture.GeneratedMips,
        TextureData = srcTexture.TextureData,
        TextureExternal = srcTexture.TextureExternal,
        TextureLoaded = srcTexture.TextureLoaded,
        TextureWidth = srcPage.TargetWidth,
        TextureHeight = srcPage.TargetHeight,
        IndexInGroup = srcTexture.IndexInGroup,
        TextureInfo = srcTexture.TextureInfo
    };
    Data.EmbeddedTextures.Add(newTexture);
    var newPage = new UndertaleTexturePageItem {
        Name = GetOrAddString($"FontMod Page {Data.TexturePageItems.Count}"),
        SourceX = srcPage.SourceX, SourceY = srcPage.SourceY,
        SourceWidth = srcPage.SourceWidth, SourceHeight = srcPage.SourceHeight,
        TargetX = srcPage.TargetX, TargetY = srcPage.TargetY,
        TargetWidth = srcPage.TargetWidth, TargetHeight = srcPage.TargetHeight,
        BoundingWidth = srcPage.BoundingWidth, BoundingHeight = srcPage.BoundingHeight,
        TexturePage = newTexture
    };
    Data.TexturePageItems.Add(newPage);
    dstFont.DisplayName = GetOrAddString(srcFont.DisplayName?.Content ?? name);
    dstFont.EmSizeIsFloat = srcFont.EmSizeIsFloat; dstFont.EmSize = srcFont.EmSize;
    dstFont.Bold = srcFont.Bold; dstFont.Italic = srcFont.Italic;
    dstFont.RangeStart = srcFont.RangeStart; dstFont.RangeEnd = srcFont.RangeEnd;
    dstFont.Charset = srcFont.Charset; dstFont.AntiAliasing = srcFont.AntiAliasing;
    dstFont.ScaleX = srcFont.ScaleX; dstFont.ScaleY = srcFont.ScaleY;
    dstFont.Ascender = srcFont.Ascender; dstFont.SDFSpread = srcFont.SDFSpread;
    dstFont.LineHeight = srcFont.LineHeight; dstFont.AscenderOffset = srcFont.AscenderOffset;
    dstFont.Glyphs = new UndertalePointerList<UndertaleFont.Glyph>(srcFont.Glyphs.Select(g => {
        var glyph = new UndertaleFont.Glyph {
            Character = g.Character, SourceX = g.SourceX, SourceY = g.SourceY,
            SourceWidth = g.SourceWidth, SourceHeight = g.SourceHeight,
            Shift = g.Shift, Offset = g.Offset,
            Kerning = g.Kerning,
            UnknownAlwaysZero = g.UnknownAlwaysZero
        };
        return glyph;
    }));
    dstFont.Texture = newPage;
    report.AppendLine($"{name}: glyphs={dstFont.Glyphs.Count}, texture={newTexture.Name.Content} {newTexture.TextureWidth}x{newTexture.TextureHeight}, page={newPage.Name.Content}");
}
report.AppendLine($"Target after: fonts={Data.Fonts.Count}, textures={Data.EmbeddedTextures.Count}, pages={Data.TexturePageItems.Count}");
File.WriteAllText(reportPath, report.ToString());

