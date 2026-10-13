#!/usr/bin/env bash
# Publishes the app into ../pkhex, which GitHub Pages serves as-is.
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
out="$(mktemp -d)"
dotnet publish "$here/src/PKHeXMobile/PKHeXMobile.csproj" -c Release -o "$out"
# Pages compresses responses itself, so the precompressed copies only add weight.
find "$out/wwwroot" \( -name '*.br' -o -name '*.gz' \) -delete
rm -rf "$here/../pkhex"
cp -r "$out/wwwroot" "$here/../pkhex"
rm -rf "$out"
echo "Built into $(cd "$here/.." && pwd)/pkhex"
