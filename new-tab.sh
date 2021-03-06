#!/bin/bash

exec 2>&1
THIS_DIR=$(dirname `readlink -f "$0"`)

if tmux display -p "#{pane_start_command}" | grep -q tab-container; then
  tmux send C-b c
else
  tmux new-session -d -s tmp-tabs -c '#{pane_current_path}'
  tmux set -s -t tmp-tabs "status-position" top
  tmux set -s -t tmp-tabs "status-left" ""
  tmux set -s -t tmp-tabs "status-right" ""
  tmux set -s -t tmp-tabs "status-style" "bg=colour240"
  tmux set-hook -t tmp-tabs window-unlinked "run-shell ${THIS_DIR}/on-tab-close.sh"

  tmux swap-pane -d -t tmp-tabs:1
  pid=`tmux display -p "#{pane_id}"`
  tmux new-window -t tmp-tabs -c '#{pane_current_path}'
  tmux rename-session -t tmp-tabs "${pid#%}-tabs"
  tmux respawn-pane -k "$THIS_DIR/tab-container.sh" "$pid"
fi
