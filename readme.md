Dead-Reckoning-Data-Processing

This is an attempt to clean up the code from my previous Dead-Reckoning-Data-Processing repository.

instructions - assume $logfile is the getSense logfile
julia dead-reckoning.jl $logfile  -> modified Acc, Ori, Wifi and the pngs (output1)
julia step-counting.jl $logfile -> steps.txt and path (output2) [use output1 to become output2]
python map-annotate.py dataget/K/logfile_2017_10_18_$i
