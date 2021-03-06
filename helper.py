#!/usr/bin/python3

import re
import sys
import subprocess
from collections import namedtuple
from dataclasses import dataclass

@dataclass
class Size:
  w: int
  h: int

@dataclass
class Box:
  type: str
  w: int
  h: int
  x: int
  y: int
  children: list
  pane_id: str

  def panes(self):
    if self.type == 'pane':
      yield self

    for box in self.children:
      yield from box.panes()

  def find_pane(self, pane_id):
    if self.pane_id == pane_id:
      return self

    for box in self.children:
      r = box.find_pane(pane_id)
      if r:
        return r

    return None

  def min_size(self):
    if self.type == 'pane':
      return Size(1, 1)

    s = Size(0, 0)
    for box in self.children:
      ms = box.min_size()
      if self.type == 'vbox':
        s.w = max(s.w, ms.w)
        s.h += ms.h + 1
      else:
        s.w = ms.w + 1
        s.h = max(ms.h)

    return s

  def set_geo(self, x, y, w, h):
    self.x = x
    self.y = y
    self.w = w
    self.h = h

    if self.type == 'hbox':
      self.adjust([x.w for x in self.children])
    elif self.type == 'vbox':
      self.adjust([x.h for x in self.children])

  def adjust(self, quotes):
    assert len(quotes) == len(self.children)
    if self.type == 'pane':
      return

    todo = list(range(len(self.children)))
    target = [-1] * len(quotes)

    if self.type == 'hbox':
      min_sizes = [x.min_size().w for x in self.children]
    else:
      min_sizes = [x.min_size().h for x in self.children]

    remains = self.w if self.type == 'hbox' else self.h
    remains -= len(self.children) - 1

    total_quote = sum(quotes)

    while True:
      todo2 = []
      for i in todo:
        size = int(quotes[i] / total_quote * remains + 0.01)
        if size <= min_sizes[i]:
          target[i] = min_sizes[i]
          total_quote -= quotes[i]
          remains -= size
        else:
          todo2.append(i)

      if len(todo2) == len(todo):
        break
      else:
        todo = todo2

    for i in todo:
      size = int(quotes[i] / total_quote * remains + 0.01)
      target[i] = size
      total_quote -= quotes[i]
      remains -= size

    stack_dim_cur = self.x if self.type == 'hbox' else self.y
    for i in range(len(quotes)):
      if self.type == 'hbox':
        self.children[i].set_geo(stack_dim_cur, self.y, target[i], self.h)
      else:
        self.children[i].set_geo(self.x, stack_dim_cur, self.w, target[i])

      stack_dim_cur += target[i] + 1

  def to_string(self, with_checksum=True):
    s = str(self.w) + 'x' + str(self.h) + ',' + str(self.x) + ',' + str(self.y)
    if self.type == 'pane':
      s += ',' + self.pane_id[1:]

    else:
      s += '{' if self.type == 'hbox' else '['
      s += ','.join(box.to_string(False) for box in self.children)
      s += '}' if self.type == 'hbox' else ']'

    if with_checksum:
      s = Box.checksum(s) + ',' + s

    return s

  def checksum(x):
    csum = 0
    for ch in x:
      csum = (((csum >> 1) | (csum << 15)) + ord(ch)) & 0xffff
    return "%04x" % csum


class LayoutParser:

  def parse(self, cont):
    csum, layout = cont.split(',', 1)
    if Box.checksum(layout) != csum:
      raise Exception('checksum error')

    self._str = layout
    self._cur = 0

    return self.parse_boxes()[0]

  def parse_box(self):
    w = self.take_int()
    assert self.take_char() == 'x'
    h = self.take_int()
    assert self.take_char() == ','
    x = self.take_int()
    assert self.take_char() == ','
    y = self.take_int()

    ch = self.take_char()
    if ch == ',':
      pane_id = self.take_int()
      return Box('pane', w, h, x, y, [], '%' + str(pane_id))
    elif ch == '{':
      children = self.parse_boxes()
      assert self.take_char() == '}'
      return Box('hbox', w, h, x, y, children, None)
    elif ch == '[':
      children = self.parse_boxes()
      assert self.take_char() == ']'
      return Box('vbox', w, h, x, y, children, None)
    else:
      assert False

  def parse_boxes(self):
    boxes = []
    while True:
      boxes.append(self.parse_box())
      if self.peek_char() == ',':
        self.take_char()
      else:
        break
    return boxes

  def take_char(self):
    if self._cur < len(self._str):
      ch = self._str[self._cur]
      self._cur += 1
      return ch

    return ''

  def peek_char(self):
    return self._str[self._cur] if self._cur < len(self._str) else ''

  def take_int(self):
    x = 0
    while self.peek_char() >= '0' and self.peek_char() <= '9':
      x = x * 10 + int(self.take_char())
    return x


class Tmux:

  Window = namedtuple('Window', ['id', 'active', 'layout'])

  def run_command(self, *args):
    r = subprocess.run(['tmux'] + list(args),
                       capture_output=True, encoding='utf-8')
    return r.stdout

  def query(self, *fields):
    sep = '--5763599105--'
    query = sep.join('#{'+x+'}' for x in fields)
    line = self.run_command('display', '-p', '-F', query).strip()
    t = namedtuple('info', [re.sub('^@', '', x) for x in fields])
    return t(*line.split(sep))

  def setw(self, key, value):
    self.run_command('setw', key, str(value))

  def select_pane(self, pane_id):
    self.run_command('select-pane', '-t', pane_id)

  def list_pane(self, *fields):
    sep = '--5763599105--'
    query = sep.join('#{'+x+'}' for x in fields)
    lines = self.run_command('list-pane', '-F', query).strip()
    t = namedtuple('info', [re.sub('^@', '', x) for x in fields])
    return [t(*line.split(sep)) for line in lines.split('\n')]

  def apply_layout(self, layout, active_pane):
    if type(layout) == str:
      layout = LayoutParser().parse(layout)

    panes_in_window = [x[0] for x in self.list_pane('pane_id')]
    panes_in_layout = [p.pane_id for p in layout.panes()]
    if sorted(panes_in_window) != sorted(panes_in_layout):
      raise Exception('apply_layout failed, panes list not match')

    layout_s = layout.to_string()
    self.run_command('select-layout', layout_s)

    for i in range(len(panes_in_layout)):
      if panes_in_window[i] == panes_in_layout[i]:
        continue

      ii = panes_in_window.index(panes_in_layout[i])
      self.swap_pane(panes_in_window[i], panes_in_window[ii], active_pane)
      panes_in_window[ii] = panes_in_window[i]
      panes_in_window[i] = panes_in_layout[i]

  def swap_pane(self, pane1, pane2, active_pane):
    if active_pane != pane1 and active_pane != pane2:
      self.run_command('swap-pane', '-d', '-s', pane1, '-t', pane2)
      return

    if active_pane == pane1:
      pane1, pane2 = pane2, pane1

    self.run_command('swap-pane', '-s', pane1, '-t', pane2)


def select_column(idx_1base):
  idx = idx_1base - 1
  tmux = Tmux()
  info = tmux.query('window_layout', 'pane_id')
  layout = LayoutParser().parse(info[0])
  current_pane = info.pane_id

  if layout.type != 'hbox':
    tmux.display('Not in column-based layout')
    return False

  columns = layout.children
  if idx < 0 or idx >= len(columns):
    tmux.display('Column ' + idx_1base + ' does not exists')
    return False

  for i in range(len(columns)):
    if columns[i].find_pane(current_pane):
      current_column = i
      break

  if idx == current_column:
    return False

  info = tmux.query('@column_' + str(idx) + '_last_pane')

  if columns[idx].find_pane(info[0]):
    raise_pane = info[0]

  else:
    box = columns[idx]
    while box.type != 'pane':
      box = box.children[0]

    raise_pane = box.pane_id

  tmux.setw('@column_' + str(current_column) + '_last_pane', current_pane)
  tmux.select_pane(raise_pane)


def even_columns():
  tmux = Tmux()
  info = tmux.query('window_layout', 'pane_id')
  layout = LayoutParser().parse(info[0])

  if layout.type != 'hbox':
    return

  layout.adjust([1] * len(layout.children))
  tmux.apply_layout(layout, info.pane_id)


def swap_columns(column1_1base, column2_1base):
  c1 = column1_1base - 1
  c2 = column2_1base - 1
  if c1 == c2:
    return

  tmux = Tmux()
  info = tmux.query('window_layout', 'pane_id')
  layout = LayoutParser().parse(info[0])

  if layout.type != 'hbox':
    return

  columns = layout.children

  if c1 < 0 or c1 >= len(columns):
    return
  if c2 < 0 or c2 >= len(columns):
    return

  columns[c1], columns[c2] = columns[c2], columns[c1]
  layout.adjust([x.w for x in columns])

  tmux.apply_layout(layout, info.pane_id)


def move_column(column_idx_1base, dir):
  assert dir == 'left' or dir == 'right'

  tmux = Tmux()
  info = tmux.query('window_layout', 'pane_id')
  layout = LayoutParser().parse(info[0])

  if layout.type != 'hbox':
    return

  columns = layout.children

  if column_idx_1base == 'cur':
    for i in range(len(columns)):
      if columns[i].find_pane(info.pane_id):
        col = i
  else:
    col = int(column_idx_1base) - 1

  if col < 0 or col >= len(columns):
    return

  next_col = (col + 1 if dir == 'right' else col - 1) % len(columns)

  columns[col], columns[next_col] = columns[next_col], columns[col]
  layout.adjust([x.w for x in columns])

  tmux.apply_layout(layout, info.pane_id)


def test():
  tmux = Tmux()
  tmux.run_command('display', 'test')


def main(cmd, args):
  if cmd == 'test':
    test()

  elif cmd == 'select-column':
    assert len(args) == 1
    select_column(int(args[0]))

  elif cmd == 'even-column':
    even_columns()

  elif cmd == 'swap-column':
    assert len(args) == 2
    swap_columns(int(args[0]), int(args[1]))

  elif cmd == 'move-column':
    assert len(args) == 2
    move_column(*args)

  else:
    raise Exception('unknown subcommand: ' + cmd)


if __name__ == '__main__':
  assert len(sys.argv) >= 2
  main(sys.argv[1], sys.argv[2:])

