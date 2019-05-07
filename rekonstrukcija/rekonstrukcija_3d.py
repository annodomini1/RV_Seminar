import os
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import PIL.Image as im
import numpy as np
# import nrrd

from os.path import join

import imgproc.imlib as imlib
import imgproc.reconstruction as r3d
import kalibracija as calibration
# import calibration


# #%% ---------- NALOZI SLIKE IZ MAPE ----------
# pth = 'C:/Users/PTIT/Desktop/PTIT/data'
# pth = 'Z:/ptit/data'
pth = '/home/martin/Desktop/RV_Seminar/rekonstrukcija'

acquisition_data_pth = join(pth, 'acquisitions', 'klovn30')
calibration_image_fname = join(pth, 'calibration', 'Aneja je pro.jpg')
calibration_data_fname = join(pth, 'calibration', 'tocke_kalibra_aneja.npy')
out_volume_fname = join(pth, 'reconstructions', 'klovn3d.nrrd')

slike, koti = r3d.load_images(acquisition_data_pth, proc=imlib.rgb2gray)

# #%% ---------- DOLOCI 3D KOORDINATE TOCK NA KALIBRU ----------
pts3d = calibration.IRCT_CALIBRATION_OBJECT()
plt.close('all')
r3d.show_points_in_3d(pts3d)

# #%% ---------- OZNACI 8 TOCK NA KALIBRU, KI NAJ OZNACUJEJO SREDISCE KROGEL ----------
if not os.path.exists(calibration_data_fname):
    calibration_image = np.array(im.open(calibration_image_fname))
    pts2d =  r3d.annotate_caliber_image(calibration_image, calibration_data_fname, n=8)

    plt.close('all')
    pts2d = np.load(calibration_data_fname)[0]
    imlib.showImage(slike[0], iTitle='Oznacena sredisca krogel na kalibru.')
    plt.plot(pts2d[:,0], pts2d[:,1],'mx',markersize=15)

pts2d = np.load(calibration_data_fname)[0]

# #%% ---------- KALIBRIRAJ SISTEM ZA ZAJEM SLIK ----------
Tproj, pts3dproj = r3d.calibrate_irct(pts2d, pts3d)

plt.close('all')
imlib.showImage(slike[0], iTitle='Oznacena sredisca krogel na kalibru.')
plt.plot(pts2d[:,0], pts2d[:,1],'rx', markersize=15)
plt.plot(pts3dproj[:,0], pts3dproj[:,1],'gx', markersize=15)

# #%% ---------- FILTRIRANJE 2D SLIK PRED POVRATNO PROJEKCIJO ----------
slika = np.squeeze(slike[0])
tip_filtra = 'hann'  # none, ram-lak, cosine, hann, hamming
slika_f = r3d.filter_projection(slika, tip_filtra, cut_off=0.75)
imlib.showImage(slika_f, iCmap=cm.jet)

# #%% ---------- REKONSTRUKCIJA 3D SLIKE ----------
# FBP = Filtered BackProjection
vol = r3d.fbp(slike[::1], koti[::1], Tproj,
              filter_type='hann', sampling_mm=[3]*3,
              out_fname=out_volume_fname)

