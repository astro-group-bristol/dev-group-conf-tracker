#!/usr/bin/env python3

from astroquery.vizier import Vizier
from astropy.coordinates import SkyCoord
import astropy.units as u
import numpy as np
import pandas as pd
import argparse

Vizier.ROW_LIMIT = -1


# SURVEYS

SURVEYS = [
    ("VIII/97/catalog", 74),        # VLSSr
    ("VIII/62/wenss", 325),         # WENSS
    ("J/A+A/598/A78/table3", 150),  # TGSS
    ("VIII/92/first14", 1400),      # FIRST
    ("VIII/81B/sumss212", 843),     # SUMSS
]


# FLUX EXTRACTION

def extract_flux(table):
    for col in table.colnames:
        name = col.lower()
        if "flux" in name or name.startswith("s") or name.startswith("f"):
            try:
                arr = np.array(table[col], dtype=float)
                arr = arr[~np.isnan(arr)]
                if len(arr) > 0:
                    return float(np.nanmean(arr))
            except:
                continue
    return None



# SED data


def build_sed(ra, dec, radius_arcsec):
    """
    Appends the fluxes found in Vizier, use the output to build full SEDs
    """
    coord = SkyCoord(ra, dec, unit="deg")

    sed = []

    for cat, freq in SURVEYS:

        try:
            result = Vizier.query_region(
                coord,
                radius=radius_arcsec * u.arcsec,
                catalog=cat
            )

            if len(result) == 0:
                continue

            table = result[0]
            flux = extract_flux(table)

            if flux is None:
                continue

            sed.append({
                "freq_MHz": freq,
                "flux_Jy": flux,
                "catalog": cat
            })

        except Exception as e:
            print(f"[WARN] {cat} failed: {e}")

    df = pd.DataFrame(sed)

    if len(df) == 0:
        print("\nNo SED points found. Try increasing radius.\n")
        return df

    return df.sort_values("freq_MHz")



# Arguments

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Build a radio SED using VizieR archival surveys."
    )

    parser.add_argument("--ra", type=float, required=True,
                        help="Right ascension (deg)")

    parser.add_argument("--dec", type=float, required=True,
                        help="Declination (deg)")

    parser.add_argument("--radius", type=float, default=30.0,
                        help="Match radius in arcsec (default 30)")

    parser.add_argument("--out", type=str, default=None,
                        help="Optional output CSV file")

    args = parser.parse_args()

    sed = build_sed(args.ra, args.dec, args.radius)

    print("\n     SED     \n" )
    print(sed.to_string(index=False))

    if args.out and len(sed) > 0:
        sed.to_csv(args.out, index=False)
        print(f"\nSaved to {args.out}\n")