# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['blink/main.py'],
             pathex=['blink', '/home/thealphadollar/.local/share/virtualenvs/Blink-_KHfAu0d/', '/media/sf_Blink'],
             binaries=[],
             datas=[('blink/.client_secrets', '.'), ('blink/trackerList.json', '.')],
             hiddenimports=['google-api-python-client'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
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
          name='main',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True )
