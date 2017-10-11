using DataFrames
#rate is 70, 75, 80
#threshold could be 1.2-1.5
#ARGS should be fileName, startpoint, endpoint, rate, threshold
folder = ARGS[1]
startpoint = 1
endpoint = 2290
rate = 80
threshold = 1.5
# println(accel, " ", x[2], " ", x[3]," ", x[4]," ", x[5])

A = readtable("$folder/Accelerometer.txt", separator='\t')
B = readtable("$folder/Orientation.txt", separator='\t')
row_number=size(A, 1)
A[:index] = 1:row_number
todelete = startpoint .< A[:index] .< endpoint
A = A[todelete,:]
# delete!(A,:index)

row_number=size(A, 1) #update row_number
# rate = parse(Int, x[4])
t=1/rate
# axOffset = -0.01
# ayOffset = 0.23
# azOffset = -0.17
axOffset = 0
ayOffset = 0
azOffset = 0
# threshold = parse(Float64, x[5])
noStep=0
flagUp=0
timestamp=[]
angle=[]
D=sqrt((A[1,2]-axOffset).^2+(A[1,3]-ayOffset).^2+(A[1,4]-azOffset).^2)
stepLength=[0 0 0]
meanA=[A[1,2] A[1,3] A[1,4]]
stepPt=[0 0]
ind=0

for i=2:row_number
  accNorm=sqrt((A[i,2]-axOffset).^2+(A[i,3]-ayOffset).^2+(A[i,4]-azOffset).^2)
  if(flagUp==1)
    flag=(accNorm-D) > threshold
  else
    flag=(D-accNorm) > threshold
  end

  if(flag==1)

    if(D>accNorm)
      flagUp=1
    else
      flagUp=0
    end
    stepPt = vcat(stepPt,[ind D])
    D = accNorm
    ind = i

    if noStep == 0
        push!(timestamp, A[i,:TIMESTAMP])
        noStep = noStep+1
    end
    push!(timestamp, A[i,:TIMESTAMP])
    noStep = noStep+1
    stepLength = vcat(stepLength, meanA*t)
    meanA=[0 0 0]

  else

    if(((flagUp==1) && D > accNorm) || ((flagUp==0) && D < accNorm))
      D=accNorm
      ind=i
    end

    meanA=meanA+[A[i,2] A[i,3] A[i,4]]
  end
end

direction = []
jd = 1
for i=1:length(timestamp)
    if B[jd, :TIMESTAMP] == timestamp[i]
        push!(direction, sqrt(B[jd,2].^2+B[jd,3].^2+B[jd,4].^2))
        jd = jd + 1
    else
        if B[jd, :TIMESTAMP] < timestamp[i]
            while B[jd, :TIMESTAMP] < timestamp[i]
                jd = jd + 1
            end
            push!(direction, sqrt(B[jd,2].^2+B[jd,3].^2+B[jd,4].^2))
        else
            push!(direction, sqrt(B[jd,2].^2+B[jd,3].^2+B[jd,4].^2))
        end
    end
end

# println(length(direction))
# println(length(timestamp))

stepPtDF = convert(DataFrame, stepPt)
stepPtDF[:index] = 1:size(stepPt,1)
numOfOdd = 0
numOfEven = 0
oddTotal = 0
evenTotal = 0

for i=2:size(stepPtDF, 1)
  if i%2==0
    numOfEven = numOfEven + 1
    evenTotal = evenTotal + stepPtDF[i, :x2]
  else
    numOfOdd = numOfOdd + 1
    oddTotal = oddTotal + stepPtDF[i, :x2]
  end
end

stepPtDF[:index] = 0:size(stepPtDF,1)-1
todelete = 0 .< stepPtDF[:index]
stepPtDF = stepPtDF[todelete,:]
delete!(stepPtDF,:index)
newTimestamp = []
for i = 1:length(todelete)
    if todelete[i]
        push!(newTimestamp, timestamp[i])
        push!(angle, direction[i])
    end
end
timestamp = newTimestamp


#print(stepPtDF)
#print("\n")

evenAverage = evenTotal / numOfEven
oddAverage = oddTotal / numOfOdd
#the minimum threshold of peaks
minOfmax = 100
#the maximum threshold of valleys
maxOfmin = 0

if evenAverage > oddAverage
  #even is max
  for i=2:size(stepPtDF, 1)
    if i%2==0
      if stepPtDF[i, :x2] < minOfmax
        minOfmax = stepPtDF[i, :x2]
      end
    else
      if stepPtDF[i, :x2] > maxOfmin
        maxOfmin = stepPtDF[i, :2]
      end
    end
  end
else
  #even is min
  for i=2:size(stepPtDF, 1)
    if i!%2==0
      if stepPtDF[i, :x2] < minOfmax
        minOfmax = stepPtDF[i, :x2]
      end
    else
      if stepPtDF[i, :x2] > maxOfmin
        maxOfmin = stepPtDF[i, :2]
      end
    end
  end
end

#print("The minimum threshold for peaks is $minOfmax\n")
#print("The maximum threshold for valleys is $maxOfmin\n")


noOfStep=(noStep+1)/2
totalLength=sum(stepLength[1:noStep, 2])

#print("Total Footsteps detected is $noOfStep\n")
#print("Total Length is $totalLength\n")

#writedlm("noodle.txt", stepPt, '\t')
#print(size(stepPtDF, 1)/2 -0.5)

#siz = size(stepPtDF, 1)/2 -0.5
siz = size(stepPtDF, 1)/2

stepInt = convert(Int64, siz)
steps = DataFrame()
newTimestamp = []
newAngle = []
for i = 1:stepInt
    push!(newTimestamp, timestamp[i*2])
    push!(newAngle, angle[i*2])
end
steps[:timestamp] = newTimestamp
steps[:step] = 1:stepInt
#print(stepInt)

#stepPtDF[:odd] = vcat(repeat([1,2], inner =[1], outer = [stepInt]), 1)
stepPtDF[:odd] = repeat([1,2], inner =[1], outer = [stepInt])

#stepPtDF[size(stepPtDF, 1), :odd] =10
oddPt = stepPtDF[:odd] .< 2
#stepPtDF[size(stepPtDF, 1), :odd] =0
evenPt = stepPtDF[:odd] .> 1

steps[:max] = stepPtDF[oddPt,:][:x2]
steps[:min] = stepPtDF[evenPt,:][:x2]
steps[:formula] = sqrt(sqrt(abs(steps[:max] - steps[:min])))
steps[:angle] = newAngle

path = DataFrame(ANGLE=steps[:angle], DISTANCE=steps[:formula])
print(path)
print("\n")
writetable("$folder/output/Steps.txt", steps, separator='\t')
writetable("$folder/output/path.txt", path, separator=' ')
