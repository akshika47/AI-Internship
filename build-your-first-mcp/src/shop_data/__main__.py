"""Entry point: `uv run shop-data` (or `python -m shop_data`)."""

from __future__ import annotations

import logging
import sys

from shop_data.config import ConfigError, load_settings
from shop_data.server import create_server


def main() -> None:
    # Logs go to stderr. Never print(): in stdio mode, stdout is the channel the app reads.
    logging.basicConfig(stream=sys.stderr, level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    log = logging.getLogger("shop_data")
    try:
        settings = load_settings()
    except ConfigError as e:
        log.error("Bad configuration: %s", e)
        sys.exit(2)
    if not settings.db_path.is_file():
        log.error("Database not found at %s. Set SHOP_DB_PATH or run: uv run data/make_data.py", settings.db_path)
        sys.exit(2)

    mcp = create_server(settings)
    log.info(
        "shop-data starting: transport=%s db=%s writes=%s",
        settings.transport,
        settings.db_path,
        "on" if settings.allow_writes else "off",
    )
    if settings.transport == "http":
        mcp.run(transport="http", host=settings.host, port=settings.port, show_banner=False)
    else:
        mcp.run(show_banner=False)


if __name__ == "__main__":
    main()
