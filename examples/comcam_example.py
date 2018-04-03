import numpy as np
import lsst.sims.featureScheduler as fs
from lsst.sims.speedObservatory import Speed_observatory
import matplotlib.pylab as plt
import healpy as hp

if __name__ == "__main__":

    # Need to crank up resolution for camcam
    nside = fs.set_default_nside(nside=256)

    survey_length = 20.  # Days
    target_map = fs.standard_goals(nside=nside)
    ra, dec = fs.ra_dec_hp_map(nside=nside)
    out_region = np.where((dec > np.radians(-40)) | (dec < np.radians(-50.)))
    in_region = np.where((dec <= np.radians(-40)) | (dec >= np.radians(-50.)))
    for key in target_map:
        target_map[key][out_region] = 0.
        target_map[key][in_region] = 1.

    years = np.round(survey_length/365.25)
    filters = ['g', 'r', 'i']
    surveys = []

    for filtername in filters:
        bfs = []
        bfs.append(fs.M5_diff_basis_function(filtername=filtername, nside=nside))
        bfs.append(fs.Target_map_basis_function(filtername=filtername,
                                                target_map=target_map[filtername],
                                                out_of_bounds_val=-10., nside=nside))

        bfs.append(fs.North_south_patch_basis_function(zenith_min_alt=50., nside=nside))
        #bfs.append(fs.Zenith_mask_basis_function(maxAlt=78., penalty=-100, nside=nside))
        bfs.append(fs.Slewtime_basis_function(filtername=filtername, nside=nside))
        bfs.append(fs.Strict_filter_basis_function(filtername=filtername))

        weights = np.array([3.0, 1.0, 1., 3., 3.])
        # Might want to try ignoring DD observations here, so the DD area gets covered normally
        surveys.append(fs.Greedy_survey_comcam(bfs, weights, block_size=1, filtername=filtername,
                                               dither=True, nside=nside))

    surveys.append(fs.Pairs_survey_scripted([], [], ignore_obs='DD', min_alt=20.))

    # Set up the DD
    # XXX commenting out because we only have 3 filters loaded.
    #dd_surveys = fs.generate_dd_surveys()
    #surveys.extend(dd_surveys)

    scheduler = fs.Core_scheduler(surveys, nside=nside, camera='comcam')
    observatory = Speed_observatory(nside=nside)
    observatory, scheduler, observations = fs.sim_runner(observatory, scheduler,
                                                         survey_length=survey_length,
                                                         filename='comcam_baseline_%iyrs.db' % years,
                                                         delete_past=True)


# To run maf:
#  python run_glance.py comcam_baseline_0yrs.db comcam_test --camera ComCam

# Time for 20 days:  205min = 3.5hr.  ~10min per day. 
