#!/usr/bin/env bash
# Downloads what is missing into a work folder, through the svipall CLI, alternating hosts. Safe to run again.
# usage: bash tools/library/fetch.sh [work]   (default tools/library/work)
U="${1:-$(dirname "$0")/work}"; mkdir -p "$U/pkg" "$U/licenses"
W="$(cygpath -w "$U" 2>/dev/null || echo "$U")"
i=0
for p in lucide tabler ph heroicons iconoir pixelarticons fluent fluent-color hugeicons bi radix-icons healthicons akar-icons majesticons eva mynaui humbleicons zondicons simple-line-icons bx fluent-emoji-flat fluent-emoji fluent-emoji-high-contrast simple-icons logos devicon devicon-plain cib skill-icons flag circle-flags cif flagpack catppuccin octicon; do
  [ -s "$U/pkg/$p.json" ] && continue
  i=$((i+1))
  if [ $((i%2)) = 0 ]; then u="https://unpkg.com/@iconify-json/$p/icons.json"; else u="https://cdn.jsdelivr.net/npm/@iconify-json/$p/icons.json"; fi
  svipall fetch "$u" --out "$W/pkg/$p.json" --wait 300 --timeout 180000 --cache bypass > /dev/null 2>&1
  [ -s "$U/pkg/$p.json" ] && echo "ok   $p" || echo "MISS $p"
done
while read -r name url; do
  [ -s "$U/licenses/$name.txt" ] && continue
  svipall fetch "$url" --out "$W/licenses/$name.txt" --text --wait 300 --cache bypass > /dev/null 2>&1
  [ -s "$U/licenses/$name.txt" ] && echo "ok   licence $name" || echo "MISS licence $name"
done <<'EOF'
lucide https://raw.githubusercontent.com/lucide-icons/lucide/main/LICENSE
tabler https://raw.githubusercontent.com/tabler/tabler-icons/main/LICENSE
ph https://raw.githubusercontent.com/phosphor-icons/core/main/LICENSE
heroicons https://raw.githubusercontent.com/tailwindlabs/heroicons/master/LICENSE
iconoir https://raw.githubusercontent.com/iconoir-icons/iconoir/main/LICENSE
pixelarticons https://raw.githubusercontent.com/halfmage/pixelarticons/master/LICENSE
fluent https://raw.githubusercontent.com/microsoft/fluentui-system-icons/main/LICENSE
octicon https://raw.githubusercontent.com/primer/octicons/main/LICENSE
hugeicons https://unpkg.com/@hugeicons/core-free-icons@4.4.0/LICENSE.md
bi https://raw.githubusercontent.com/twbs/icons/main/LICENSE
radix-icons https://raw.githubusercontent.com/radix-ui/icons/master/LICENSE
healthicons https://raw.githubusercontent.com/resolvetosavelives/healthicons/main/LICENSE
akar-icons https://raw.githubusercontent.com/artcoholic/akar-icons/master/LICENSE
majesticons https://raw.githubusercontent.com/halfmage/majesticons/main/LICENSE
eva https://raw.githubusercontent.com/akveo/eva-icons/master/LICENSE.txt
mynaui https://raw.githubusercontent.com/praveenjuge/mynaui-icons/main/LICENSE
humbleicons https://raw.githubusercontent.com/zraly/humbleicons/master/LICENSE
zondicons https://raw.githubusercontent.com/dukestreetstudio/zondicons/master/LICENSE
simple-line-icons https://raw.githubusercontent.com/thesabbir/simple-line-icons/master/LICENSE.md
bx https://raw.githubusercontent.com/box-icons/boxicons/master/LICENSE
fluent-emoji https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/LICENSE
simple-icons https://raw.githubusercontent.com/simple-icons/simple-icons/develop/LICENSE.md
logos https://raw.githubusercontent.com/gilbarbara/logos/main/LICENSE.txt
devicon https://raw.githubusercontent.com/devicons/devicon/master/LICENSE
coreui https://raw.githubusercontent.com/coreui/coreui-icons/main/LICENSE
skill-icons https://raw.githubusercontent.com/tandpfun/skill-icons/main/LICENSE
flag https://raw.githubusercontent.com/lipis/flag-icons/main/LICENSE
circle-flags https://raw.githubusercontent.com/HatScripts/circle-flags/gh-pages/LICENSE
flagpack https://raw.githubusercontent.com/Yummygum/flagpack-core/main/LICENSE
catppuccin https://raw.githubusercontent.com/catppuccin/vscode-icons/main/LICENSE
EOF
