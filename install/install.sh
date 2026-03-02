#!/usr/bin/env bash

set -euo pipefail

readonly UV_INSTALL_URL="https://astral.sh/uv/install.sh"
readonly MIN_PYTHON="3.11"

info() {
  printf '[INFO] %s\n' "$1"
}

success() {
  printf '[OK] %s\n' "$1"
}

fail() {
  printf '[ERROR] %s\n' "$1" >&2
  exit 1
}

has_cmd() {
  command -v "$1" >/dev/null 2>&1
}

ensure_macos() {
  if [[ "$(uname -s)" != "Darwin" ]]; then
    fail "This script is for macOS only. / This script supports macOS only."
  fi
}

ensure_uv() {
  if has_cmd uv; then
    success "uv is already installed. / uv already available."
    return
  fi

  has_cmd curl || fail "curl is required to install uv. / Please install curl first."
  info "Installing uv... / Installing uv..."
  curl -LsSf "$UV_INSTALL_URL" | sh || fail "Failed to install uv. / uv installation failed."

  export PATH="$HOME/.local/bin:$PATH"
  has_cmd uv || fail "uv not found after install. / uv not found in PATH after install."
  success "uv installed. / uv installed successfully."
}

ensure_python() {
  info "Installing Python ${MIN_PYTHON} via uv... / Installing Python ${MIN_PYTHON} with uv..."
  uv python install "$MIN_PYTHON" || fail "Python installation failed. / Failed to install Python ${MIN_PYTHON}."
  success "Python is ready. / Python installed or already available."
}

install_bao() {
  info "Installing bao-ai from PyPI... / Installing bao-ai from PyPI..."
  uv tool install --upgrade bao-ai || fail "Failed to install bao-ai. / bao-ai install failed."

  info "Verifying installation... / Verifying installation..."
  uvx --from bao-ai bao --version >/dev/null || fail "bao command verification failed. / Failed to verify bao command."
  success "bao-ai installed successfully. / bao-ai installed successfully."
}

print_finish() {
  printf '\n'
  success "All done. Run: bao"
  if ! has_cmd bao; then
    info "If 'bao' is not found, add this to your shell profile:"
    info "export PATH=\"$HOME/.local/bin:\$PATH\""
  fi
}

main() {
  info "Bao one-click installer (macOS) / Bao one-click installer (macOS)"
  ensure_macos
  ensure_uv
  ensure_python
  install_bao
  print_finish
}

main "$@"
