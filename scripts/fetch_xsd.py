"""Download/cache official or user-provided tsrv.001 XSD."""

from __future__ import annotations

import argparse
import urllib.request
from pathlib import Path

_DEFAULT_URL = "https://www.iso20022.org/sites/default/files/media/file/tsrv.001.001.01.xsd"
_CACHE_DIR = Path.home() / ".cache" / "lc-translator" / "xsd"


def main() -> None:
    """Download a tsrv.001 XSD to the local cache."""
    parser = argparse.ArgumentParser(description="Fetch a tsrv.001 XSD schema")
    parser.add_argument(
        "--url",
        default=_DEFAULT_URL,
        help="URL of the XSD to download",
    )
    parser.add_argument(
        "--output",
        default=str(_CACHE_DIR / "tsrv.001.001.01.xsd"),
        help="Destination file path",
    )
    args = parser.parse_args()

    destination = Path(args.output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    print(f"Downloading {args.url} ...")
    try:
        urllib.request.urlretrieve(args.url, destination)
        print(f"Saved to {destination}")
    except Exception as exc:  # noqa: BLE001
        print(f"Failed to download schema: {exc}")
        print(
            "Tip: ISO 20022 schemas often require a login. "
            "You can provide a direct URL with --url or place a schema manually."
        )
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
