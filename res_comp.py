import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# -----------------------------
# Load data
# -----------------------------
df_rocketpy_custom_aero = pd.read_csv("Bluewren_SAC_rocketpy_custom_aero.csv")
df_rocketpy_cfd = pd.read_csv("Bluewren_SAC_rocketpy_CFD.csv")
df_telem = pd.read_csv("TeleMegaBluewrenSAC(in).csv")

ALT_OFFSET = 1401  # subtract this from RocketPy Z to match TeleMega reference

# -----------------------------
# Trim each dataset to apogee
# -----------------------------
# --- TeleMega trim to apogee ---
telem_h = df_telem["height"]
telem_apogee_idx = telem_h.idxmax()  # index of first max
df_telem_trim = df_telem.loc[:telem_apogee_idx].copy()

# --- RocketPy custom aero trim to apogee ---
rocketpy_h = df_rocketpy_custom_aero[" Z (m)"] - ALT_OFFSET  # apply offset BEFORE apogee detection
rocketpy_apogee_idx = rocketpy_h.idxmax()
df_rocketpy_trim = df_rocketpy_custom_aero.loc[:rocketpy_apogee_idx].copy()

# --- RocketPy CFD trim to apogee ---
rocketpy_cfd_h = df_rocketpy_cfd[" Z (m)"] - ALT_OFFSET
rocketpy_cfd_apogee_idx = rocketpy_cfd_h.idxmax()
df_rocketpy_cfd_trim = df_rocketpy_cfd.loc[:rocketpy_cfd_apogee_idx].copy()

# -----------------------------
# Plot altitude vs time (trimmed to apogee)
# -----------------------------
plt.plot(df_telem_trim["time"], df_telem_trim["height"], label="TeleMega")

plt.plot(
    df_rocketpy_trim["Time (s)"],
    df_rocketpy_trim[" Z (m)"] - ALT_OFFSET,
    label="RocketPy Custom Aero",
)

plt.plot(
    df_rocketpy_cfd_trim["Time (s)"],
    df_rocketpy_cfd_trim[" Z (m)"] - ALT_OFFSET,
    label="RocketPy CFD",
)

plt.xlabel("Time (s)")
plt.ylabel("Altitude (m)")
plt.title("Bluewren SAC Flight: Altitude vs Time (Trimmed to Apogee)")
plt.grid(True)
plt.legend()
plt.show()

# -----------------------------
# % error calculations (vs TeleMega)
# -----------------------------
def pct_err(pred: float, truth: float) -> float:
    """Signed percent error: positive means pred > truth."""
    return 100.0 * (pred - truth) / truth

def abs_pct_err(pred: float, truth: float) -> float:
    """Absolute percent error magnitude."""
    return 100.0 * abs(pred - truth) / truth

# TeleMega apogee (truth)
telem_apogee = float(df_telem["height"].max())
telem_t_apogee = float(df_telem.loc[telem_apogee_idx, "time"])

# RocketPy apogee (already offset via rocketpy_h)
rocketpy_apogee = float(rocketpy_h.max())
rocketpy_t_apogee = float(df_rocketpy_custom_aero.loc[rocketpy_apogee_idx, "Time (s)"])

# RocketPy CFD apogee (already offset via rocketpy_cfd_h)
cfd_apogee = float(rocketpy_cfd_h.max())
cfd_t_apogee = float(df_rocketpy_cfd.loc[rocketpy_cfd_apogee_idx, "Time (s)"])

# Apogee altitude errors
rocketpy_apogee_pct = pct_err(rocketpy_apogee, telem_apogee)
rocketpy_apogee_abs_pct = abs_pct_err(rocketpy_apogee, telem_apogee)

cfd_apogee_pct = pct_err(cfd_apogee, telem_apogee)
cfd_apogee_abs_pct = abs_pct_err(cfd_apogee, telem_apogee)

# Optional: time-to-apogee errors
rocketpy_t_pct = pct_err(rocketpy_t_apogee, telem_t_apogee)
rocketpy_t_abs_pct = abs_pct_err(rocketpy_t_apogee, telem_t_apogee)

cfd_t_pct = pct_err(cfd_t_apogee, telem_t_apogee)
cfd_t_abs_pct = abs_pct_err(cfd_t_apogee, telem_t_apogee)

print("===== APOGEE COMPARISON (vs TeleMega) =====")
print(f"TeleMega apogee:      {telem_apogee * 3.28084:10.2f} m   at t = {telem_t_apogee:8.3f} s\n")

print(f"RocketPy Custom Aero apogee:      {rocketpy_apogee * 3.28084:10.2f} m   at t = {rocketpy_t_apogee:8.3f} s")
print(f"  Apogee % error:     {rocketpy_apogee_pct:+10.2f}%   (abs {rocketpy_apogee_abs_pct:8.2f}%)")
print(f"  Time % error:       {rocketpy_t_pct:+10.2f}%   (abs {rocketpy_t_abs_pct:8.2f}%)\n")

print(f"RocketPy CFD apogee:  {cfd_apogee * 3.28084:10.2f} m   at t = {cfd_t_apogee:8.3f} s")
print(f"  Apogee % error:     {cfd_apogee_pct:+10.2f}%   (abs {cfd_apogee_abs_pct:8.2f}%)")
print(f"  Time % error:       {cfd_t_pct:+10.2f}%   (abs {cfd_t_abs_pct:8.2f}%)")
