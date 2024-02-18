def encode(indexArr):
    tCount = 0
    tSum = 0

    outAr = []
    outSt = ""

    for i in indexArr:
        
        outAr.append(255)
        outAr.append(i)

        outSt += chr(i)

        tCount += 1
        tSum += i

        if tCount == 10:
            for j in range(3):
                
                rem = tSum % 245
                quo = int((tSum - rem) / 245)

                outAr.append(254)
                outAr.extend([quo, rem])

                outSt += chr(quo) + chr(rem) + chr(254)
            
            tCount = 0
            tSum = 0
    
    return outAr, outSt

# encode(list(range(0,30)))