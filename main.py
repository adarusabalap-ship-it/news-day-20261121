import os
import pathlib
import shutil

HERE = pathlib.Path(__file__).resolve().parent
OUT = pathlib.Path(os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output")

LIMIT_BYTES = 1 << 20
LIMIT_SIDE = 1024
PNG_SIG = b"\x89PNG\r\n\x1a\n"


def inspect(path):
    """Read the picture and refuse anything the gate would refuse."""
    raw = path.read_bytes()
    if not raw.startswith(PNG_SIG):
        raise SystemExit("%s is not a PNG" % path.name)
    if len(raw) > LIMIT_BYTES:
        raise SystemExit("%s is %d bytes, over the 1 MiB cap" % (path.name, len(raw)))
    width = int.from_bytes(raw[16:20], "big")
    height = int.from_bytes(raw[20:24], "big")
    if not width or not height:
        raise SystemExit("%s has no readable size" % path.name)
    if width > LIMIT_SIDE or height > LIMIT_SIDE:
        raise SystemExit("%s is %dx%d, over %d" % (path.name, width, height, LIMIT_SIDE))
    return width, height, len(raw)


def main():
    src = HERE / "entry.png"
    width, height, size = inspect(src)
    OUT.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, OUT / "entry.png")
    print("entry.png %dx%d, %d bytes -> %s" % (width, height, size, OUT))


if __name__ == "__main__":
    main()
