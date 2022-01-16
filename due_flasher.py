from serial import Serial, SerialException
from time import sleep
import subprocess
import sys
import os

#### FUNC DEFS - PIO ####


def get_serial_ports(filter_hwid=False):
    try:
        # pylint: disable=import-outside-toplevel
        from serial.tools.list_ports import comports
    except ImportError:
        raise Exception.GetSerialPortsError(os.name)

    result = []
    for p, d, h in comports():
        if not p:
            continue
        if not filter_hwid or "VID:PID" in h:
            result.append({"port": p, "description": d, "hwid": h})

    if filter_hwid:
        return result

    # # fix for PySerial
    # if not result and IS_MACOS:
    #     for p in glob("/dev/tty.*"):
    #         result.append({"port": p, "description": "n/a", "hwid": "n/a"})
    return result


def wait_for_serial_port(port, before):
    print("Waiting for the new upload port...")
    prev_port = port
    new_port = None
    elapsed = 0
    before = [p["port"] for p in before]
    while elapsed < 5 and new_port is None:
        now = [p["port"] for p in get_serial_ports()]
        for p in now:
            if p not in before:
                new_port = p
                break
        before = now
        sleep(0.25)
        elapsed += 0.25

    if not new_port:
        for p in now:
            if prev_port == p:
                new_port = p
                break

    try:
        s = Serial(new_port)
        s.close()
    except SerialException:
        sleep(1)

    if not new_port:
        sys.stderr.write(
            "Error: Couldn't find a board on the selected port. "
            "Check that you have the correct port selected. "
            "If it is correct, try pressing the board's reset "
            "button after initiating the upload.\n"
        )
        exit()

    return new_port


def run_sub_cmd(cmd):
    # cmd = cmd.split()
    print("Run subcommand\n", cmd)

    output = subprocess.getoutput(cmd)
    print(output)


def serial_due_soft_reset(port, baudrate):
    print("Forcing reset using %dbps open/close on port %s" % (baudrate, port))
    try:
        if not (is_windows):
            s = Serial(port=f"/dev/{port}", baudrate=baudrate)
        else:
            s = Serial(port=f"{port}", baudrate=baudrate)

        s.setDTR(False)
        s.close()
    except Exception as inst:
        print(inst)          # __str__ allows args to be printed directly,
        # print(type(inst))    # the exception instance
        # print(inst.args)     # arguments stored in .args
    pass
    sleep(0.4)  # DO NOT REMOVE THAT (required by SAM-BA based boards)


def check_port():
    exists = False
    for p in get_serial_ports():
        if port_name in str(p):
            exists = True

    return exists


########################################################################################################


print("Hello, this is Arduino hex flasher!\n")
sleep(0.5)

is_windows = sys.platform.startswith('win')
hex_path = ""
port_name = ""
board = ""
availible_boards = ["uno", "due"]

# print("Args: ", sys.argv)

# Sanity checks
if (len(sys.argv) == 4):
    board = sys.argv[1]
    hex_path = sys.argv[2]
    port_name = sys.argv[3]

    print(f"Board type: {board}")
    print(f"Hex File to flash: {hex_path}")
    print(f"Port name to flash: {port_name}")
    sleep(1.0)
else:
    print("(!) Number of arguments is invalid! Aborting...\n")
    print("Usage:\n")
    print(" python due_flasher.py  <board name> <hex file path>  <port name>\n")
    print("availible_boards:", availible_boards)
    exit()

if not check_port():
    print("(!) Could not detect selected port. Aborting")
    exit()

if (board == "due"):

    serial_due_soft_reset(port_name, 1200)  # DUE - erase memory before flash
    port_name = wait_for_serial_port(port_name, get_serial_ports())
    if not (is_windows):
        run_sub_cmd(
            f"./tools/tool-bossac/bossac_linux --info --port \"{port_name}\" --write --verify --reset --erase -U true --boot {hex_path}")
    else:
        run_sub_cmd(
            f"/tools/tool-bossac/bossac_win.exe --info --port \"{port_name}\" --write --verify --reset --erase -U true --boot {hex_path}")

elif (board == "uno"):
    if not (is_windows):
        run_sub_cmd(
            f"./tools/tool-avrdude/linux/avrdude -v -p atmega328p -C ./tools/tool-avrdude/linux/avrdude.conf -c arduino -b 115200 -D -P {port_name} -U flash:w:{hex_path}:i")
    else:
        run_sub_cmd(
            f"/tools/tool-avrdude/win/avrdude.exe -v -p atmega328p -C ./tools/tool-avrdude/win/avrdude.conf -c arduino -b 115200 -D -P {port_name} -U flash:w:{hex_path}:i")

print("\nFlash complete !")
exit()
