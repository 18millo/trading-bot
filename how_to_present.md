# How to Use the Presentation Slides

## 📊 Opening the Presentation

### Method 1: LibreOffice Impress (Recommended)
```bash
cd /home/millo/Documents/python-projects/trading-bot

# Open the presentation
libreoffice --impress presentation.odp &

# Or just double-click the file in file manager
```

### Method 2: Convert to PDF First
```bash
# If you want PDF format:
libreoffice --headless --convert-to pdf presentation.odp

# Then open PDF
xdg-open presentation.pdf
```

### Method 3: Use the Markdown Slides
```bash
# If LibreOffice isn't available, use the markdown version:
cat presentation_slides.md

# Or convert with pandoc (if installed):
pandoc presentation_slides.md -o presentation.pdf
```

---

## 🎤 Running the Live Demo

### Step 1: Create User (Auto-login)
```bash
cd /home/millo/Documents/python-projects/trading-bot

# Create user (no auth needed)
./trading-bot create-user --username presenter --password demo123
```

### Step 2: Test Commands (Before Presentation)
```bash
# Check status
./trading-bot status

# Show strategy config
./trading-bot strategy --show-config

# Run backtest with Gold (impressive!)
./trading-bot backtest --symbol XAUUSD --timeframe-1h H1 --timeframe-entry M1 --days 30

# Run backtest with US30
./trading-bot backtest --symbol US30 --timeframe-1h H1 --timeframe-entry M1 --days 30
```

### Step 3: During Presentation
```bash
# 1. Show title slide (Slide 1)
#    (in LibreOffice)

# 2. Create user (Slide 6 demo)
./trading-bot create-user --username demo --password demo123

# 3. Show strategy config (Slide 7)
./trading-bot strategy --show-config

# 4. Run backtest with Gold (Slide 8)
./trading-bot backtest --symbol XAUUSD --timeframe-1h H1 --timeframe-entry M1 --days 30

# 5. Open PDF report (Slide 9)
xdg-open backtest_report_*.pdf

# 6. Forward test with US30 (Slide 10)
./trading-bot forwardtest --symbol US30 --timeframe-1h H1 --timeframe-entry M1 --duration 1
# Press Ctrl+C after 30 seconds

# 7. Show all commands (Slide 12)
./trading-bot --help
```

---

## 📋 Presentation Flow with Slides

| Slide | Content | Action |
|-------|---------|--------|
| 1 | Title Slide | Show in LibreOffice |
| 2 | Problem Statement | Explain current bot issues |
| 3 | Solution Overview | Highlight ENB + S/R |
| 4 | ENB Strategy | Explain the 4 conditions |
| 5 | System Architecture | Show CLI structure |
| 6 | **Demo: User Creation** | `./trading-bot create-user` |
| 7 | **Demo: Strategy Config** | `./trading-bot strategy --show-config` |
| 8 | **Demo: Backtest Gold** | `./trading-bot backtest --symbol XAUUSD` |
| 9 | **Demo: PDF Report** | Open `backtest_report_*.pdf` |
| 10 | **Demo: Forward Test** | `./trading-bot forwardtest --symbol US30` |
| 11 | Risk Management | Explain features |
| 12 | All Commands | Show `--help` |
| 13 | Why Different | Compare to other bots |
| 14 | Supported Markets | Gold, US30, etc. |
| 15 | Q&A | Answer questions |
| 16 | Final Pitch | Thank you! |
| 17 | Quick Reference | Keep for Q&A |

---

## 🎯 Quick Presentation Script

### Opening (2 mins):
1. Open **Slide 1** in LibreOffice
2. Say: "Today I'm presenting an MT5 Trading Bot with ENB Strategy + Support/Resistance detection"
3. Move to **Slide 2-3**: Explain the problem and solution

### Strategy Explanation (3 mins):
4. Show **Slide 4**: Explain ENB + S/R
5. Show **Slide 5**: System architecture
6. Run: `./trading-bot strategy --show-config`

### Live Demo (10 mins):
7. **Slide 6**: Create user
   ```bash
   ./trading-bot create-user --username presenter --password demo123
   ```

8. **Slide 7**: Show strategy
   ```bash
   ./trading-bot strategy --show-config
   ```

9. **Slide 8**: Run backtest with Gold
   ```bash
   ./trading-bot backtest --symbol XAUUSD --timeframe-1h H1 --timeframe-entry M1 --days 30
   ```

10. **Slide 9**: Open PDF report
    ```bash
    xdg-open backtest_report_*.pdf
    ```

11. **Slide 10**: Forward test with US30
    ```bash
    ./trading-bot forwardtest --symbol US30 --duration 1
    # Ctrl+C after 30 seconds
    ```

### Closing (5 mins):
12. **Slide 11-14**: Explain features
13. **Slide 15**: Q&A
14. **Slide 16**: Final pitch
15. **Slide 17**: Quick reference for Q&A

---

## 📊 Download Links (If Needed)

### LibreOffice:
```bash
# Ubuntu/Debian
sudo apt install libreoffice

# Fedora
sudo dnf install libreoffice

# Or download: https://www.libreoffice.org/download/
```

### Alternative: Use Google Slides
1. Open `presentation_slides.md`
2. Copy content to Google Slides
3. Format as needed

---

## 🔧 Troubleshooting

### Can't open .odp file?
```bash
# Check if LibreOffice is installed
which libreoffice

# If not, install it or use markdown version:
cat presentation_slides.md
```

### Presentation won't advance?
- Use arrow keys or click to advance slides
- Press `F5` to start presentation mode in LibreOffice

### Commands not working during demo?
```bash
# Make sure you're in the right directory
cd /home/millo/Documents/python-projects/trading-bot

# Check if virtual environment is active
which python3  # Should show venv/bin/python3

# If not, activate it:
source venv/bin/activate
```

---

## ✅ Final Checklist

Before presentation:
- [ ] Test LibreOffice can open `presentation.odp`
- [ ] Run `./trading-bot create-user` successfully
- [ ] Test backtest command (run before presentation)
- [ ] Have `backtest_report_*.pdf` ready to show
- [ ] Print `presentation_slides.md` as backup
- [ ] Have `how_to_present.md` open on second screen

---

**Your presentation is ready!** 🚀  
Open: `libreoffice --impress presentation.odp`  
Run demo: `./trading-bot create-user --username presenter --password demo123`
