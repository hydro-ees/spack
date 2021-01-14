# Copyright 2013-2021 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack import *

class RHydrogof(RPackage):
    """hydroGOF is an R package that provides S3 functions implementing both 
    statistical and graphical goodness-of-fit measures between 
    observed and simulated values, mainly oriented to be used during 
    the calibration, validation, and application of hydrological models."""

    homepage = "https://cran.r-project.org/web/packages/hydroGOF/index.html"
    url      = "https://cran.r-project.org/src/contrib/hydroGOF_0.4-0.tar.gz"
    list_url = "https://cran.r-project.org/src/contrib/Archive/hydroGOF"

    version('0.4.0', sha256='6a109740e36549a9369b5960b869e5e0a296261df7b6faba6cb3bd338d59883b')

    depends_on('r@3.5.1:', type=('build', 'run'))
    depends_on('r-zoo@1.7-2:', type=('build', 'run'))