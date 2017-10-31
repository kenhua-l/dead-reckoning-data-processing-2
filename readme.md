Dead-Reckoning-Data-Processing

This is an attempt to clean up the code from my previous Dead-Reckoning-Data-Processing repository.

(NOT) auto.sh - direction determinant
(NOT) auto2.sh - the whole process from preprocess to map for a single file or loop in folder
(sunset) datacheck.jl - process Acc, Orientation, and Wifi
(INFO) get_dir.jl - sub part of Orientation (for getSense data) - actually just to get the direction of a path (average)
(sunsets) getData-processor.jl - to process getSense data to be compatible to data_logger's
(MAIN) map-annotate.py - draw map using python
map.png - picture of map
(MAIN) step-counting.jl - get the number of steps and direction of steps
(SUB) wifi_detector.jl - get the most strong signal wifi
(SUNSET) wifi-correction - just get wifi and their strength
(MAIN) dead-reckoning.jl - process data


instructions - assume $logfile is the getSense logfile
julia getData-processor.jl $logfile  -> modified Acc, Ori, Wifi and the pngs (output1)
julia step-counting.jl dataget/K/logfile_2017_10_18_$i -> steps.txt (output2) [use output1 to become output2]
python map-annotate.py dataget/K/logfile_2017_10_18_$i
