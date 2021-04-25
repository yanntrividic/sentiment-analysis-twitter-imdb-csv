# -*- mode: python ; coding: utf-8 -*-

#Command to type in: pyinstaller l3aa1.spec --noconfirm

block_cipher = None

# \!/ \!/ \!/ \!/ ONLY ONE LINE HAS TO BE UNCOMMENTED DEPENDING ON THE LOCAL MACHINE'S DIR
src = '/home/yann/eclipse-workspace/SentimentAnalysis/src/'
#src = r'D:\\University\\L3 Informatique\\Projet tutoré\\SVN\\trunk\\src\\' # windows
# /!\ /!\ /!\ /!\

def get_all_files_from_folder(src_folder):
  '''Reconstructs the architecture of the src folder, but in the executable version
  '''
  l = []
  for root, dirs, files in os.walk(src_folder):
    for file in files:
      l.append((os.path.join(root,file), root[len(src):]))
  return l

bin = get_all_files_from_folder(src+'model/resources/pickle/') # all the pickle files are listed here
#training = get_all_files_from_folder(src+'resources/trainig_data/') # all the training data in case we have to train the model
imgs = get_all_files_from_folder(src+'view/img/') # all the images of the project

datas = imgs

a = Analysis([src + 'l3aa1.py'],
             pathex=[src, # every package has to be listed here
                     src + 'controller', 
                     src + 'model', 
                     src + 'model/analysis',
                     src + 'model/local_io', 
                     src + 'model/data_extraction',
                     src + 'view',
                     src + 'setup'],
             binaries=bin, # the pickle files
             datas=datas, #training+ # images and training data
             hiddenimports=['sklearn.utils.sparsetools._graph_validation', # those are the various modules that are hidden at import
                            'sklearn.utils.sparsetools._graph_tools',
                            'sklearn.utils.lgamma',
                            'sklearn.utils.weight_vector',
                            'sklearn.utils._weight_vector'],
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
          [],
          exclude_binaries=True,
          name='l3aa1',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='l3aa1')

app = BUNDLE(coll,
         name='l3aa1.app',
         icon=src + 'view/img/L3AA1.png',
         bundle_identifier=None)