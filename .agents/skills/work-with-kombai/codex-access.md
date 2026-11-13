# Getting access in Codex's sandbox

Read this only when running in Codex's sandbox (the Codex CLI, the IDE extension, or the Codex or ChatGPT
desktop app); `SKILL.md` beside this file sends you here.

When running in Codex's sandbox, get access outside it **before the first Kombai command**; do not try the
restricted command first. The commands need network access and write `~/.kombai` and npm's configured cache;
`npx` may contact the package registry before Kombai starts.

Before requesting access, resolve npm's cache with the local config read `npm config get cache`
(`npm.cmd config get cache` on Windows), from the workspace root when in an npm workspace. Request the
returned directory, including any configured override; do not assume it is `~/.npm`.

- If this chat can approve sandbox escalations, use `sandbox_permissions: "require_escalated"` on the
  execution tool call for the first command and every later Kombai CLI command.
- If it can't but has the `request_permissions` tool (as a ChatGPT or Codex app chat with no project picked
  does), get the access through that, asking for network access and write access to those paths, then run the
  commands without escalation. Its grant can end with the reply, so before the first Kombai command or
  design-file write of each reply, run `node -p "'network_off='+(process.env.CODEX_SANDBOX_NETWORK_DISABLED||0)"` on its own: if
  it prints `network_off=1`, call `request_permissions` first; if `network_off=0`, the earlier grant still
  holds, so don't ask again. No output alone does not mean the network was off: if execution returns a
  running session, poll it instead of rerunning the command. If a Kombai command exits with no output, check the
  same way: only if it prints `network_off=1` did it never start, so ask and run it again. Retry only a
  confirmed sandbox denial before any write was sent; for an unknown write outcome, inspect state first. If a later reply in the chat has
  to call `request_permissions` again (asking twice in one reply doesn't count), once that reply's Kombai work
  is done, call Kombai's `access_card` tool with reason `granted` where it is there (in Codex, find it in
  `ALL_TOOLS`), once per chat: it shows the user how to stop this prompt on every message (the request is
  done, so it has no Continue button).
- Before any later command needs another write path, request the missing access first. Every
  `mcp install codex`, including an existing view's upgrade or setup from the standalone skill, needs the
  directory containing `config.toml` under `$CODEX_HOME` (else `~/.codex`), following a config symlink to
  its target's directory. The CLI creates a temporary sibling there before replacing the config.
- If neither is available, or the user declines, run nothing and do not retry inside the sandbox. Where
  Kombai's `access_card` tool is there, call it with reason `blocked` (it shows how to allow Kombai, with a
  Continue button that sends "Continue" here) and end your turn with one line. Otherwise tell the user only
  this, in one or two lines: Kombai needs network access to start, and they can allow it by choosing **Approve
  for me** in the permissions menu under the message box (in Codex in a terminal, by allowing network access
  in its approval settings), then sending their message again.
