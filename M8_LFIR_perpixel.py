from astropy.io import fits
import numpy as np

# Constants
c = 3e10  # Speed of light in cm/s
distance_pc = 1000  # Example distance in parsecs
distance_cm = distance_pc * 3.086e18  # Convert parsecs to cm

# Function to convert from Jy to cgs units (if needed)
def jansky_to_cgs(flux_density):
    return flux_density * 1e-23  # 1 Jy = 1e-23 erg s^-1 cm^-2 Hz^-1


# Function to remove negative values by setting a threshold
def remove_negative_values(data, threshold=0):
    data[data < threshold] = 0
    return data

# Load FITS files for PACS and SPIRE
fits_files = ['m8_60mu_cgs.fits', 'm8_160mu_cgs.fits', 'm8_250mu_cgs.fits', 'm8_350mu_cgs.fits']

# Define corresponding wavelengths in microns
wavelengths = np.array([60, 160, 250, 350]) * 1e-4  # Convert microns to cm

# Convert wavelengths to frequencies
frequencies = c / wavelengths

# Initialize lists to hold data
flux_densities = []
pixel_scale_arcsec = None

# Extract pixel scale from the first FITS file
hdulist = fits.open(fits_files[0])
header = hdulist[0].header
hdulist.close()

# Check for alternative keywords for pixel scale
if 'PIXSCALE' in header:
    pixel_scale_arcsec = header['PIXSCALE']
elif 'CDELT1' in header and 'CDELT2' in header:
    pixel_scale_arcsec = header['CDELT1'] * 3600  # Convert degrees to arcseconds
elif 'CD1_1' in header:
    pixel_scale_arcsec = header['CD1_1'] * 3600  # Convert degrees to arcseconds
elif 'PIXSCAL1' in header:
    pixel_scale_arcsec = header['PIXSCAL1']
elif 'PIXSCAL2' in header:
    pixel_scale_arcsec = header['PIXSCAL2']
else:
    raise ValueError("Pixel scale keyword not found in FITS header.")
    
# Convert pixel scale from arcseconds to steradians
pixel_area_sr = (pixel_scale_arcsec / 3600.0)**2 * (np.pi / 180.0)**2  # Pixel scale in arcsec to sr

# Process each FITS file and extract flux densities
for fits_file in fits_files:
    hdulist = fits.open(fits_file)
    image_data = hdulist[0].data
    hdulist.close()
    
    # Assuming the data is already in units of erg/cm^2/sr/s/Hz
    # Convert to erg/cm^2/s/Hz per pixel
    flux_density = image_data * pixel_area_sr  # Convert to erg/cm^2/s/Hz per pixel
    
    # Remove negative values
    flux_density = remove_negative_values(flux_density)
    
    flux_densities.append(flux_density)
    
# Convert list of flux densities to a 3D numpy array (frequency, y, x)
flux_densities = np.array(flux_densities)

# Integrate flux density over the frequency range for each pixel
# Use cumulative trapezoidal rule to avoid negative values
L_FIR_per_pixel = np.cumsum(np.abs(flux_densities) * frequencies[:, np.newaxis, np.newaxis], axis=0)[-1]

# Correct for distance
L_FIR_per_pixel_total = 4 * np.pi * distance_cm**2 * L_FIR_per_pixel

# Create a new FITS HDU (Header/Data Unit) with the result
hdu = fits.PrimaryHDU(L_FIR_per_pixel_total)

# Update the header with relevant information
hdu.header['BUNIT'] = 'erg/s'  # Unit of the output data
hdu.header['COMMENT'] = 'Far-Infrared Luminosity per pixel'

# Write the result to a new FITS file
hdu.writeto('M8_LFIR.fits', overwrite=True)

print("Far-Infrared Luminosity (L_FIR) per pixel FITS file created: M8_LFIR.fits")

