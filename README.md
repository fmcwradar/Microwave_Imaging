# Radar_Signal_Processing

In this repository you can find python scripts for microwave imaging using a vector network analyzer (VNA) and a frequency modulated continuous wave (FMCW) radar system.

```math
\mathbf{H}_{fit}(s) = \mathbf{D} + s \cdot \mathbf{E} + \mathbf{Z} \cdot \frac{1}{s} + \sum_{k=1}^{n} \mathbf{R}_{k} \cdot \frac{1}{s - p_k}
```

where $\mathbf{D}$ is the constant term, $\mathbf{E}$ is the linear term and $\mathbf{R}_{k}$, $p_k$ are the (possibly complex) residues in matrix form and poles. Additionally poles at the origin ($\mathbf{Z}$) can be fitted explicitly. This is especially useful for modelling conductivities as part of complex permittivities.

## Example

The example shows the fitting of 3-port s-parameters of an RF inductor with center tap. The s-parameters are imported directly from the `s3p` touchstone file.
