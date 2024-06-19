import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
from astropy.wcs import WCS

# Load the FITS file
fits_file = 'M8_LFIR.fits'
hdulist = fits.open(fits_file)
data = hdulist[0].data
header = hdulist[0].header
hdulist.close()

# Get WCS information from the header
wcs = WCS(header)

# Plot the data with WCS coordinates
plt.figure(figsize=(10, 8))
ax = plt.subplot(projection=wcs)
im = ax.imshow(data, cmap='inferno', origin='lower', vmin=2e33, vmax=2e35)
cbar = plt.colorbar(im, ax=ax, label=r'$L_{\mathrm{FIR}}$ (erg/s)', pad = 0)
ax.set_title(r'M8 - FIR Luminosity', fontsize=14)
ax.set_xlabel('Right Ascension (J2000)', fontsize=12)
ax.set_ylabel('Declination (J2000)', fontsize=12)

# Save the plot as a PNG file
plt.savefig('M8_LFIR_plot_wcs.png', bbox_inches='tight', dpi = 100)
#plt.show()
