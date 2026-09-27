"""
Master Idempotent Data Ingestion Runner
Synchronizes all authoritative agricultural datasets into local database & Azure Table Storage.
Usage:
    python -m ingestion.run_all_sync
"""

import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ingestion.sync_locations import sync_locations
from ingestion.sync_soil import sync_soil
from ingestion.sync_crops import sync_crops
from ingestion.sync_crop_calendar import sync_crop_calendar
from ingestion.sync_advisories import sync_advisories
from ingestion.sync_markets import sync_markets
from seed_community_data import seed_community

def run_all_sync():
    print("=" * 70)
    print("🌾 GRAM VAANI: COMPREHENSIVE AGRICULTURAL DATA SYNCHRONIZATION")
    print("=" * 70)
    start_time = datetime.utcnow()

    summary = {}
    try:
        summary["locations"] = sync_locations()
        summary["soil"] = sync_soil()
        summary["crops"] = sync_crops()
        summary["crop_calendar"] = sync_crop_calendar()
        summary["advisories"] = sync_advisories()
        summary["markets"] = sync_markets()
        seed_community()
        summary["community"] = {"status": "success"}

        total_time = (datetime.utcnow() - start_time).total_seconds()
        print("\n" + "=" * 70)
        print(f"🎉 ALL AGRICULTURAL DATASETS SYNCHRONIZED SUCCESSFULLY IN {total_time:.2f}s!")
        print("=" * 70)
        return summary
    except Exception as e:
        print(f"❌ Synchronization failed: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    run_all_sync()
