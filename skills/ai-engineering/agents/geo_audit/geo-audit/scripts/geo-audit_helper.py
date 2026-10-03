#!/usr/bin/env python3
"""
GEO Audit Helper & Diagnostic Test Runner
"""
import sys
import os

# Add scripts directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from geo_seo_auditor import GeoSeoAuditor, verify_geo_auditor

def main():
    print("============================================================")
    print("Running Full Website GEO & SEO Audit Verification Suite")
    print("============================================================")
    verify_geo_auditor()
    print("\nSTATUS: Operational and ready.")

if __name__ == "__main__":
    main()
