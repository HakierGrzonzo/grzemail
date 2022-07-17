import logging
from .services import config_class as config

logging.basicConfig(level=logging.INFO, filename="loger.txt")


async def main(app_factory):
    app = await app_factory()
    await app.run_async()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="A Terminal email client for 21st century"
    )
    parser.add_argument("mode", type=str)
    args = parser.parse_args()
    if args.mode.lower() == "client":
        from .client import Grzemail

        Grzemail.run(log="log.txt")
