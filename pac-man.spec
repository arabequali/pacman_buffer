# PyInstaller spec: `make package` builds dist/pacman/ (one folder).
# The assets are bundled; config.json and README.txt are copied next to
# the executable by the Makefile so players can edit the configuration.
a = Analysis(
    ["pac-man.py"],
    pathex=["."],
    datas=[("assets", "assets")],
    hiddenimports=["mazegenerator", "src.app"],
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="pacman",
    console=False,
)
coll = COLLECT(exe, a.binaries, a.datas, name="pacman")
