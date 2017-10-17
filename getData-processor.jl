using DataFrames

# file = ARGS[1]
# println(file)
id = "2017_10_11_14_15_26"
file = string("dataget/logfile_", id)

println(isfile("$file.txt"))
acc_df = DataFrame(TIMESTAMP = Float64[], VALUE0 = Float64[], VALUE1 = Float64[], VALUE2 = Float64[])
dir_df = DataFrame(TIMESTAMP = Float64[], VALUE0 = Float64[], VALUE1 = Float64[], VALUE2 = Float64[])
wifi_raw_df = DataFrame(TIMESTAMP = Float64[], SSID = String[], MAC_ID = String[], RSS = Int64[])
open("$file.txt", "r") do f
    for line in eachline(f)
        if line != ""
            if line[1] != '%'
                segment = split(line, ";")
                if segment[1] == "ACCE"
                    time = parse(Float64, segment[2])
                    a_x = parse(Float64, segment[4])
                    a_y = parse(Float64, segment[5])
                    a_z = parse(Float64, segment[6])
                    # a_mean = sqrt(a_x ^ 2 + a_y ^ 2 + a_z ^ 2)
                    push!(acc_df, [time a_x a_y a_z])
                elseif segment[1] == "AHRS"
                    time = parse(Float64, segment[2])
                    p_x = parse(Float64, segment[4])
                    r_y = parse(Float64, segment[5])
                    y_z = parse(Float64, segment[6])
                    if y_z < 0
                        y_z = y_z * -1
                    elseif y_z < 180
                        y_z = y_z + 180
                    end
                    # o_mean = sqrt(p_x ^ 2 + r_y ^ 2 + y_z ^ 2)
                    push!(dir_df, [time y_z p_x r_y])
                elseif segment[1] == "WIFI"
                    time = parse(Float64, segment[2])
                    if (contains(segment[4],"NUS") || contains(segment[4],"eduroam"))
                        name = string(segment[4])
                        id = string(segment[5])
                        rss = parse(Int64, segment[6])
                        if rss > -55
                            push!(wifi_raw_df, [time, name, id, rss])
                        end
                    end
                end
            end
        end
    end
end

mkpath("dataget/$id/")
writetable("dataget/$id/Accelerometer.txt", acc_df, quotemark = ' ', separator='\t')
writetable("dataget/$id/Orientation.txt", dir_df, quotemark = ' ', separator='\t')

temp = by(wifi_raw_df, :TIMESTAMP, nrow)
cols = maximum(temp[:x1])
header = String[]
push!(header, "TIMESTAMP")
for col = 1:cols
    push!(header, "SSID")
    push!(header, "MAC_ID")
    push!(header, "RSS")
end

# header = reshape(header, (1, length(header)))

open("dataget/$id/WiFi.txt", "w") do w
    focus_time = ""
    row = header
    for r in eachrow(wifi_raw_df)
        if r[:TIMESTAMP] != focus_time
            writedlm(w, reshape(row, (1, length(row))))
            focus_time = r[:TIMESTAMP]
            row = [focus_time, r[:SSID], r[:MAC_ID], string(r[:RSS])]
        else
            push!(row, r[:SSID])
            push!(row, r[:MAC_ID])
            push!(row, string(r[:RSS]))
        end
    end
end

# writetable("dataget/$id/WiFi.txt", acc_df, separator='\t')
# println(wifi_raw_df)
