# ARRAY=(13_07_27 13_20_50 13_57_14 14_00_53 14_14_53 14_16_34 14_19_15 14_38_13 14_41_00 14_43_43)
# ARRAY=(13_07_27 13_20_50 13_57_14 14_00_53 14_14_53 14_16_34 14_19_15 14_38_13 14_41_00 14_43_43)
ARRAY=(10_31_22_05_37 10_31_22_19_07 10_31_22_32_43 10_31_22_41_24 10_31_22_57_19 10_31_23_34_56 10_31_23_43_30 10_31_23_52_45 11_01_00_00_21 11_01_00_07_32 11_01_00_10_46)
for i in "${ARRAY[@]}"
do
  # julia getData-processor.jl K/logfile_2017_10_18_$i
  # julia datacheck.jl dataget/K/logfile_2017_10_18_$i 0
  # julia step-counting.jl dataget/K/logfile_2017_10_18_$i
  # python map-annotate.py dataget/K/logfile_2017_10_18_$i
  # julia dead-reckoning.jl test/[accept]logfile_2017_$i
  python map-out.py test/[accept]logfile_2017_$i
done
