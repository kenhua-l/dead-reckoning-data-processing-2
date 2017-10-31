using DataFrames
path = []
origin = (370, 1294)
start_point = (63.5, 11.3)
north = 30.0
scale = 27 #27 pixels : 1meter

wifi1_location = (0, 19.45)
wifi2_location = (12.42, 4.65)
wifi3_location = (25.05, 11.83)
wifi4_location = (45.32, 12.73)
wifi5_location = (51.22, 20.68)
wifi6_location = (51.00, 14.77)
wifi7_location = (55.69, 13.28)
wifi8_location = (60.60, 15.07)
wifi9_location = (60.57, 20.07)
wifiDict = Dict("NUS_STU_00270d494b8c" => wifi4_location, "NUSOPEN_00270d49491e" => wifi3_location,
                "eduroam_d4d74844c7a6" => wifi3_location)

fileName="dataget/K/logfile_2017_10_18_13_07_27/output/Steps.txt"
wifiFileName="dataget/K/logfile_2017_10_18_13_07_27/output/WiFi.txt"

current_time = 0.0
index = 1
steps = readtable(fileName, separator='\t')
wifi = readtable(wifiFileName, separator='\t')

wifisteps = DataFrame(timestamp=Float64[], x=Float64[], y=Float64[])
# start_x = start_point[1] * scale + origin[1]
# start_y = origin[2] - start_point[2] * scale
open("dataget/K/logfile_2017_10_18_13_07_27/output/StepsWiFi.txt", "w") do w
    wifiRow = 1
    wifiTestTime = wifi[wifiRow, 1]
    wifiTest = Array(wifi[wifiRow,2:end])
    row = [2, start_point[1], start_point[2]]
    writedlm(w, reshape(row, (1, length(row))))
    delaywrite = []
    for r in eachrow(steps)
        current_time = r[:timestamp][1]
        if wifiTestTime <= current_time
            (val, ind) = findmax(wifiTest)
            if val > -46
                wifiName = String(names(wifi)[ind+1])
                location = wifiDict[wifiName]
                row = [2, location[1], location[2]]
                writedlm(w, reshape(row, (1, length(row))))
                # push!(delaywrite, tuple(4, row))
            end
            wifiRow = wifiRow + 1
            if wifiRow < nrow(wifi)
                wifiTestTime = wifi[wifiRow, 1]
                wifiTest = Array(wifi[wifiRow,2:end])
            elseif wifiRow > nrow(wifi)
                wifiTestTime = 10000
            end
        end
        row = [1, r[:angle], r[:formula]]
        writedlm(w, reshape(row, (1, length(row))))
        # if !isempty(delaywrite)
        #     for i = 1:length(delaywrite)
        #         change = (delaywrite[i][1]-1, delaywrite[i][2])
        #         insert!(delaywrite, i, change)
        #     end
        #     if delaywrite[1][1]==0
        #         row = delaywrite[1][2]
        #         println(delaywrite)
        #         writedlm(w, reshape(row, (1, length(row))))
        #         shift!(delaywrite)
        #     end
        # end
    end
end
