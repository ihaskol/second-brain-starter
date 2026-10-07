"""Force Times New Roman in a .docx: theme major/minor latin fonts and any asciiTheme refs."""
import re, shutil, sys, zipfile
for path in sys.argv[1:]:
    tmp = path + ".tmp"
    with zipfile.ZipFile(path) as zin, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for n in zin.namelist():
            d = zin.read(n)
            if n.endswith(".xml"):
                t = d.decode("utf8")
                if n.startswith("word/theme/"):
                    t = re.sub(r'(<a:latin typeface=")[^"]*(")', r'\1Times New Roman\2', t)
                    t = re.sub(r'(<a:(?:ea|cs) typeface=")[^"]*(")', r'\1\2', t)
                    t = re.sub(r'(<a:font script="[^"]*" typeface=")[^"]*(")', r'\1Times New Roman\2', t)
                else:
                    t = re.sub(r'w:(?:ascii|hAnsi|cs|eastAsia)Theme="[^"]*"', '', t)
                    t = re.sub(r'(w:(?:ascii|hAnsi)=")(Calibri|Cambria|Aptos|Aptos Display|Arial)(")', r'\1Times New Roman\3', t)
                d = t.encode("utf8")
            zout.writestr(n, d)
    shutil.move(tmp, path)
    z = zipfile.ZipFile(path); fs = set()
    for n in z.namelist():
        if n.endswith(".xml"):
            s = z.read(n).decode("utf8", "ignore")
            fs |= set(re.findall(r'w:(?:ascii|hAnsi)="([^"]+)"', s)) | set(re.findall(r'<a:latin typeface="([^"]*)"', s))
    print(path.split("/")[-1], sorted(fs))
