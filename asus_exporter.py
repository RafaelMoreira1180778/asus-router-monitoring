#!/usr/bin/env python3
"""
ASUS Router Prometheus Exporter
Entry point for the ASUS Router monitoring application
"""

import argparse
import asyncio
import sys

from src.config import ExporterConfig, setup_logging
from src.main import AsusExporter


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="ASUS Router Prometheus Exporter v2.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --hostname 192.168.1.1 --username admin --password mypass
  %(prog)s --help

Environment Variables:
  ASUS_HOSTNAME            Router IP address (default: 192.168.1.1)
  ASUS_USERNAME            Router username (default: admin)
  ASUS_PASSWORD            Router password (required)
  ASUS_USE_SSL             Use SSL connection (default: false)
  EXPORTER_PORT            HTTP server port (default: 8000)
  EXPORTER_COLLECTION_INTERVAL  Metrics collection interval in seconds (default: 15)
  EXPORTER_LOG_LEVEL       Log level (default: INFO)
  EXPORTER_CACHE_TIME      Cache time in seconds (default: 5)
        """,
    )
    parser.add_argument("--hostname", help="Router IP address", default=None)
    parser.add_argument("--username", help="Router username", default=None)
    parser.add_argument("--password", help="Router password", default=None)
    parser.add_argument("--use-ssl", action="store_true", help="Use SSL connection")
    parser.add_argument("--port", type=int, help="HTTP server port", default=None)
    parser.add_argument(
        "--collection-interval",
        type=int,
        help="Metrics collection interval in seconds",
        default=None,
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Log level",
        default=None,
    )
    parser.add_argument(
        "--cache-time",
        type=int,
        help="Cache time in seconds",
        default=None,
    )
    parser.add_argument(
        "--version", action="version", version="ASUS Router Prometheus Exporter v2.0"
    )
    return parser.parse_args()


async def main():
    """Main entry point"""
    try:
        args = parse_args()

        # Load configuration from environment variables first
        try:
            config = ExporterConfig.from_env()
        except ValueError:
            # If environment variables are not set, try to use command line arguments
            if not args.hostname or not args.username or not args.password:
                print("❌ Error: Router credentials are required")
                print("Either set environment variables or use command line arguments:")
                print("  --hostname <router_ip> --username <username> --password <password>")
                print("Or set environment variables: ASUS_HOSTNAME, ASUS_USERNAME, ASUS_PASSWORD")
                sys.exit(1)

            config = ExporterConfig(
                hostname=args.hostname,
                username=args.username,
                password=args.password,
                use_ssl=args.use_ssl,
                port=args.port or 8000,
                collection_interval=args.collection_interval or 15,
                log_level=args.log_level or "INFO",
                cache_time=args.cache_time or 5,
            )

        # Override with command line arguments if provided
        if args.hostname:
            config.hostname = args.hostname
        if args.username:
            config.username = args.username
        if args.password:
            config.password = args.password
        if args.use_ssl:
            config.use_ssl = args.use_ssl
        if args.port:
            config.port = args.port
        if args.collection_interval:
            config.collection_interval = args.collection_interval
        if args.log_level:
            config.log_level = args.log_level
        if args.cache_time:
            config.cache_time = args.cache_time

        # Setup logging
        setup_logging(config.log_level)

        # Create and run exporter
        exporter = AsusExporter(config)
        await exporter.run_forever()

    except KeyboardInterrupt:
        print("\n🛑 Exporter stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Failed to start exporter: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
