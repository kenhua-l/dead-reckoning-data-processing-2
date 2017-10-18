
path = []
start_point = (63.5, 11.3)
north = 30.0
scale = 27 #27 pixels : 1meter

wifi1_location = (0, 19.45)
wifi2_location = (12.42, 4.65)

wifi3 = "NUSOPEN_00270d49491e"
wifi3_location = (25.05, 11.83)
wifi4 = "NUS_STU_00270d494b8c"
wifi4_location = (45.32, 12.73)

wifi5_location = (51.22, 20.68)
wifi6_location = (51.00, 14.77)
wifi7_location = (55.69, 13.28)
wifi8_location = (60.60, 15.07)
wifi9_location = (60.57, 20.07)

fileName="data/22-48-51-copy/output/Steps.txt"
wifiFileName="data/22-48-51-copy/output/wifi.txt"

current_time = 0.0
wifiRow = 1
steps = readtable(fileName, separator='\t')
wifi = readtable(wifiFileName, separator='\t')
for r in eachrow(steps)
    current_time = r[1, :timestamp]
    while wifi[wifiRow, :TIMESTAMP] < current_time
        wifiRow +=1
    end
    (val, ind) = findmax(wifi[wifiRow])
end
steps_row = nrow(steps)
nrow(wifi)
