# How to Uninstall Fly.io CLI

## Quick Uninstall

Since you installed Fly.io CLI but chose not to add it to PATH (you pressed 'n'), uninstalling is simple:

### Step 1: Remove the Fly.io directory

```bash
rm -rf /home/centrox/.fly
```

This removes the entire Fly.io installation.

### Step 2: Verify it's gone

```bash
ls -la ~/.fly
```

You should see: `ls: cannot access '/home/centrox/.fly': No such file or directory`

That's it! ✅

---

## If You Had Added It to PATH

If you had pressed 'Y' and added it to PATH, you'd also need to:

### Remove from .bashrc:

```bash
nano ~/.bashrc
```

Look for and delete these lines:
```bash
export FLYCTL_INSTALL="/home/centrox/.fly"
export PATH="$FLYCTL_INSTALL/bin:$PATH"
```

Save and exit (Ctrl+X, then Y, then Enter)

### Reload your shell:

```bash
source ~/.bashrc
```

---

## Complete Cleanup (Optional)

If you want to remove ALL traces:

### 1. Remove CLI installation:
```bash
rm -rf ~/.fly
```

### 2. Remove Fly.io config (if you logged in):
```bash
rm -rf ~/.fly.toml
```

### 3. Check for any Fly.io entries in .bashrc:
```bash
grep -i "fly" ~/.bashrc
```

If you see any Fly.io related lines, remove them:
```bash
nano ~/.bashrc
```

---

## Your Current Situation

Based on your output, you:
- ✅ Installed Fly.io CLI to `/home/centrox/.fly`
- ✅ Chose NOT to add it to PATH (pressed 'n')
- ✅ CLI is installed but not accessible from anywhere

### To uninstall right now:

Just run:
```bash
rm -rf /home/centrox/.fly
```

Done! The CLI is completely removed.

---

## Why You Might Not Need CLI

Since you're using the **Web Portal** method:
- ✅ Deploy via GitHub (no CLI needed)
- ✅ View logs in browser (no CLI needed)
- ✅ Update settings in browser (no CLI needed)
- ✅ Restart app in browser (no CLI needed)

**You can do everything through the web interface!**

---

## When You WOULD Need CLI

You'd only need the CLI if you want to:
- Deploy without GitHub
- Run commands from terminal
- Automate deployments with scripts
- SSH into your app from terminal

For your use case (weekly scheduled scraping via n8n), **the web portal is perfect!**

---

## Recommendation

Since you're going with the web portal method:

1. **Uninstall the CLI:**
   ```bash
   rm -rf /home/centrox/.fly
   ```

2. **Use the web portal for everything:**
   - Deploy: https://fly.io/dashboard
   - Logs: Click "Logs" in dashboard
   - Settings: Click "Settings" in dashboard

3. **If you ever need CLI later:**
   - Just run the install command again
   - It takes 30 seconds to reinstall

---

## Summary

**To uninstall Fly.io CLI:**
```bash
rm -rf /home/centrox/.fly
```

That's it! Since you didn't add it to PATH, there's nothing else to clean up.

**Stick with the web portal** - it's easier and does everything you need! 🚀
