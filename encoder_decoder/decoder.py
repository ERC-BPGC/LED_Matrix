def decode(arr):

    finalOut = []
    tempOut = []

    tSum = 0
    tCount = 0
    initial = True
    er = False
    erCount = 0
    erInd = True
    cycleCount = 0
    quo = 0
    rem = 0
    m = 0
    critEr = False
    readSuccess = False
    readingTail = False
    received254 = False
    received255 = False

    for k in range(len(arr)):
        i = arr[k]
        if (not received255) and (i != 255) and initial:
            # initial 255 lost
            # fake 255
            initial = False
            received255 = True
        else:
            initial = False
        
        if readingTail:
            if (i != 255) and (i != 254):
                if not readSuccess:
                    quo = rem
                    rem = i
                m += 1
            elif ((i == 254) or (i == 255)) and (m >= 2):
                cycleCount += 1
                m = 0
                readSuccess = True
            elif (m >= 2):
                # 255 or 254 got lost
                cycleCount += 1
                m = 0
                readSuccess = True
            elif i == 254:
                m = 0
            else:
                pass

            if (i == 255) and (not readSuccess):
                print("XD")
                for ind in range(10):
                    if tempOut[ind] == 250:
                        tempOut[ind] = 235

            if readSuccess and er:
                # resolving error
                rSum = (quo * 245) + rem

                for ind in range(10):
                    if tempOut[ind] == 250:
                        if erCount > 1:
                            tempOut[ind] = 235
                        else:
                            tempOut[ind] = rSum - tSum
                
                er = False

            if (i == 255) or (cycleCount == 3):
                readingTail = False
                tSum = 0
                tCount = 0
                initial = True
                cycleCount = 0
                m = 0
                erCount = 0
                readSuccess = False
                received255 = False
                finalOut.extend(tempOut.copy())
                tempOut.clear()
            elif (cycleCount == 2) and (m >= 3):
                # closing 255 is lost
                # closing tail
                readingTail = False
                tSum = 0
                tCount = 0
                initial = True
                cycleCount = 0
                m = 0
                erCount = 0
                readSuccess = False
                received255 = False
                finalOut.extend(tempOut.copy())
                tempOut.clear()
        
        if not readingTail:
            if received255 and (i != 255) and (i != 254) and (tCount < 10):
                # normal index
                tempOut.append(i)
                tSum += i
                tCount += 1
                received255 = False
            elif received255 and (i == 255):
                # index lost
                er = True
                erInd = int((k-1)/2)

                tempOut.append(250)
                erCount += 1
                tCount += 1
                received255 = True
            elif received255 and (i == 254):
                # last index before tail is lost
                er = True
                erInd = int((k-1)/2)

                tempOut.append(250)
                tCount += 1
                erCount += 1

                readingTail = True
                readSuccess = False
            elif (not received255) and (i != 255) and (i != 254) and (tCount < 10):
                # 255 was lost
                # fake 255
                received255 = True
            elif (not received255) and (i == 255):
                received255 = True
            elif ((not received255) and (i == 254)) or tCount == 10:
                readingTail = True
                readSuccess = False
            
            if readingTail and (tCount < 10):
                for x in range(10 - tCount):
                    tempOut.append(235)
                    erCount += 1
    
    if len(tempOut) > 0:
        if readSuccess and er:
            # resolving error
            rSum = (quo * 245) + rem

            for ind in range(10):
                if tempOut[ind] == 250:
                    if erCount > 1:
                        tempOut[ind] = 235
                    else:
                        tempOut[ind] = rSum - tSum
            
            er = False
    
    for x in range(10 - tCount):
        tempOut.append(235)
        erCount += 1
    
    finalOut.extend(tempOut)
    
    return finalOut

        

# check = [254, 0, 45, 254, 0, 45, 254, 0, 45, 20]
# check = [255, 0, 255, 1, 255, 2, 255, 3, 255, 4, 255, 5, 255, 6, 255, 7, 255, 8, 255, 9, 254, 0, 45, 254, 0, 45, 254, 0, 45, 255, 10, 255, 11, 255, 12, 255, 13, 255, 14, 255, 15, 255, 16, 255, 17, 255, 18, 255, 19, 254, 0, 145, 254, 0, 145, 254, 0, 145, 255, 20, 255, 21, 255, 22, 255, 23, 255, 24, 255, 25, 255, 26, 255, 27, 255, 28, 255, 29, 254, 0, 245, 254, 0, 245, 254, 0, 245]
# check = [255, 0, 255, 1, 255, 2, 255, 3, 255, 4, 255, 5, 255, 6, 255, 7, 255, 8, 255, 9, 254, 0, 45, 254, 0, 45, 254, 0, 45, 255, 10, 255, 11, 255, 12, 255, 13, 255, 14, 255, 15, 255, 16, 255, 17, 255, 18, 255, 19, 254, 0, 145, 254, 0, 145, 254, 0, 145, 255, 20, 255, 21, 255, 22, 255, 23, 255, 24, 255, 25, 255, 26, 255, 27, 255, 28, 255, 29, 254, 0, 245, 254, 0, 245, 254, 0, 245]

# print(decode(check))

# length = len(check)
# score = 0

# for m in range(length):
#     tCase = []
#     tCase.extend(check[:m])
#     tCase.extend(check[m+1:])

#     sol = decode(tCase)

#     print(sol, end=" ")

#     if sol == list(range(20)):
#         print("YO !!!")
#         score += 1
#     else:
#         print("SHITTTTTTT!!!!")
#         print(tCase)
#         raise Exception("SADNESS IS REAL !")

# print(score,"/",length)