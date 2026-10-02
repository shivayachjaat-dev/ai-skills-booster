#!/usr/bin/env python3
import sys
import os

def analyze_fits(filepath):
    if not os.path.exists(filepath):
        print(f"Error: File '{filepath}' does not exist.")
        sys.exit(1)

    try:
        from astropy.io import fits
        from astropy.wcs import WCS
    except ImportError:
        print("Error: Astropy is required. Run 'pip install astropy'.")
        sys.exit(1)

    print("=" * 65)
    print(f"Analyzing Astronomical FITS File: {os.path.basename(filepath)}")
    print("=" * 65)

    with fits.open(filepath) as hdul:
        print(f"HDU Extensions: {len(hdul)}")
        for idx, hdu in enumerate(hdul):
            shape_str = str(hdu.data.shape) if hdu.data is not None else "No Data"
            print(f"  HDU #{idx}: Name={hdu.name}, Type={type(hdu).__name__}, Shape={shape_str}")

        primary = hdul[0]
        hdr = primary.header
        
        keys_of_interest = ['TELESCOP', 'INSTRUME', 'OBJECT', 'EXPTIME', 'DATE-OBS', 'FILTER']
        print("\nKey Observation Metadata:")
        for k in keys_of_interest:
            if k in hdr:
                print(f"  {k:<12}: {hdr[k]}")

        try:
            wcs = WCS(hdr)
            if wcs.has_celestial:
                print("\nWorld Coordinate System (WCS) Found:")
                print(f"  Projection Type: {wcs.wcs.ctype[0]} / {wcs.wcs.ctype[1]}")
                print(f"  Reference Pixel: {wcs.wcs.crpix}")
                print(f"  Ref Coordinates: {wcs.wcs.crval} deg")
        except Exception as e:
            print(f"\nNo valid celestial WCS: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python fits_header_analyzer.py <path-to-fits-file>")
        sys.exit(1)
    analyze_fits(sys.argv[1])
