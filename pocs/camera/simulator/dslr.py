import os
import random

from threading import Timer

import numpy as np

from astropy import units as u
from astropy.io import fits

from pocs.camera import AbstractCamera
from pocs.utils.images import fits as fits_utils
from pocs.utils import get_quantity_value


class Camera(AbstractCamera):

    def __init__(self, name='Simulated Camera', *args, **kwargs):
        kwargs['timeout'] = kwargs.get('timeout', 0.5 * u.second)
        super().__init__(name, *args, **kwargs)
        self.connect()
        self.logger.info("{} initialised".format(self))

    def connect(self):
        """ Connect to camera simulator

        The simulator merely markes the `connected` property.
        """
        # Create a random serial number if one hasn't been specified
        if self._serial_number == 'XXXXXX':
            self._serial_number = 'SC{:04d}'.format(random.randint(0, 9999))

        self._connected = True
        self.logger.debug('{} connected'.format(self.name))

    def take_observation(self, observation, headers=None, filename=None, *args, **kwargs):

        exptime = kwargs.get('exptime', observation.exptime.value)
        if exptime > 1:
            kwargs['exptime'] = 1
            self.logger.debug("Trimming camera simulator exposure to 1 s")

        return super().take_observation(observation,
                                        headers,
                                        filename,
                                        *args,
                                        **kwargs)

    def _end_exposure(self):
        self._is_exposing = False

    def _start_exposure(self, seconds, filename, dark, header, *args, **kwargs):
        exposure_thread = Timer(interval=get_quantity_value(seconds, unit=u.second) + 0.05,
                                function=self._end_exposure)
        self._is_exposing = True
        exposure_thread.start()
        readout_args = (filename, header)
        return readout_args

    def _readout(self, filename, header):
        # Get example FITS file from test data directory
        file_path = os.path.join(
            os.environ['POCS'],
            'pocs', 'tests', 'data',
            'unsolved.fits'
        )
        fake_data = fits.getdata(file_path)

        if header.get('IMAGETYP') == 'Dark Frame':
            # Replace example data with a bunch of random numbers
            fake_data = np.random.randint(low=975, high=1026,
                                          size=fake_data.shape,
                                          dtype=fake_data.dtype)
        fits_utils.write_fits(fake_data, header, filename, self.logger)

    def _process_fits(self, file_path, info):
        file_path = super()._process_fits(file_path, info)
        self.logger.debug('Overriding mount coordinates for camera simulator')
        solved_path = os.path.join(
            os.environ['POCS'],
            'pocs', 'tests', 'data',
            'solved.fits.fz'
        )
        solved_header = fits_utils.getheader(solved_path)
        with fits.open(file_path, 'update') as f:
            hdu = f[0]
            hdu.header.set('RA-MNT', solved_header['RA-MNT'], 'Degrees')
            hdu.header.set('HA-MNT', solved_header['HA-MNT'], 'Degrees')
            hdu.header.set('DEC-MNT', solved_header['DEC-MNT'], 'Degrees')

        self.logger.debug("Headers updated for simulated image.")
        return file_path
