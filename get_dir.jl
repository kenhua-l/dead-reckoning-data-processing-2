using DataFrames

id = ARGS[1]
println(isfile("$id.txt"))
dir_df = DataFrame(TIMESTAMP = Float64[], VALUE0 = Float64[], VALUE1 = Float64[], VALUE2 = Float64[], VALUE_MEAN = Float64[])
open("$id.txt", "r") do f
    for line in eachline(f)
        if line != ""
            if line[1] != '%'
                segment = split(line, ";")
                if segment[1] == "AHRS"
                    time = parse(Float64, segment[2])
                    p_x = parse(Float64, segment[4])
                    r_y = parse(Float64, segment[5])
                    y_z = parse(Float64, segment[6])
                    if y_z < 0
                        y_z = y_z * -1
                    elseif y_z > 0
                        y_z = 360 - y_z
                    end
                    o_mean = sqrt(p_x ^ 2 + r_y ^ 2 + y_z ^ 2)
                    push!(dir_df, [time y_z p_x r_y o_mean])
                end
            end
        end
    end
end

println(mean(dir_df[:VALUE_MEAN]))
