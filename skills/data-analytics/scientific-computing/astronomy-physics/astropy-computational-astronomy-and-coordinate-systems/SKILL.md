---
name: astropy-computational-astronomy-and-coordinate-systems
description: "Use this skill to perform computational astronomy, astrophysical data analysis, and celestial mechanics using Astropy. It covers celestial coordinate transformations (ICRS, Galactic, FK5, AltAz), FITS image and table I/O with WCS header mapping, physical units and dimensional quantities, time standards (UTC, TDB, Julian Dates), and cosmological parameter modeling."
domain: data-analytics
category: scientific-computing
subcategory: astronomy-physics
tags:
  - data-analytics
  - scientific-computing
  - astronomy
  - astrophysics
  - astropy
  - fits
  - coordinate-frames
  - celestial-mechanics
technologies:
  - Astropy
  - NumPy
  - SciPy
  - Matplotlib
  - Python
complexity: expert
maturity: stable
tools:
  - python
  - bash
dependencies:
  - astropy@^6.0.0
  - numpy@^1.26.0
  - scipy@^1.12.0
---
# Astropy Computational Astronomy & Coordinate Systems

## Overview

A scientific computing engineering standard for processing astronomical datasets, calculating orbital trajectories, and transforming celestial coordinate frames using Python and the Astropy core library. Astronomical data processing demands strict precision regarding relativistic time scales (UTC vs. TAI vs. TDB), spherical trigonometry frame conversions (ICRS, Galactic, AltAz topocentric), FITS (Flexible Image Transport System) file parsing with World Coordinate Systems (WCS), and physical unit dimension checking. This skill provides production patterns for astrophysicists, data engineers, and AI research agents.

```
+------------------------------------------------------------------------+
|                      Astropy Core Architecture                         |
|                                                                        |
|  [ Physical Units & Quantities ] <---> [ Time & Epoch Management ]     |
|      (astropy.units, u.Quantity)           (astropy.time.Time, JD/MJD) |
|                      |                                |                |
|                      v                                v                |
|  [ Celestial Coordinate Frames ]     [ FITS Data I/O & WCS Mapping ]   |
|   (SkyCoord, ICRS, Galactic, AltAz)     (astropy.io.fits, astropy.wcs) |
|                      |                                |                |
|                      +----------------+---------------+                |
|                                       v                                |
|                        [ Cosmological Distance Models ]                |
|                           (astropy.cosmology.FlatLambdaCDM)            |
+------------------------------------------------------------------------+
```

## When to Use

- Parsing, validating, and modifying scientific FITS images, multi-extension headers, and binary tables.
- Converting astronomical observation targets between equatorial coordinates (RA/Dec in ICRS or FK5) and local observatory horizons (Altitude/Azimuth with atmospheric refraction).
- Performing dimensionally safe physics calculations (velocities, luminosity, parsecs, light-years) with automated unit cancellation.
- Computing cosmological distances (angular diameter distance, luminosity distance, lookback time) using standard $\Lambda\text{CDM}$ parameterizations.

## When NOT to Use

- General tabular data manipulation with no astronomical spatial/coordinate context (use pure pandas/Polars).
- Simple cartesian 2D/3D geometry without celestial sphere projection or epoch precession.

## Inputs & Prerequisites

- Python 3.10+ with `astropy`, `numpy`, and `scipy` installed.
- Target astronomical dataset (FITS files, Gaia/SDSS/Kepler catalog tables, or coordinate catalogs).
- Observatory site specifications (latitude, longitude, elevation, and timestamp) for topocentric calculations.

## Core Workflow

### Step 1: Dimensioned Quantities and Physical Unit Safety
Prevent unit calculation errors by wrapping values in `astropy.units`:

```python
import astropy.units as u
from astropy.constants import G, M_earth, R_earth

# Calculate Earth escape velocity with automatic unit simplification
v_escape = ((2 * G * M_earth) / R_earth)**0.5
v_escape_km_s = v_escape.to(u.km / u.s)

print(f"Earth Escape Velocity: {v_escape_km_s:.2f}")
# Output: 11.18 km / s
```

### Step 2: Celestial Coordinate Transformations
Transform celestial targets from ICRS (equatorial) to local horizon (AltAz) for a specific ground-based telescope:

```python
from astropy.coordinates import SkyCoord, EarthLocation, AltAz
from astropy.time import Time
import astropy.units as u

# Target: Crab Nebula (M1)
crab = SkyCoord.from_name("M1")

# Observation site: Keck Observatory, Mauna Kea, Hawaii
keck = EarthLocation.of_site("Keck Observatory")

# Observation epoch: 2026-10-15 08:30:00 UTC
obs_time = Time("2026-10-15 08:30:00", scale="utc")

# Transform to local horizon frame
altaz_frame = AltAz(obstime=obs_time, location=keck)
crab_altaz = crab.transform_to(altaz_frame)

print(f"Crab Nebula Altitude: {crab_altaz.alt:.2f}, Azimuth: {crab_altaz.az:.2f}")
if crab_altaz.alt > 30 * u.deg:
    print("Target is observable above airmass limit (>30 deg).")
```

### Step 3: FITS File I/O and WCS Projection
Load high-energy telescope FITS data, inspect headers, and map pixel coordinates to real sky coordinates:

```python
from astropy.io import fits
from astropy.wcs import WCS
import numpy as np

def inspect_fits_file(filepath: str):
    with fits.open(filepath) as hdul:
        hdul.info()
        primary_hdu = hdul[0]
        header = primary_hdu.header
        image_data = primary_hdu.data
        
        # Initialize World Coordinate System
        wcs = WCS(header)
        
        # Convert central pixel to RA/Dec
        ny, nx = image_data.shape
        center_sky = wcs.pixel_to_world(nx / 2, ny / 2)
        print(f"Center Coordinate (ICRS): {center_sky.to_string('hmsdms')}")
        
        return header, image_data, wcs
```

### Step 4: Cosmological Redshift Calculations
Compute luminosity distance and lookback time for high-redshift galaxies:

```python
from astropy.cosmology import FlatLambdaCDM
import astropy.units as u

# Standard Planck 2018 cosmology: H0 = 67.4 km/s/Mpc, Om0 = 0.315
cosmo = FlatLambdaCDM(H0=67.4 * u.km / (u.s * u.Mpc), Om0=0.315)

z = 2.45 # Distant quasar redshift
d_L = cosmo.luminosity_distance(z)
t_lookback = cosmo.lookback_time(z)

print(f"Redshift z={z}: Luminosity Distance = {d_L.to(u.Gpc):.2f}, Lookback Time = {t_lookback.to(u.Gyr):.2f}")
```

## Best Practices & Failure Modes

- **Never Assume UTC for Orbital Mechanics**: High-precision ephemerides require Terrestrial Time (TT) or Barycentric Dynamical Time (TDB) rather than UTC to account for leap seconds.
- **WCS Axis Order**: Remember that NumPy indexing is `[row, col]` (y, x), whereas FITS WCS indexing is `(x, y)` (NAXIS1, NAXIS2). Inverting coordinates leads to flipped astronomical projections.
- **Large FITS Memory Management**: For gigabyte-scale survey images, use `memmap=True` in `fits.open(..., memmap=True)` to avoid reading the entire dataset into RAM.

## Verification & Testing

1. Validate coordinate conversion accuracy against the SIMBAD or VizieR astronomical databases.
2. Verify dimensional consistency: Ensure formulas evaluate without `UnitConversionError`.
3. Check FITS header compliance: Validate with `fits.verify('fix')` to detect non-standard FITS keywords.
