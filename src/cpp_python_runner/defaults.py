"""Neutral defaults of the package. Project specific settings (paths, exe, instances) belong into the
project that uses this package and are passed in via `Experiment`."""

import os

# Number of exe processes running at the same time. If you compare computation times,
# use at most the number of PHYSICAL cores (two runs on the hyper-threads of one core slow each other down).
# Half of the logical cores is a rough guess for the physical cores.
NUMBER_PROCESSES = max(1, (os.cpu_count() or 2) // 2)

REPETITIONS = 1

# Run the tasks in a random but reproducible order. Otherwise the tasks run sorted by parameter
# configuration and instance size, so the machine load (and with it the measured computation time)
# is systematically different for different configurations.
SHUFFLE_TASKS = True
SHUFFLE_SEED = 42
