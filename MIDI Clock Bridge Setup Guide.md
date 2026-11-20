# MIDI Clock Bridge Setup Guide

Nov 18, 2026 · @acvd

This script, for Mac or Windows, takes the tempo from the CDJ-3000 via the DJM-A9 mixer and sends it as MIDI clock to the Deluge and Torso T-1, so the synths play in sync with the DJ set. Setup takes about 15 minutes the first time; after that, starting it is one command.

## What you need

| Item | Notes |
| --- | --- |
| Mac | Any recent macOS (no driver needed) or Windows laptop (needs the Pioneer DJM-A9 driver; see Windows setup). |
| DJM-A9 + CDJ-3000 | Linked as usual. The A9 reads the BPM from the CDJ. |
| Synthstrom Deluge and/or Torso T-1 | The devices that follow the tempo. |
| USB cable: DJM-A9 to Mac | USB-B on the mixer end. USB-C on the Mac end, or use an adapter. |
| USB cable per synth to Mac | One for the Deluge, one for the T-1. A USB hub is fine if the Mac is short on ports. |
| Internet connection | Only for the one-time install. |

No USB MIDI host boxes are needed. The ones tried so far (Doremidi UMH-21, Kenton) don't work reliably with the DJM-A9.

## Connections

The tempo flows CDJ → mixer → Mac → synths, with every link over USB except CDJ to mixer.

1. CDJ-3000 to DJM-A9: linked as usual for DJing.
2. DJM-A9 **USB A** port to the Mac. Use port A: port B does not send the clock.
3. Deluge USB to the Mac.
4. Torso T-1 USB to the Mac.

Remove any 5-pin DIN MIDI cables going into the Deluge or T-1. Each synth should get clock from one source only, or it reads a wrong tempo.

## Device settings

| Device | Setting | Why |
| --- | --- | --- |
| DJM-A9 | Press **MIDI ON** so it lights up | The mixer only sends clock with MIDI on |
| DJM-A9 | Beat FX channel selector on the playing channel or Master | The clock follows the BPM shown on the mixer's display |
| Deluge | Settings → MIDI → Clock → In: **On** | Lets it follow external tempo |
| Deluge | MIDI Thru: Off | Avoids MIDI loops |
| Deluge | SYNC-SCALING button off; tempo magnitude matching off | Otherwise the tempo can be scaled to odd values |
| Torso T-1 | Receive external MIDI clock over USB | Menu depends on firmware; see the T-1 manual |

Check that the BPM on the A9's display matches the CDJ before going further.

## One-time install

This installs a small Python MIDI library in its own folder (`~/midibridge`). It doesn't change anything else on the Mac.

1. Open **Terminal** (Applications → Utilities → Terminal).
2. Paste this line and press Enter:

```bash
python3 -m venv ~/midibridge && ~/midibridge/bin/pip install mido python-rtmidi
```

3. If macOS asks to install "command line developer tools", click **Install**, wait until it finishes, then paste the line again.
4. It's done when you see "Successfully installed" followed by mido and python-rtmidi.

## Create the script

Paste this whole block into Terminal and press Enter. It saves `bridge.py` in your home folder. You only do this once.

```bash
cat > ~/bridge.py << 'EOF'
import sys, mido

# Usage:  bridge.py <dest> [<dest> ...]   e.g.  bridge.py T-1   or   bridge.py Deluge T-1
KEEP = {"clock", "start", "stop", "continue", "songpos"}

ins, outs = mido.get_input_names(), mido.get_output_names()
print("Inputs: ", ins)
print("Outputs:", outs)

wanted = sys.argv[1:] or ["Deluge"]
src = next((n for n in ins if "djm" in n.lower()), None)
if not src:
    raise SystemExit("\nDJM-A9 not found - is it connected via USB A with MIDI ON?")

dests = []
for w in wanted:
    match = next((n for n in outs if w.lower() in n.lower()), None)
    if match:
        dests.append(match)
    else:
        print(f"\n!! No output matching '{w}' - check the Outputs list above.")
if not dests:
    raise SystemExit("\nNo destinations found.")

ports = [mido.open_output(d) for d in dests]
print(f"\nForwarding clock: {src} -> {', '.join(dests)}")
print("Press Ctrl+C to stop.\n")

try:
    with mido.open_input(src) as i:
        for msg in i:
            if msg.type in KEEP:
                for p in ports:
                    p.send(msg)
                if msg.type != "clock":
                    print("Sent:", msg.type)
except KeyboardInterrupt:
    pass
finally:
    for p in ports:
        p.close()
EOF
```

The script only forwards timing messages (clock, start, stop, continue, song position). The A9's fader and knob MIDI is filtered out so it never reaches the synths.

## Running it each session

With everything connected and MIDI ON lit on the A9, open Terminal and run the command for the synths you're using:

| What you want | Command |
| --- | --- |
| Both synths | `~/midibridge/bin/python ~/bridge.py Deluge T-1` |
| Deluge only | `~/midibridge/bin/python ~/bridge.py Deluge` |
| T-1 only | `~/midibridge/bin/python ~/bridge.py T-1` |

Terminal lists the MIDI ports, then shows a line starting "Forwarding clock". Leave that window open the whole time you play.

To check it works:

1. Play a track on the CDJ.
2. Press play on each synth. The Deluge's sync light comes on and its tempo matches the CDJ.
3. Move the CDJ's tempo fader. The synths should follow within a beat or two.

To stop, click the Terminal window and press **Ctrl+C**. A slight tempo wobble on the synth display is normal for clock from a computer.

## Windows setup

On a Windows laptop, the script itself is unchanged; only the install and launch steps differ. Connections and device settings are the same as above.

1. **Install the DJM-A9 driver.** Download it from the DJM-A9 support page on [pioneerdj.com](https://www.pioneerdj.com/en/support/software/mixer/djm-a9/). Unlike on a Mac, Windows needs it before the mixer shows up as a MIDI device.
2. **Install Python** from [python.org](https://www.python.org/downloads/). During setup, tick **Add python.exe to PATH**.
3. **Install the MIDI library.** Open **Command Prompt** and run:

```bat
py -m venv %USERPROFILE%\midibridge
%USERPROFILE%\midibridge\Scripts\pip install mido python-rtmidi
```

4. **Create the script.** Open Notepad and paste only the Python code from Create the script: everything between the `cat > ~/bridge.py << 'EOF'` line and the final `EOF`, not those two lines. Choose Save As, set Save as type to **All files**, and save it as `bridge.py` in your user folder (`C:\Users\<name>`), or Notepad will add `.txt`.
5. **Run it** from Command Prompt:

```bat
%USERPROFILE%\midibridge\Scripts\python %USERPROFILE%\bridge.py Deluge T-1
```

Use `Deluge` or `T-1` alone to clock just one synth. Press **Ctrl+C** to stop.

Two Windows-specific points:

- **One app per MIDI port.** Windows normally lets only one program open a MIDI port. Close rekordbox, MIDI-OX or any DAW using the DJM-A9 or the synths before starting the bridge, or the script can't open them.
- **Keep USB awake.** Set the laptop to never sleep, and turn off USB selective suspend in the power plan's advanced settings. Otherwise Windows can cut power to a USB port mid-set.

Run a full test on the gig laptop with the A9, Deluge and T-1 connected before the show.

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| "DJM-A9 not found" | Mixer not sending MIDI, or on the wrong port | Use the A9's USB A port and check MIDI ON is lit |
| "No output matching 'T-1'" (or 'Deluge') | The synth uses a different port name, or isn't connected | Check the cable, then use part of the name shown in the Outputs list |
| "No such file or directory" | The install or script step was skipped | Repeat the One-time install and Create the script sections |
| Synth tempo far too slow or erratic | A second clock source, such as a DIN cable from a USB host box | Remove other MIDI cables so the Mac is the only clock |
| Synth doesn't move at all | Its transport isn't running, or clock in is off | Press play on the synth and check its clock-in setting |
| A9 shows the wrong BPM | Beat FX channel selector on an empty channel | Set it to the playing channel or Master |

To see exactly what the mixer sends, the free app [MIDI Monitor](https://www.snoize.com/midimonitor/) shows a steady stream of "Clock" messages from the DJM-A9, about 56 per second at 140 BPM. To edit the script, run `open -e ~/bridge.py`.
