# Copyright 2013-2020 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)
# ----------------------------------------------------------------------------

from spack import *
import os
import tempfile


class WrfHydro(Package):
    """
    WRF-Hydro is a community modeling system and framework
    for hydrologic modeling and model coupling.
    """

    # NCAR WRF-Hydro homepage and release tarball
    homepage = "https://ral.ucar.edu/projects/wrf_hydro/overview"
    url = "https://github.com/NCAR/wrf_hydro_nwm_public/archive/v5.1.2.tar.gz"
    git = "https://github.com/NCAR/wrf_hydro_nwm_public.git"

    version("master", branch="master")
    version(
        "5.1.2",
        sha256="203043916c94c597dd4204033715d0b2dc7907e2168cbe3dfef3cd9eef950eb7",
    )

    # WRF-Hydro supports multiple build configs, ostensibly
    # set as flags in trunk/NDHMS/template/setEnvar.sh.
    # Override here.
    variant(
        "with_calibration_pkgs",
        default=False,
        description="Installs Python and R modules needed for NWM calibration.",
    )
    variant(
        "hydro_d",
        default="0",
        values=("0", "1"),
        description="Enhanced diagnostic output for debugging: 0=Off, 1=On.",
    )
    variant(
        "spatial_soil",
        default="0",
        values=("0", "1"),
        description="Spatially distributed parameters for NoahMP: 0=Off, 1=On.",
    )
    variant(
        "wrf_hydro_rapid",
        default="0",
        values=("0", "1"),
        description="RAPID model: 0=Off, 1=On.",
    )
    variant(
        "ncep_wcoss",
        default="0",
        values=("0", "1"),
        description="WCOSS file units: 0=Off, 1=On.",
    )
    variant(
        "wrf_hydro_nudging",
        default="0",
        values=("0", "1"),
        description="Streamflow nudging: 0=Off, 1=On.",
    )

    # WRF-Hydro dependencies
    depends_on("autoconf")
    depends_on("automake")
    depends_on("libtool")
    depends_on("m4")
    depends_on("mpi")
    depends_on("netcdf-c~parallel-netcdf")
    depends_on("netcdf-fortran")

    # Required packages for NOAA NWM Calibration Procedure
    RUNTIME_KWARGS = {
        "type": ("build", "run"),
        "when": "+with_calibration_pkgs",
    }

    depends_on("python@3.8.6", **RUNTIME_KWARGS)
    depends_on("r@3.5.1", **RUNTIME_KWARGS)

    # Python modules
    depends_on("py-netcdf4", **RUNTIME_KWARGS)
    depends_on("py-pandas", **RUNTIME_KWARGS)
    depends_on("py-numpy", **RUNTIME_KWARGS)
    depends_on("py-psycopg2", **RUNTIME_KWARGS)
    depends_on("py-psutil", **RUNTIME_KWARGS)

    # R modules
    depends_on("r-data-table", **RUNTIME_KWARGS)
    depends_on("r-ncdf4", **RUNTIME_KWARGS)
    depends_on("r-glue", **RUNTIME_KWARGS)
    depends_on("r-scales", **RUNTIME_KWARGS)
    
    depends_on("r-vctrs", **RUNTIME_KWARGS)
    depends_on("r-tibble", **RUNTIME_KWARGS)
    depends_on("r-ggplot2", **RUNTIME_KWARGS)

    depends_on("r-gridextra", **RUNTIME_KWARGS)
    depends_on("r-plyr", **RUNTIME_KWARGS)
    depends_on("r-hydrogof", **RUNTIME_KWARGS)

    def setup_environment(self, spack_env, run_env):
        nc_c_home = self.spec["netcdf-c"].prefix
        nc_f_home = self.spec["netcdf-fortran"].prefix

        spack_env.append_path("LD_LIBRARY_PATH", nc_c_home.lib)
        spack_env.append_path("LD_LIBRARY_PATH", nc_f_home.lib)
        spack_env.append_path("CPATH", nc_c_home.include)
        spack_env.set("NETCDF_INC", nc_f_home.include)
        spack_env.set("NETCDF_LIB", nc_f_home.lib)

    def install(self, spec, prefix):

        compiler_config = {"pgi": "1", "gcc": "2", "intel": "3"}

        # Set the compiler flag for ./configure based on active
        # compiler family
        try:
            configure_args = [compiler_config[self.spec.compiler.name]]
        except KeyError:
            raise InstallError(
                "Compiler not recognized nor supported: {}".format(
                    self.spec.compiler.name
                )
            )

        # Set up virtual setEnvar.sh file
        set_envar = [
            "#!/bin/bash",
            "export WRF_HYDRO=1",
            "export HYDRO_D=" + spec.variants["hydro_d"].value,
            "export SPATIAL_SOIL=" + spec.variants["spatial_soil"].value,
            "export WRF_HYDRO_RAPID=" + spec.variants["wrf_hydro_rapid"].value,
            "export NCEP_WCOSS=" + spec.variants["ncep_wcoss"].value,
            "export WRF_HYDRO_NUDGING="
            + spec.variants["wrf_hydro_nudging"].value,
        ]

        # Configure and build in trunk/NDHMS rather than root source
        with working_dir(join_path("trunk", "NDHMS")):
            copy(join_path("template", "setEnvar.sh"), "setEnvar.sh")
            configure(*configure_args)
            start_build = Executable("./compile_offline_NoahMP.sh")

            with tempfile.NamedTemporaryFile(mode="w") as fp:
                fp.write("\n".join(set_envar))
                fp.flush()
                start_build(fp.name)

        # Install compiled binaries
        mkdir(prefix.bin)
        install(
            join_path("trunk", "NDHMS", "Run", "wrf_hydro.exe"), prefix.bin
        )
        install(
            join_path("trunk", "NDHMS", "Run", "wrf_hydro_NoahMP.exe"),
            prefix.bin,
        )
