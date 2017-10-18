# ARRAY=(13_07_27 13_20_50 13_57_14 14_00_53 14_14_53 14_16_34 14_19_15 14_38_13 14_41_00 14_43_43)
ARRAY=(13_07_27 13_20_50 13_57_14 14_00_53 14_14_53 14_16_34 14_19_15 14_38_13 14_41_00 14_43_43)

for i in "${ARRAY[@]}"
do
  julia getData-processor.jl K/logfile_2017_10_18_$i
  julia datacheck.jl dataget/K/logfile_2017_10_18_$i 0
  julia step-counting.jl dataget/K/logfile_2017_10_18_$i
  python map-annotate.py dataget/K/logfile_2017_10_18_$i
done
