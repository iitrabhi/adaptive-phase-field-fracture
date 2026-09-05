#!/usr/bin/env bash
#
# Batch runner — set 1 to run a study, 0 to skip it.
# Studies execute sequentially; each one starts only after the previous finishes.
#
# Usage:
#   bash run.sh
#   bash run.sh 2>&1 | tee run.log

# ---------------------------------------------------------------------------
# 4.1 Accuracy
# ---------------------------------------------------------------------------
RUN_4_1_01=0   # non-adaptive reference, hw=0.5H  (locally refined)
RUN_4_1_02=0   # non-adaptive reference, hw=0.25H (locally refined)
RUN_4_1_03=0   # non-adaptive reference, hw=0.0H  (locally refined)
RUN_4_1_04=0   # adaptive, hw=0.5H
RUN_4_1_05=0   # adaptive, hw=0.25H
RUN_4_1_06=0   # adaptive, hw=0.0H
RUN_4_1_07=0   # non-adaptive reference, hw=0.5H  (globalally refined)
RUN_4_1_08=0   # non-adaptive reference, hw=0.25H (globalally refined)
RUN_4_1_09=0   # non-adaptive reference, hw=0.0H  (globalally refined)

# ---------------------------------------------------------------------------
# 4.2 Sensitivity
# ---------------------------------------------------------------------------
RUN_4_2_01=0   # length-scale sensitivity, ell=5 m
RUN_4_2_02=0   # length-scale sensitivity, ell=10 m
RUN_4_2_03=0   # length-scale sensitivity, ell=20 m

# ---------------------------------------------------------------------------
# 4.3 Interaction
# ---------------------------------------------------------------------------
RUN_4_3_01=1   # two-crevasse interaction, S=15 m
RUN_4_3_02=1   # two-crevasse interaction, S=25 m
RUN_4_3_03=1   # two-crevasse interaction, S=50 m
RUN_4_3_04=1   # two-crevasse interaction, S=100 m

# ---------------------------------------------------------------------------
# 4.4 Competitive
# ---------------------------------------------------------------------------
RUN_4_4_01=1   # five-crevasse competitive growth, S=50 m
RUN_4_4_02=1   # five-crevasse competitive growth, S=70 m
RUN_4_4_03=1   # ten-crevasse competitive growth,  S=70 m

# ---------------------------------------------------------------------------
# 4.5 Parallel
# ---------------------------------------------------------------------------
RUN_4_5_01=0   # parallel scaling, 01-06
RUN_4_5_07=0   # parallel scaling, 30-crevasse

# ---------------------------------------------------------------------------
# 4.6 Boundary
# ---------------------------------------------------------------------------
RUN_4_6_01=0   # boundary condition study, 01
RUN_4_6_02=0   # boundary condition study, 02

# ===========================================================================
# Runner — do not edit below this line
# ===========================================================================

run() {
    local flag=$1
    local toml=$2
    if [ "$flag" -eq 1 ]; then
        echo ""
        echo "========================================================"
        echo "  Running: $toml"
        echo "  Started: $(date)"
        echo "========================================================"
        python3 main.py --input "$toml"
        echo "  Finished: $(date)"
    fi
}

run "$RUN_4_1_01" examples/4.1.accuracy/01.toml
run "$RUN_4_1_02" examples/4.1.accuracy/02.toml
run "$RUN_4_1_03" examples/4.1.accuracy/03.toml
run "$RUN_4_1_04" examples/4.1.accuracy/04.toml
run "$RUN_4_1_05" examples/4.1.accuracy/05.toml
run "$RUN_4_1_06" examples/4.1.accuracy/06.toml
run "$RUN_4_1_07" examples/4.1.accuracy/07.toml
run "$RUN_4_1_08" examples/4.1.accuracy/08.toml
run "$RUN_4_1_09" examples/4.1.accuracy/09.toml

run "$RUN_4_2_01" examples/4.2.sensitivity/01.toml
run "$RUN_4_2_02" examples/4.2.sensitivity/02.toml
run "$RUN_4_2_03" examples/4.2.sensitivity/03.toml

run "$RUN_4_3_01" examples/4.3.interaction/01.toml
run "$RUN_4_3_02" examples/4.3.interaction/02.toml
run "$RUN_4_3_03" examples/4.3.interaction/03.toml
run "$RUN_4_3_04" examples/4.3.interaction/04.toml

run "$RUN_4_4_01" examples/4.4.competitive/01.toml
run "$RUN_4_4_02" examples/4.4.competitive/02.toml
run "$RUN_4_4_03" examples/4.4.competitive/03.toml

run "$RUN_4_5_01" examples/4.5.parallel/01-06.toml
run "$RUN_4_5_07" examples/4.5.parallel/07.toml

run "$RUN_4_6_01" examples/4.6.boundary/01.toml
run "$RUN_4_6_02" examples/4.6.boundary/02.toml

echo ""
echo "All selected studies complete."
