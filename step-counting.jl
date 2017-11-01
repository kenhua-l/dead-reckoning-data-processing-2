using DataFrames

folder = ARGS[1]
rate = 90
K = 0.45
threshold = 2.1

A = readtable("$folder/Accelerometer.txt", separator='\t')
B = readtable("$folder/Orientation.txt", separator='\t')
row_number=nrow(A)
t=1/rate
noStep=0
flagUp=0
timestamp=[]
angle=[]
D=sqrt((A[1,2]).^2+(A[1,3]).^2+(A[1,4]).^2)
stepLength=[0 0 0]
meanA=[A[1,2] A[1,3] A[1,4]]
stepPt=[0 0]
ind=0

for i=2:row_number
  accNorm=sqrt((A[i,2]).^2+(A[i,3]).^2+(A[i,4]).^2)
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

noOfStep=(noStep+1)/2
totalLength=sum(stepLength[1:noStep, 2])

siz = size(stepPtDF, 1)/2

stepInt = convert(Int64, floor(siz))
steps = DataFrame()
newTimestamp = []
newAngle = []
for i = 1:stepInt
    push!(newTimestamp, timestamp[i*2])
    push!(newAngle, angle[i*2])
end
steps[:timestamp] = newTimestamp
steps[:step] = 1:stepInt

odd = repeat([1,2], inner =[1], outer = [stepInt])
if length(odd) != size(stepPtDF, 1)
    odd = vcat(odd, 1)
end
stepPtDF[:odd] = odd

if nrow(stepPtDF) % 2 != 0
    stepPtDF = stepPtDF[1:nrow(stepPtDF)-1, :]
end
oddPt = stepPtDF[:odd] .< 2
evenPt = stepPtDF[:odd] .> 1

steps[:max] = stepPtDF[oddPt,:][:x2]
steps[:min] = stepPtDF[evenPt,:][:x2]
steps[:formula] = sqrt(sqrt(abs(steps[:max] - steps[:min]))) * K
steps[:angle] = newAngle

path = DataFrame(ANGLE=steps[:angle], DISTANCE=steps[:formula])
writetable("$folder/steps.txt", steps, quotemark = ' ', separator='\t')
writetable("$folder/path.txt", path, quotemark = ' ', separator=' ')
