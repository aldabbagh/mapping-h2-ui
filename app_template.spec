# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['MainWindow.py'],
             pathex=['shapefile_to_network/main/convertor', 
		     'shapefile_to_network/main/shortest_paths'],
             binaries=[],
             datas=[
             	('Results', 'Results'),
		('Data', 'Data'),
		('shapefile_to_network', 'shapefile_to_network')
             ],
             hiddenimports=None,
             hookspath=None,
             runtime_hooks=None,
             excludes=None,
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='hydrogen cost calculation tool',
          debug=True,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False,
          icon='solar-energy-icon.ico' )

coll = COLLECT(a.binaries, 
	       a.zipfiles,
	       a.datas,
	       name = 'h2-shareable')
