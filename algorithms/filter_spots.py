# filter_spots.py
#
# Filters detected spots/triplets to keep only those INSIDE nuclei.
# Also generates an interactive HTML overlay of filtered spots on the
# nucleus image (similar to batch_process.ipynb).
#
# Inputs:
#   - Triplets (left, middle, right spot coordinates in microns)
#   - Binary nucleus mask from nuclear_morphology.py
#   - Scale factors (microns per pixel)
#
# Outputs:
#   - _filtered_spots.csv:  same format as _distances.csv but only
#     triplets where ALL 3 spots are inside nuclei
#   - _filtered_spots.html: interactive Plotly overlay on nucleus image

import numpy as np
import csv
from math import sqrt, nan


def is_spot_inside_nucleus(spot_microns, binary_mask, scale):
    """
    Check if a single spot (in microns) falls inside the nuclear mask.

    Parameters
    ----------
    spot_microns : tuple of (x, y, z) in microns
    binary_mask : 2D bool array from segment_nuclei()
    scale : dict with 'X' and 'Y' pixel-to-micron scale factors

    Returns
    -------
    bool : True if the spot is inside a nucleus
    """
    # Convert micron coordinates to pixel coordinates
    col = int(round(spot_microns[0] / scale['X']))
    row = int(round(spot_microns[1] / scale['Y']))

    h, w = binary_mask.shape
    # Out of bounds = outside
    if row < 0 or row >= h or col < 0 or col >= w:
        return False

    return bool(binary_mask[row, col])


def filter_triplets(triplets, binary_mask, scale):
    """
    Filter triplets to keep only those where ALL 3 spots are inside nuclei.

    Parameters
    ----------
    triplets : list of [left_spot, middle_spot, right_spot]
        Each spot is [x, y, z] in microns.
    binary_mask : 2D bool array
    scale : dict with 'X', 'Y' keys

    Returns
    -------
    filtered : list of triplets that passed
    removed_count : int, how many triplets were removed
    """
    filtered = []
    for triplet in triplets:
        left, middle, right = triplet[0], triplet[1], triplet[2]
        # All 3 spots must be inside a nucleus
        if (is_spot_inside_nucleus(left, binary_mask, scale) and
                is_spot_inside_nucleus(middle, binary_mask, scale) and
                is_spot_inside_nucleus(right, binary_mask, scale)):
            filtered.append(triplet)

    removed_count = len(triplets) - len(filtered)
    return filtered, removed_count


def filter_doublets(doublets, binary_mask, scale):
    """
    Filter doublets to keep only those where BOTH spots are inside nuclei.
    """
    filtered = []
    for doublet in doublets:
        if (is_spot_inside_nucleus(doublet[0], binary_mask, scale) and
                is_spot_inside_nucleus(doublet[1], binary_mask, scale)):
            filtered.append(doublet)
    return filtered


def dist(p1, p2):
    return sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2 + (p1[2]-p2[2])**2)


def write_filtered_csv(triplets, left_doublets, right_doublets,
                       lr_doublets, out_path):
    """
    Write filtered spots CSV in the same format as _distances.csv.
    """
    with open(out_path, "w") as f:
        f.write("Xleft,Yleft,Zleft,Xmiddle,Ymiddle,Zmiddle,"
                "Xright,Yright,Zright,leftDist,rightDist,leftRightDist\n")
        for t in triplets:
            left, middle, right = t[0], t[1], t[2]
            f.write(f"{left[0]},{left[1]},{left[2]},"
                    f"{middle[0]},{middle[1]},{middle[2]},"
                    f"{right[0]},{right[1]},{right[2]},"
                    f"{dist(left, middle)},{dist(middle, right)},"
                    f"{dist(left, right)}\n")
        for d in left_doublets:
            f.write(f"{d[0][0]},{d[0][1]},{d[0][2]},"
                    f"{d[1][0]},{d[1][1]},{d[1][2]},"
                    f"{nan},{nan},{nan},"
                    f"{dist(d[0], d[1])},{nan},{nan}\n")
        for d in right_doublets:
            f.write(f"{nan},{nan},{nan},"
                    f"{d[0][0]},{d[0][1]},{d[0][2]},"
                    f"{d[1][0]},{d[1][1]},{d[1][2]},"
                    f"{nan},{dist(d[0], d[1])},{nan}\n")
        for d in lr_doublets:
            f.write(f"{d[0][0]},{d[0][1]},{d[0][2]},"
                    f"{nan},{nan},{nan},"
                    f"{d[1][0]},{d[1][1]},{d[1][2]},"
                    f"{nan},{nan},{dist(d[0], d[1])}\n")


def generate_filtered_html(nucleus_image, filtered_triplets, scale,
                           out_path, left_doublets=None, right_doublets=None,
                           lr_doublets=None, morph_stats=None,
                           spots_rgb=None):
    """
    Generate an interactive Plotly HTML overlay showing ALL filtered spots
    (triplets + doublets) on the detected-spots image.

    The background is the _spots_rgb image (showing all raw detected spots
    as colored rectangles).  Filtered spots are overlaid as filled circles
    so you can see which detected spots passed the nucleus filter.

    Parameters
    ----------
    nucleus_image : 2D numpy array
        Fallback background if spots_rgb is not provided.
    filtered_triplets : list of [left, middle, right] in microns
    scale : dict with 'X', 'Y' keys
    out_path : str, output HTML path
    left_doublets : list of [left, middle] doublets, optional
    right_doublets : list of [middle, right] doublets, optional
    lr_doublets : list of [left, right] doublets, optional
    morph_stats : dict, optional summary stats for title
    spots_rgb : 2D RGB numpy array (H x W x 3), optional
        The _spots_rgb image with raw detected spots drawn on the nucleus
        channel.  Used as the background so detected spots are visible.
    """
    import plotly.graph_objs as go
    import plotly.io as pio

    left_doublets = left_doublets or []
    right_doublets = right_doublets or []
    lr_doublets = lr_doublets or []

    # Use spots_rgb as background if available, otherwise fall back to nucleus
    if spots_rgb is not None:
        rgb = spots_rgb
        if rgb.dtype != np.uint8:
            rgb = np.clip(rgb, 0, 255).astype(np.uint8)
    else:
        # Get 2D slice if 3D
        if len(nucleus_image.shape) == 3:
            slice_2d = nucleus_image[nucleus_image.shape[0] // 2]
        else:
            slice_2d = nucleus_image

        # Normalize to uint8 for display
        if slice_2d.dtype != np.uint8:
            im = slice_2d.astype(np.float32)
            im = (im - im.min()) / (im.max() - im.min() + 1e-10) * 255
            slice_2d = im.astype(np.uint8)

        # Make RGB
        rgb = np.stack([slice_2d, slice_2d, slice_2d], axis=-1)

    fig = go.Figure()
    fig.add_trace(go.Image(z=rgb))

    # --- Helper to convert microns to pixel coords for Plotly ---
    # spot[0] = row position (microns) -> Plotly Y axis
    # spot[1] = col position (microns) -> Plotly X axis
    def to_px(spot):
        plotly_x = spot[1] / scale['Y']   # column
        plotly_y = spot[0] / scale['X']   # row
        return (plotly_x, plotly_y)

    # Channel colors: 647 = green, 488 = red, 555 = blue
    color_left = 'green'     # 647
    color_middle = 'red'     # 488
    color_right = 'blue'     # 555

    # Collect spots by channel and draw connecting lines
    left_spots = []
    middle_spots = []
    right_spots = []

    # --- Triplets: yellow connecting lines + all 3 channel spots ---
    triplet_line_added = False
    for t in filtered_triplets:
        lp, mp, rp = to_px(t[0]), to_px(t[1]), to_px(t[2])
        left_spots.append(lp)
        middle_spots.append(mp)
        right_spots.append(rp)
        # Yellow line connecting left -> middle -> right
        fig.add_trace(go.Scatter(
            x=[lp[0], mp[0], rp[0]], y=[lp[1], mp[1], rp[1]],
            mode='lines',
            line=dict(color='yellow', width=2),
            showlegend=not triplet_line_added,
            name='Triplet Line',
            hoverinfo='skip',
        ))
        triplet_line_added = True

    # --- Doublets: orange connecting lines ---
    doublet_line_added = False
    for d in left_doublets:
        lp, mp = to_px(d[0]), to_px(d[1])
        left_spots.append(lp)
        middle_spots.append(mp)
        fig.add_trace(go.Scatter(
            x=[lp[0], mp[0]], y=[lp[1], mp[1]],
            mode='lines',
            line=dict(color='orange', width=2),
            showlegend=not doublet_line_added,
            name='Doublet Line',
            hoverinfo='skip',
        ))
        doublet_line_added = True

    for d in right_doublets:
        mp, rp = to_px(d[0]), to_px(d[1])
        middle_spots.append(mp)
        right_spots.append(rp)
        fig.add_trace(go.Scatter(
            x=[mp[0], rp[0]], y=[mp[1], rp[1]],
            mode='lines',
            line=dict(color='orange', width=2),
            showlegend=not doublet_line_added,
            name='Doublet Line',
            hoverinfo='skip',
        ))
        doublet_line_added = True

    for d in lr_doublets:
        lp, rp = to_px(d[0]), to_px(d[1])
        left_spots.append(lp)
        right_spots.append(rp)
        fig.add_trace(go.Scatter(
            x=[lp[0], rp[0]], y=[lp[1], rp[1]],
            mode='lines',
            line=dict(color='orange', width=2),
            showlegend=not doublet_line_added,
            name='Doublet Line',
            hoverinfo='skip',
        ))
        doublet_line_added = True

    # --- Filled circles per channel ---
    spot_groups = [
        ('488 spot', color_middle, middle_spots),
        ('647 spot', color_left, left_spots),
        ('555 spot', color_right, right_spots),
    ]

    for name, color, spots in spot_groups:
        if len(spots) > 0:
            xs = [s[0] for s in spots]
            ys = [s[1] for s in spots]
            fig.add_trace(go.Scatter(
                x=xs, y=ys,
                mode='markers',
                marker=dict(
                    color=color, size=5, symbol='circle',
                    opacity=0.9,
                ),
                name=name,
                hovertemplate=(
                    f"{name}<br>"
                    "x: %{x:.1f} px<br>"
                    "y: %{y:.1f} px<br>"
                    "<extra></extra>"
                )
            ))

    # Match the batch_process.ipynb / reference HTML layout exactly:
    # fixed width/height = image size, zero margins, reversed y-axis.
    img_h, img_w = rgb.shape[:2]

    fig.update_layout(
        width=img_w,
        height=img_h,
        hovermode='closest',
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(title=dict(text='X Position (Pixels)')),
        yaxis=dict(autorange='reversed',
                   title=dict(text='Y Position (Pixels)')),
        showlegend=True,
    )

    pio.write_html(fig, out_path)
