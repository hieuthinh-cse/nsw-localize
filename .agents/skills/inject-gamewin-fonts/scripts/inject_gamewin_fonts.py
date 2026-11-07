#!/usr/bin/env python3
"""Copy selected font glyphs and texture pages between compatible GameMaker game.win files."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path


CSX_TEMPLATE = r'''using System;
using System.IO;
using System.Linq;
using UndertaleModLib;
using UndertaleModLib.Models;
EnsureDataLoaded();
string donorPath = __DONOR__;
string reportPath = __REPORT__;
string[] fontNames = __FONTS__;
UndertaleData donor;
using (var stream = File.OpenRead(donorPath)) donor = UndertaleIO.Read(stream, (w, _) => {});
UndertaleString GetOrAddString(string value) {
    var found = Data.Strings.FirstOrDefault(s => s.Content == value);
    if (found != null) return found;
    var created = new UndertaleString(value); Data.Strings.Add(created); return created;
}
var report = new System.Text.StringBuilder();
report.AppendLine($"Before: fonts={Data.Fonts.Count}, textures={Data.EmbeddedTextures.Count}, pages={Data.TexturePageItems.Count}");
foreach (string name in fontNames) {
    var srcFont = donor.Fonts.FirstOrDefault(f => f?.Name?.Content == name);
    var dstFont = Data.Fonts.FirstOrDefault(f => f?.Name?.Content == name);
    if (srcFont == null || dstFont == null) throw new Exception($"Font not present in both files: {name}");
    var srcPage = srcFont.Texture;
    if (srcPage == null || srcPage.TexturePage == null) throw new Exception($"Donor font texture missing: {name}");
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
    dstFont.Glyphs = new UndertalePointerList<UndertaleFont.Glyph>(srcFont.Glyphs.Select(g => new UndertaleFont.Glyph {
        Character = g.Character, SourceX = g.SourceX, SourceY = g.SourceY,
        SourceWidth = g.SourceWidth, SourceHeight = g.SourceHeight,
        Shift = g.Shift, Offset = g.Offset, Kerning = g.Kerning,
        UnknownAlwaysZero = g.UnknownAlwaysZero
    }));
    dstFont.Texture = newPage;
    report.AppendLine($"{name}\t{dstFont.Glyphs.Count}\t{newTexture.TextureWidth}x{newTexture.TextureHeight}\t{newPage.Name.Content}");
}
report.AppendLine($"After: fonts={Data.Fonts.Count}, textures={Data.EmbeddedTextures.Count}, pages={Data.TexturePageItems.Count}");
File.WriteAllText(reportPath, report.ToString());
'''

DEFAULT_FONTS = ("fnt_default", "fnt_default2", "fnt_default3", "fnt_title")


def require_file(value: str, label: str) -> Path:
    path = Path(value).expanduser().resolve(strict=True)
    if not path.is_file():
        raise ValueError(f"{label} is not a file: {path}")
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", required=True, help="Base/newer game.win to update")
    parser.add_argument("--donor", required=True, help="Modded game.win containing the fonts")
    parser.add_argument("--utmt-cli", required=True, help="Path to UndertaleModCli.exe")
    parser.add_argument("--output", required=True, help="New output game.win path; must not exist")
    parser.add_argument("--fonts", nargs="+", default=list(DEFAULT_FONTS), help="Font resource names to transfer")
    args = parser.parse_args()

    try:
        target = require_file(args.target, "Target")
        donor = require_file(args.donor, "Donor")
        cli = require_file(args.utmt_cli, "UndertaleModTool CLI")
        output = Path(args.output).expanduser().resolve()
        if target == donor:
            raise ValueError("Target and donor must be different files")
        if output.exists():
            raise ValueError(f"Output already exists: {output}")
        output.parent.mkdir(parents=True, exist_ok=True)

        with tempfile.TemporaryDirectory(prefix="inject_gamewin_fonts_", dir=output.parent) as temp:
            tempdir = Path(temp)
            csx = tempdir / "inject-fonts.csx"
            report = tempdir / "font-report.txt"
            code = (CSX_TEMPLATE
                    .replace("__DONOR__", json.dumps(str(donor)))
                    .replace("__REPORT__", json.dumps(str(report)))
                    .replace("__FONTS__", "new string[] { " + ", ".join(json.dumps(n) for n in args.fonts) + " }"))
            csx.write_text(code, encoding="utf-8")
            result = subprocess.run(
                [str(cli), "load", str(target), "-s", str(csx), "-o", str(output)],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, errors="replace", check=False,
            )
            if result.stdout:
                print(result.stdout, end="" if result.stdout.endswith("\n") else "\n")
            if result.returncode != 0:
                raise RuntimeError(f"UndertaleModTool failed with exit code {result.returncode}")
            if not output.is_file() or not report.is_file():
                raise RuntimeError("UndertaleModTool did not produce the output and font report")

            info = subprocess.run([str(cli), "info", str(output)], stdout=subprocess.PIPE,
                                  stderr=subprocess.STDOUT, text=True, errors="replace", check=False)
            if info.returncode != 0:
                print(info.stdout, file=sys.stderr)
                raise RuntimeError("UndertaleModTool could not reopen the generated game.win")
            print(info.stdout, end="" if info.stdout.endswith("\n") else "\n")

            print("Transferred fonts:")
            for line in report.read_text(encoding="utf-8").splitlines():
                if "\t" in line:
                    name, glyphs, dimensions, page = line.split("\t", 3)
                    print(f"  {name}: {glyphs} glyphs, atlas {dimensions}, {page}")

        digest = hashlib.sha256()
        with output.open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(block)
        print(f"Output: {output}\nBytes: {output.stat().st_size}\nSHA256: {digest.hexdigest()}")
        return 0
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
