#!/usr/bin/env python3
"""
Test script for ASUS Router Prometheus Exporter

This script tests the connection to your ASUS router and verifies
that the AsusRouter library can fetch basic metrics.
"""

import asyncio
import os
import sys

from asusrouter import AsusData, AsusRouter


async def test_connection():
    """Test connection to ASUS router"""

    # Get configuration
    hostname = os.getenv("ASUS_HOSTNAME", "192.168.1.1")
    username = os.getenv("ASUS_USERNAME", "admin")
    password = os.getenv("ASUS_PASSWORD")
    use_ssl = os.getenv("ASUS_USE_SSL", "false").lower() == "true"

    if not password:
        print("❌ Error: ASUS_PASSWORD environment variable is required")
        print("\nUsage:")
        print("  ASUS_PASSWORD=your_password python3 test_connection.py")
        return False

    print("🔗 Testing connection to ASUS router...")
    print(f"   Hostname: {hostname}")
    print(f"   Username: {username}")
    print(f"   Use SSL: {use_ssl}")
    print()

    try:
        # Create router instance
        router = AsusRouter(
            hostname=hostname,
            username=username,
            password=password,
            use_ssl=use_ssl,
        )

        # Test connection
        print("⏳ Connecting to router...")
        await router.async_connect()
        print("✅ Successfully connected to router!")
        print()

        # Test various data endpoints
        test_cases = [
            (AsusData.CPU, "CPU usage"),
            (AsusData.RAM, "RAM usage"),
            (AsusData.WAN, "WAN statistics"),
            (AsusData.DEVICEMAP, "Device information"),
            (AsusData.TEMPERATURE, "Temperature sensors"),
            (AsusData.CLIENTS, "Connected clients"),
        ]

        successful_tests = 0
        total_tests = len(test_cases)

        for data_type, description in test_cases:
            try:
                print(f"📊 Testing {description}...")
                data = await router.async_get_data(data_type)
                if data:
                    print(f"✅ {description}: OK")
                    # Print sample of the data
                    if isinstance(data, dict):
                        for key, value in list(data.items())[:3]:  # Show first 3 items
                            print(f"   {key}: {value}")
                        if len(data) > 3:
                            print(f"   ... and {len(data) - 3} more items")
                    else:
                        print(f"   Data: {str(data)[:100]}...")
                    successful_tests += 1
                else:
                    print(f"⚠️  {description}: No data returned (may not be supported)")
            except Exception as e:
                print(f"❌ {description}: Failed - {e}")
            print()

        print("=" * 50)
        print("📈 Test Summary:")
        print(f"   Total tests: {total_tests}")
        print(f"   Successful: {successful_tests}")
        print(f"   Failed/Unsupported: {total_tests - successful_tests}")

        if successful_tests >= 2:  # At least CPU and RAM should work
            print("✅ Router connection test PASSED!")
            print("🚀 You can now run the Prometheus exporter:")
            print(f"   ASUS_PASSWORD={password} python3 asus_exporter.py")
            return True
        else:
            print("❌ Router connection test FAILED!")
            print(
                "   Your router may not be fully supported by the AsusRouter library."
            )
            print(
                "   Check the compatibility list: https://github.com/Vaskivskyi/asusrouter#supported-devices"
            )
            return False

    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print()
        print("🔧 Troubleshooting tips:")
        print("   1. Check that the router IP address is correct")
        print("   2. Verify username and password")
        print("   3. Ensure the router's web interface is enabled")
        print("   4. Try setting ASUS_USE_SSL=true if the router uses HTTPS")
        print("   5. Check network connectivity with: ping " + hostname)
        return False


def main():
    """Main entry point"""
    print("🧪 ASUS Router Connection Test")
    print("=" * 50)

    try:
        success = asyncio.run(test_connection())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
