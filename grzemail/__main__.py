from .daemon import daemon_main
import logging
import asyncio


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="A Terminal email client for 21st century"
    )
    parser.add_argument("mode", type=str)
    args = parser.parse_args()
    if args.mode == "deamon":
        logging.basicConfig(level=logging.DEBUG)
        asyncio.run(daemon_main())

    if args.mode == "client":
        logging.basicConfig(level=logging.INFO, filename="loger.txt")
        from .client import Grzemail

        Grzemail.run(log="log.txt")
