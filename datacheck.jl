using Gadfly
using DataFrames

folder = ARGS[1]
type_ = ARGS[2] #1 if data_logger, 0 if getSense
println(folder)
start = ""
time_format = Dates.DateFormat("H:M:S.s")

if isfile("$folder/Accelerometer.txt")
    println("processing Accelerometer")
    acc = readtable("$folder/Accelerometer.txt", separator='\t')
    if (:USER_ID in keys(acc.colindex))
        delete!(acc, :USER_ID)
    end
    if (:ACCURACY in keys(acc.colindex))
        delete!(acc, :ACCURACY)
    end
    if (:CUR_TIME in keys(acc.colindex))
        delete!(acc, :CUR_TIME)
    end
    acc[:VALUE_MEAN] = sqrt(acc[:VALUE0] .^ 2 + acc[:VALUE1] .^ 2 + acc[:VALUE2] .^ 2)
    if (type_ == "1") #data_logger type
        time = [0.0]
        global start = DateTime(acc[:TIMESTAMP][1], time_format)
        println(start)
        for r in acc[:TIMESTAMP][2:end]
            spent = DateTime(r, time_format) - start
            spent = Int64(Dates.value(spent)) / 1000
            push!(time, spent)
            # println(spent)
        end
        acc[:TIMESTAMP] = time
    end
    mkpath("$folder/output/")
    writetable("$folder/output/Accelerometer.txt", acc, quotemark=' ', separator='\t')
    p = plot(acc, x=:TIMESTAMP, y=:VALUE_MEAN, Geom.line)
    draw(PNG("$folder/output/Accelerometer.png", 14inch, 8inch), p)
end
if isfile("$folder/Orientation.txt")
    println("processing Orientation")
    ori = readtable("$folder/Orientation.txt", separator='\t')
    if (:USER_ID in keys(ori.colindex))
        delete!(ori, :USER_ID)
    end
    if (:ACCURACY in keys(ori.colindex))
        delete!(ori, :ACCURACY)
    end
    if (:CUR_TIME in keys(ori.colindex))
        delete!(ori, :CUR_TIME)
    end
    ori[:VALUE_MEAN] = sqrt(ori[:VALUE0] .^ 2 + ori[:VALUE1] .^ 2 + ori[:VALUE2] .^ 2)
    ori[:CORRECTED] = copy(ori[:VALUE_MEAN])
    row_number = nrow(ori)
    Curr_MIN_ANGLE = 0
    Curr_MAX_ANGLE = 360
    prev = ori[1, :CORRECTED]
    for i=2:row_number
      if (abs(ori[i, :CORRECTED] - prev) .> 100)
        if ((prev .> Curr_MAX_ANGLE-20 && ori[i, :CORRECTED] .< Curr_MIN_ANGLE+20) || (ori[i, :VALUE_MEAN] .> Curr_MAX_ANGLE-20 && ori[i, :VALUE_MEAN] .< Curr_MIN_ANGLE+20))
          for j=i:row_number
            ori[j, :CORRECTED] = ori[j, :CORRECTED] + 360
          end
          Curr_MIN_ANGLE = Curr_MIN_ANGLE + 360
          Curr_MAX_ANGLE = Curr_MAX_ANGLE + 360
        else
          for j=i:row_number
            ori[j, :CORRECTED] = ori[j, :CORRECTED] - 360
          end
          Curr_MIN_ANGLE = Curr_MIN_ANGLE + 360
          Curr_MAX_ANGLE = Curr_MAX_ANGLE + 360
        end
      end
      prev = ori[i, :CORRECTED]
    end

    if (type_ == "1") #data_logger
        eval = DateTime(ori[:TIMESTAMP][1], time_format) - start
        time = [Int64(Dates.value(eval)) / 1000]
        for r in ori[:TIMESTAMP][2:end]
            spent = DateTime(r, time_format) - start
            spent = Int64(Dates.value(spent)) / 1000
            push!(time, spent)
        end
        ori[:TIMESTAMP] = time
    end
    p = plot(ori, x=:TIMESTAMP, y=:CORRECTED, Geom.line)
    draw(PNG("$folder/output/Orientation.png", 14inch, 8inch), p)
    writetable("$folder/output/Orientation.txt", ori, quotemark=' ', separator='\t')
end
if isfile("$folder/WiFi.txt")
    println("processing Wifi")
    timestamp=[]
    wifi_tags=[]
    wifi=Dict()
    numOfLines=0
    threshold = -46

    open("$folder/WiFi.txt", "r") do f
        for line in eachline(f)
            if numOfLines!=0
                a=split(line, "\t")
                time_lapse = a[1]
                if (type_ == "1") # data_logger
                    #data_logger needs correction
                    correction = start + Dates.Hour(6) + Dates.Minute(4) + Dates.Second(12)
                    time_lapse = DateTime(a[1], time_format) - correction
                    time_lapse = Int64(Dates.value(time_lapse)) / 1000
                end
                push!(timestamp, time_lapse)
                for i=2:4:size(a,1)
                    if (contains(a[i],"NUS") || contains(a[i],"eduroam"))
                        name = string(a[i],"_", replace(a[i+1], ":", ""))
                        # print(name, " ")
                        rssVal = parse(Int,a[i+2])
                        booRss = rssVal > threshold
                        if Symbol(name) in wifi_tags
                            if wifi[name][1] == false
                                wifi[name] = (booRss, wifi[name][2])
                            end
                            push!(wifi[name][2], rssVal)
                        else
                            push!(wifi_tags, Symbol(name))
                            # wifi[name]=zeros(numOfLines-1)
                            arr = fill(-100, (numOfLines-1))
                            push!(arr, rssVal)
                            wifi[name] = (booRss, arr)
                        end
                    end
                end
                # print(numOfLines)
            end
            for (key,value) in wifi
                if length(value[2]) != numOfLines
                    push!(wifi[key][2], -100)
                end
            end
            global numOfLines = numOfLines + 1
            # print("\n")
        end
    end

    wifi_clean = Dict()
    for (key, value) in wifi
        if value[1] == true
            wifi_clean[key] = value[2]
        end
    end

    id=1:numOfLines-1
    wifidf = DataFrame(TIMESTAMP=timestamp)
    for (key, value) in wifi_clean
        wifidf[Symbol(key)]=value
    end
    wifikey = Symbol[]
    for key in collect(keys(wifi_clean))
        push!(wifikey, Symbol(key))
    end
    if size(wifidf, 1) > 0
        p = plot(stack(wifidf,wifikey), x=:TIMESTAMP, y=:value, color=:variable, Geom.line)
        draw(PNG("$folder/output/Wifi.png", 14inch, 8inch), p)
    end
    writetable("$folder/output/WiFi.txt", wifidf, quotemark=' ', separator='\t')
end
