# Grok Roblox Multi-Instance

Simple, open-source Windows tool that lets you run **multiple Roblox clients** on one PC by holding Roblox's singleton mutex.

## How it works

Roblox creates a named mutex (`ROBLOX_singletonMutex`) when it starts. If the mutex already exists, a new client just focuses the existing window and exits.

This tool creates and holds that mutex **before** you launch Roblox, so every new client thinks it's the first one and opens normally.

## Requirements

- Windows 10 or 11
- Python 3.8+ (or use the .exe if I package one later)
- Official Roblox desktop client

## Quick Start

1. **Close every Roblox window** (check Task Manager too).
2. Run the launcher:
   ```bash
   python launcher.py
   ```
3. Click **Start Multi-Instance**.
4. Keep the launcher window open.
5. Launch Roblox as many times as you want (from the website, shortcut, etc.).
6. When finished, click **Stop & Release** or just close the window.

## Important Warnings

- **This is not an official Roblox feature.** Roblox does not support multiple clients on one machine.
- Holding multiple accounts is allowed. Using them for **ban evasion, botting, exploiting, farming, or any ToS violation** can get your accounts banned.
- This tool does **not** store cookies, passwords, or modify Roblox files.
- Antivirus may flag it (common with custom launchers). You can add an exclusion if needed.
- Use at your own risk. No warranties.

## Building a standalone .exe (optional)

If you don't want to install Python:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name GrokRobloxMulti launcher.py
```

The `.exe` will appear in the `dist` folder.

## License

MIT License — do whatever you want with it, just don't blame me if Roblox gets mad.

Made with Grok.
