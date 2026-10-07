on run argv
  set docName to item 1 of argv
  set outPath to item 2 of argv
  tell application "Keynote"
    set found to false
    repeat 60 times
      if (exists document docName) then
        set found to true
        exit repeat
      end if
      delay 1
    end repeat
    if not found then error "not opened: " & docName
    set d to document docName
    export d to (POSIX file outPath) as PDF with properties {PDF image quality:Good, skipped slides:false}
    close d saving no
  end tell
end run
