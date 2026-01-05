from typing import TYPE_CHECKING
import numpy as np
import math
import pandas as pd 
from scipy.interpolate import interp1d

if TYPE_CHECKING:
    from rocket import Rocket


class EmpiricalAero:
    def __init__(self, rocket: "Rocket"):
        self.rocket = rocket
        self.eps_table = pd.read_csv('rocketpy/rocket/eps_table.csv')
        self.nu_table = pd.read_csv('rocketpy/rocket/nu_table.csv')

    def get_drag_coeff(
        self, m: float, re_body: float, re_fins: float, aoa: float 
    ):
        l_tr = self.rocket.total_length
        d_b = self.rocket.body_diameter
        d_d = self.rocket.base_diameter
        l_c = self.rocket.boattail_length
        t_f = self.rocket.fin_thickness
        l_m = self.rocket.fin_midchord_length
        n = self.rocket.n_fins
        a_fp = self.rocket.fin_planform_area
        a_fe = self.rocket.fin_exposed_area
        d_f = self.rocket.body_diameter_fin
        l_n = self.rocket.nosecone_length
        r_s = self.rocket.fin_section_ratio
        
        f_nu = interp1d(self.nu_table["aoa"], self.nu_table["nu"], kind="linear", fill_value="extrapolate")
        f_eps = interp1d(self.eps_table["aoa"], self.eps_table["eps"], kind="linear", fill_value="extrapolate")

        # skin friciton drag (rocket body)
        re_crit = 5e5
        if re_body <= re_crit:
            cf_fb = 1.328 / np.sqrt(re_body)
        else:
            B = re_crit = (0.074 / re_body**0.2) - (1.328 / np.sqrt(re_body))
            cf_fb = (0.074 / re_body**0.2) - (B / re_body)

        # skin friction drag (rocket fins)
        if re_body <= re_crit:
            cf_ff = 1.328 / np.sqrt(re_fins)
        else:
            B = re_crit = (0.074 / re_fins**0.2) - (1.328 / np.sqrt(re_fins))
            cf_ff = (0.074 / re_fins**0.2) - (B / re_fins)

        # interference drag
        c_di = (
            2
            * cf_ff
            * (1 + 2 * (t_f / l_m))
            * ((4 * n * (a_fp - a_fe)) / (math.pi * d_f**2))
        )

        # fin drag
        c_df = 2 * cf_ff * (1 + 2 * (t_f / l_m)) * ((4 * n * a_fp) / (math.pi * d_f**2))

        # body drag
        cd_fb = (
            (1 + (60 / (l_tr / d_b) ** 3) + 0.0025 * (l_tr / d_b))
            * (
                2.7 * (l_n / d_b)
                + 4 * (l_tr / d_b)
                + 2 * (1 - (d_d / d_b)) * (l_c / d_b)
            )
            * cf_fb
        )

        # base drag
        c_db = 0.029 * ((d_d / d_b) ** 3 / np.sqrt(cd_fb))

        # total cd @ 0 aoa
        cd_0 = cd_fb + c_db + c_df + c_di

        eps = f_eps(aoa)
        nu = f_nu(aoa)
        k_fb = 0.08065 * r_s**2 + 1.153 * r_s
        k_bf = 0.1935 * r_s**2 + 0.8174 * r_s + 1
        c_db_alpha = (
            2 * eps * aoa**2
            + ((3.6 * nu * (1.36 * l_tr - 0.55 * l_n)) / (math.pi * d_b)) * aoa**3
        )
        c_df_alpha = aoa**2 * (
            1.2 * ((a_fp * 4) / (math.pi * d_f**2))
            + 3.12 * (k_fb + k_bf - 1) * ((a_fe * 4) / (math.pi * d_f**2))
        )
        cd_uncorrected = cd_0 + c_db_alpha + c_df_alpha

        if m < 0.8:
            return cd_uncorrected / np.sqrt(1 - m**2)
        elif 0.8 < m < 1.1:
            return cd_uncorrected / np.sqrt(1 - 0.8**2)
        else:
            return cd_uncorrected / np.sqrt(m**2 - 1)



    