# Installing Starmap for Claude Code

## Steps

### 1. Clone the repository

```bash
git clone https://github.com/rebelice/starmap.git ~/.claude/skills/starmap-repo
```

### 2. Symlink the skill

```bash
ln -sf ~/.claude/skills/starmap-repo/skills/starmap ~/.claude/skills/starmap
```

### 3. Verify

Confirm the skill is installed:

```bash
ls ~/.claude/skills/starmap/SKILL.md
```

You should see the file listed. Restart Claude Code and try `/starmap init`.

## Updating

```bash
cd ~/.claude/skills/starmap-repo && git pull
```

The symlink ensures you always get the latest version.

## Uninstalling

```bash
rm ~/.claude/skills/starmap
rm -rf ~/.claude/skills/starmap-repo
```
