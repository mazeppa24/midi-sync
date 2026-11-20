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
