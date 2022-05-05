import ctypes
import numpy as np
import pyastar2d.astar
from typing import Optional, Tuple


# Define array types
ndmat_f_type = np.ctypeslib.ndpointer(
    dtype=np.float32, ndim=1, flags="C_CONTIGUOUS")
ndmat_i2_type = np.ctypeslib.ndpointer(
    dtype=np.int32, ndim=2, flags="C_CONTIGUOUS")

# Define input/output types
pyastar2d.astar.restype = ndmat_i2_type  # Nx2 (i, j) coordinates or None
pyastar2d.astar.argtypes = [
    ndmat_f_type,   # weights
    ctypes.c_int,   # height
    ctypes.c_int,   # width
    ctypes.c_int,   # start index in flattened grid
    ctypes.c_int,   # goal index in flattened grid
    ctypes.c_bool,  # allow diagonal
    ctypes.c_int,   # heuristic_override
    ctypes.c_float, # tiebreaker_coefficient
]


def astar_path(
        weights: np.ndarray,
        start: Tuple[int, int],
        goal: Tuple[int, int],
        allow_diagonal: bool = False,
        heuristic_override: int = 0,
        tiebreaker_coefficient: float = 0.0) -> Optional[np.ndarray]:
    """
    Run astar algorithm on 2d weights.
    
    param np.ndarray weights: A grid of weights e.g. np.ones((10, 10), dtype=np.float32)
    param Tuple[int, int] start: (x, y) point to start
    param Tuple[int, int] goal: (x, y) point to end
    param bool allow_diagonal: Whether to allow diagonal moves
    param int heuristic_override: Override heuristic 0=auto, 1=diagonal, 2=manhattan, 3=orthogonal-x, 4=orthogonal-y
    param float tiebreaker_coefficient: Add tiebreaker to heuristic cost, 0=disable, positive enables it by that amount/1000.0
    
    Important: Please take care when using heuristic_override and tiebreaker_coefficient, they may not take the shortest path.
    """
    assert weights.dtype == np.float32, (
        f"weights must have np.float32 data type, but has {weights.dtype}"
    )
    # For the heuristic to be valid, each move must cost at least 1.
    if weights.min(axis=None) < 1.:
        raise ValueError("Minimum cost to move must be 1, but got %f" % (
            weights.min(axis=None)))
    # Ensure start is within bounds.
    if (start[0] < 0 or start[0] >= weights.shape[0] or
            start[1] < 0 or start[1] >= weights.shape[1]):
        raise ValueError(f"Start of {start} lies outside grid.")
    # Ensure goal is within bounds.
    if (goal[0] < 0 or goal[0] >= weights.shape[0] or
            goal[1] < 0 or goal[1] >= weights.shape[1]):
        raise ValueError(f"Goal of {goal} lies outside grid.")

    height, width = weights.shape
    start_idx = np.ravel_multi_index(start, (height, width))
    goal_idx = np.ravel_multi_index(goal, (height, width))

    path = pyastar2d.astar.astar(
        weights.flatten(), height, width, start_idx, goal_idx, allow_diagonal,
        heuristic_override, tiebreaker_coefficient
    )
    return path
