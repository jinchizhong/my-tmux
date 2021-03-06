My tmux configure file
======================

A fine-tuned tmux configure file.

### Features

1. Column based pane layout

2. Tabbed pane

3. Fine-tuned mouse support (with mouse message translate support)

4. System clipboard support

5. Key-bindings in copy-mode exactly same to vim

6. Two different prefixes for different commands

7. New pane inherit current path

### Usage

For now, only tmux 2.9 is tested. Tmux 3.0 should also works.

    $ cd <some-where>
    $ git clone https://github.com/jinchizhong/my-tmux
    $ ln -s <some-where>/my-tmux/tmux.conf ~/.tmux.conf

### Session shortcuts

| Key           | Function             |
| ------------- | -------------------- |
| C-b d         | Detach clinet        |
| C-b D         | Detach one client    |
| C-b s         | Choose session       |

### Window shortcuts

| Key | Function |
| - | - |
| C-b c | New window |
| C-b 1-9 | Select window 1-9 |
| C-b , | Rename window |
| C-b . | Move window |
| C-b n | Select next window |
| C-b p | Select prev window |

### Pane shortcuts

| Key | Function |
| - | - |
| F1~F4 | Switch to column 1~4 |
| C-b {/} | Move column to left/right side |
| C-b <left/right/up/down> | Focus left/right/up/down pane |
| C-b - | Create new pane below current pane |
| C-b \| | Create new column after current column |
| C-b % | Split current pane vertically |
| C-b z | Zoom current pane |
| C-b k | Kill current pane |
| C-b m | Mark current pane |
| C-b space | [when has pane marked] Swap current pane and marked pane |
|           | [when no pane marked] Even columns |
| C-a <up/down/left/right> | Resize current pane |
| C-a C-<up/down/left/right> | Resize current pane slowly |
| C-a + | Enlarge current pane |
| C-a - | Reduce current pane |
| - | - |
| C-b t | Create a tab |
| C-b tab | Switch to next tab |

### Copy mode (View history mode)

| Key | Function |
| - | - |
| C-b v | Turn on copy-mode |
| C-b PageUp | Turn on copy-mode |
| C-b / | Turn on copy-mode, and begin search |
| C-b ? | Turn on copy-mode, and begin reverse search |

Following shortcuts only works, when copy-mode is turned on. They are very close to vim default shortcuts.
Most of keys support repeat, for example:

10w => move cursor by 10 words
5PageUp => Scroll 5 pages up

| Key | Function |
| - | - |
| <up/down/left/right> | Move cursor |
| <h/j/k/l> | Move cursor (vim style) |
| w | Move cursor by word |
| W | Move cursor by word (space-separated) |
| e | Move cursor by word-end |
| E | Move cursor by word-end (space-separated) |
| b | Backward move cursor by word |
| B | Backward move cursor by word (space-separated) |
| - | - |
| 0 | Move to start of the line |
| ^ | Move to first character of line |
| $ | Move to end of the line |
| Home | Move to start of the line |
| End | Move to end of the line |
| PageUp | Page up |
| PageDown | Page down |
| gg | Move to the first line |
| G | Move to the last line |
| <num>G | Move to line <num> |
| - | - |
| / | Begin search |
| ? | Begin reverse search |
| n | Search next |
| N | Search previous |
| - | - |
| v | Begin selection |
| V | Begin selection with line selection mode |
| C-v | Begin selection with block selection mode |
| y | Copy to clipboard |
| Y | Copy to selection(linux primary clipboard) |
| Esc | Clear selection |
| q | Quit copy-mode |
| C-c | Quit copy-mode |

### Clipboard

| Key | Function |
| - | - |
| C-b p | Paste clipboard to pane |
| C-b P | Paste selection to pane |

### Mouse support

| Action | Function |
| - | - |
| Left click pane | Active pane |
| Right click pane | Mark pane, when there's marked pane: |
|                  | left click another pane to swap them |
|                  | middle click another pane to paste marked pane |
| Drag in pane | Select content, then you can right click to copy them |
| Middle click in pane | Linux style paste action |
| Wheel up/down in pane | If program run in pane support mouse wheel, translate mouse event and send to it, otherwise start copy-mode |
| Click on window label | Switch to window |
