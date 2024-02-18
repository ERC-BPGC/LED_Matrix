import random
import encoder
import decoder

if str(input("generate data  y/Y: ")) in ("y", "Y", ""):
    
    data = []
    for x in range(800):
        data.append(random.randint(0,231))
    
    print(data)

    z = str(input("Enter to encode : "))
    
    solution = data.copy()
    data = encoder.encode(data)

    print("ARRAY : ")
    print(data[0])
    print("STR : ")
    print(data[1])

    print("\n\nBYTE COUNT :", len(data[0]))

    if str(input("begin sequential distruction y/Y : ")) in ("y", "Y", ""):

        length = len(data[0])
        check = data[0].copy()
        score = 0
        
        for m in range(length):
            tCase = []
            tCase.extend(check[:m])
            tCase.extend(check[m+1:])

            sol = decoder.decode(tCase)

            print("", end=".........")

            if sol == solution:
                print("✅")
                score += 1
            else:
                print("❌")
        
        print(score,"/",length)

    safeCount = 0
    
    if str(input("begin random distruction y/Y : ")) in ("y", "Y", ""):

        while True:

            d = int(input("number of bytes to remove : "))
            if d < 2:
                print("min d = 2")

            score = 0

            while True:
                check = data[0].copy()

                for j in range(d):
                    check.pop(random.randint(0,len(check) - 1))
                
                sol = decoder.decode(check)

                if sol == solution:
                    print("✅", end="..")
                    score += 1
                    print(score)
                else:
                    print("FINAL SCORE :", score)
                    break
        