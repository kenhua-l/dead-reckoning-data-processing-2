using DataFrames

folder = ARGS[1]
println(folder)

steps = readtable("$folder/output/Steps.txt", separator='\t')

timestamp=[]
wifi_tags=[]
wifi=Dict()
numOfLines=0
threshold = -47

open("$folder/WiFi.txt", "r") do f
    for line in eachline(f)
        if numOfLines!=0
            a=split(line, "\t")
            push!(timestamp, a[1])
            for i=2:4:size(a,1)
                # if (a[i] == "")
                #     continue
                # end
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

minsize = min(size(steps,1), size(wifidf, 1))
step_wifi = Array(String, minsize)
for i=1:minsize
    min_rss = -100
    for (key,value) in wifi_clean
        if value[i] > min_rss
            step_wifi[i] = key
            min_rss = value[i]
        end
    end
end

step_wifi_value =[]
for i=1:length(step_wifi)
    push!(step_wifi_value, Int(wifi_clean[step_wifi[i]][i]))
end

wifi_info = DataFrame(NAME=step_wifi, RSS=step_wifi_value)
writetable("$folder/output/wifi_info.txt", wifi_info, separator=' ')
