println("Loading Julia packages - may take some time")
using DataFrames
using Gadfly

# Check if file exists
fileId = ARGS[1]
println("$fileId.txt exists is ", string(isfile("$fileId.txt")))

# Constant Parameters
RSS_THRESHOLD = -50
start = ""
time_format = Dates.DateFormat("H:M:S.s")

# Variables
time = 0.0

# Initialize DataFrames
acc_df = DataFrame(TIMESTAMP = Float64[], VALUE0 = Float64[], VALUE1 = Float64[], VALUE2 = Float64[], VALUE_MEAN = Float64[])
dir_df = DataFrame(TIMESTAMP = Float64[], VALUE0 = Float64[], VALUE1 = Float64[], VALUE2 = Float64[], VALUE_MEAN = Float64[])
wifi_raw_df = DataFrame(TIMESTAMP = Float64[], MAC_ID = String[], RSS = Int64[])

# read file and insert ACCE, AHRS, WIFI data into created dataFrames
open("$fileId.txt", "r") do f
    println("Reading file")
    for line in eachline(f)
        if line != ""
            if line[1] != '%'
                segment = split(line, ";")
                global time = parse(Float64, segment[2])
                if segment[1] == "ACCE"
                    a_x = parse(Float64, segment[4])
                    a_y = parse(Float64, segment[5])
                    a_z = parse(Float64, segment[6])
                    a_mean = sqrt(a_x ^ 2 + a_y ^ 2 + a_z ^ 2)
                    push!(acc_df, [time a_x a_y a_z a_mean])
                elseif segment[1] == "AHRS"
                    p_x = parse(Float64, segment[4])
                    r_y = parse(Float64, segment[5])
                    y_z = parse(Float64, segment[6])
                    # to get 360 coverage
                    if y_z < 0
                        y_z = y_z * -1
                    elseif y_z < 180
                        y_z = 360 - y_z
                    end
                    o_mean = sqrt(p_x ^ 2 + r_y ^ 2 + y_z ^ 2)
                    push!(dir_df, [time y_z p_x r_y o_mean])
                elseif segment[1] == "WIFI"
                    if (contains(segment[4],"NUS") || contains(segment[4],"eduroam"))
                        id = string(segment[4], "[", segment[5], "]")
                        rss = parse(Int64, segment[6])
                        if rss > RSS_THRESHOLD
                            push!(wifi_raw_df, [time id rss])
                        end
                    end
                end
            end
        end
    end
end

# Write Acceleration and Orientation tables and draw their graphs
mkpath("$fileId/")
println("Output Acceleration results - Drawing may take time")
writetable("$fileId/Accelerometer.txt", acc_df, quotemark = ' ', separator='\t')
plotAcc = plot(acc_df, x=:TIMESTAMP, y=:VALUE_MEAN, Coord.Cartesian(xmin=0, xmax=ceil(time)), Geom.line)
draw(PNG("$fileId/Accelerometer.png", 14inch, 8inch), plotAcc)

println("Output Orientation results - Drawing may take time")
writetable("$fileId/Orientation.txt", dir_df, quotemark = ' ', separator='\t')
plotDir = plot(dir_df, x=:TIMESTAMP, y=:VALUE_MEAN, Coord.Cartesian(xmin=0, xmax=ceil(time), ymin=0),  Geom.line)
draw(PNG("$fileId/Orientation.png", 14inch, 8inch), plotDir)

# make wifi data presentable if wifi has data
if size(wifi_raw_df, 1) > 0
    println("Processing WiFi information")
    wifi_df = unstack(wifi_raw_df, :TIMESTAMP, :MAC_ID, :RSS)
    rows = nrow(wifi_df)
    cols = ncol(wifi_df)
    for i = 1:rows
        for j = 1:cols
            if isna(wifi_df[i,j])
                wifi_df[i,j] = -100
            end
        end
    end
    println("Output Wifi results - Drawing may take time")
    writetable("$fileId/Wifi.txt", wifi_df, quotemark = ' ', separator='\t')

    SSID = collect(by(wifi_raw_df, :MAC_ID, nrow)[:MAC_ID])
    SSID_key = Symbol[]
    for key in SSID
        push!(SSID_key, Symbol(key))
    end
    wifi_stack = stack(wifi_df, SSID_key)
    plotWifi = plot(wifi_stack, x=:TIMESTAMP, y=:value, color=:variable, Coord.Cartesian(xmin=0, xmax=ceil(time)), Geom.line)
    draw(PNG("$fileId/Wifi.png", 14inch, 8inch), plotWifi)
else
    println("No Wifi Data - Just make do with dead-reckoning method")
end
