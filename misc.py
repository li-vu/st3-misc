# miscelleous commands

from __future__ import print_function
import sublime
import sublime_plugin
import subprocess
from traceback import print_exc
import sys,os
import tempfile

tmpdir="/tmp"

class LatexIndentCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    encoding = self.view.encoding()
    if encoding == 'Undefined':
      encoding = 'utf-8'
    regions = []
    command = ['latexindent']
    for r in self.view.sel():
      regions.append(r)
    region = sublime.Region(0, self.view.size())
    command.extend([str(self.view.file_name())])
    old_viewport_position = self.view.viewport_position()
    buf = self.view.substr(region)
    p = subprocess.Popen(command, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    output, error = p.communicate(buf.encode(encoding))
    if error:
      print(error)
    self.view.replace(
        edit, region,
        output.decode(encoding))
    self.view.sel().clear()
    for r in regions:
      self.view.sel().add(r)
    # FIXME: Without the 10ms delay, the viewport sometimes jumps.
    sublime.set_timeout(lambda: self.view.set_viewport_position(
      old_viewport_position, False), 10)

class LatexIndentSelectionCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    encoding = self.view.encoding()
    if encoding == 'Undefined':
      encoding = 'utf-8'
    regions = []
    indented = []
    region = sublime.Region(0, self.view.size())
    command = ['latexindent']
    for r in self.view.sel():
      regions.append(r)
      text = self.view.substr(r)
      (fd, fn) = tempfile.mkstemp()
      f = None
      try:
        f = os.fdopen(fd,'w')
        f.write(text)
        f.close()
        cmd = command + [fn]
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        output, error = p.communicate(text.encode(encoding))
        if error:
          print(error)
          # if it doesn't work, put the old text back
          indented = indented + [text]
        indented = indented + [output.decode(encoding)]
      except:
        print_exc(file=sys.stdout)
      finally:
        if f:
            f.close()
        os.remove(fn)
    for i, r in enumerate(regions):
      self.view.replace(
          edit, r,
          indented[i])
    old_viewport_position = self.view.viewport_position()
    self.view.sel().clear()
    for r in regions:
      self.view.sel().add(r)
    # FIXME: Without the 10ms delay, the viewport sometimes jumps.
    sublime.set_timeout(lambda: self.view.set_viewport_position(
      old_viewport_position, False), 10)
