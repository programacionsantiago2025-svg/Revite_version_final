# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_data_files, collect_submodules


block_cipher = None

datas = [
    ("assets", "assets"),
    ("src/data/destinos.json", "src/data"),
    ("src/data/carros.json", "src/data"),
    ("src/data/reservas.json", "src/data"),
    ("revite_carros.db", "."),
    ("revite_cliente.db", "."),
    ("revite_reserva.db", "."),
]
datas += collect_data_files("flet")

hiddenimports = collect_submodules("flet") + [
    "src",
    "src.models",
    "src.models.carro",
    "src.models.clientes",
    "src.models.reservas",
    "src.components",
    "src.components.navbar",
    "src.data",
    "src.data.base_de_datos_carros",
    "src.data.base_de_datos_cliente",
    "src.data.base_de_datos_reservas",
    "src.views",
    "src.views.page2",
]

a = Analysis(
    ["src/views/page.py"],
    pathex=["."],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="ReviteCarros",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
