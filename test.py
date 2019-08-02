import volta
import os

def iterate_folder(folder, f):
  for p in os.listdir(folder):
    file_path = os.path.join(folder, p)
    if os.path.isdir(file_path):
      continue
    f(file_path)

def clear_folder(folder):
  iterate_folder(folder, lambda p: os.remove(p))

def remove_num(folder):
  def rename(path):
    base = os.path.basename(path)
    new_path = base[0:base.find('#')] + '.md'
    os.rename(path, new_path)
  iterate_folder(folder, rename)