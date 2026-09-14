$files = Get-ChildItem -Path . -Recurse -File -Filter *.md | Sort-Object FullName
$result = foreach($f in $files){
  $rel = Resolve-Path -Relative $f.FullName
  $content = Get-Content -Path $f.FullName -Encoding UTF8
  $heading = ($content | Where-Object { $_ -match '^# ' } | Select-Object -First 1)
  if(-not $heading){ $heading = ($content | Where-Object { $_.Trim().Length -gt 0 } | Select-Object -First 1) }
  $todo = ($content | Select-String -Pattern '^- \[ \]' -SimpleMatch:$false).Count
  $done = ($content | Select-String -Pattern '^- \[x\]|^- \[X\]' -SimpleMatch:$false).Count
  [PSCustomObject]@{
    Path = $rel
    Heading = $heading
    Todo = $todo
    Done = $done
  }
}
$result | ConvertTo-Json -Depth 3
