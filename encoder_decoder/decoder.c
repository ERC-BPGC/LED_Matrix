// right the following code for entire data in a frame

void loop(){
    int tempOut[10];

    int tSum = 0;
    int tCount = 0;
    int initial = 1;
    int er = 0;
    int erCount = 0;
    int erInd = 0;
    int cycleCount = 0;
    int quo = 0;
    int rem = 0;
    int m = 0;
    int critEr = 0;
    int readSuccess = 0;
    int readingTail = 0;
    int received254 = 0;
    int received255 = 0;

    // for every byte read i and index k... replace the while loop
    int i,k;

    while (1==1) {
        if ((received254 == 0) && (i != 255) && (initial == 1)) {
            initial = 0;
            received255 = 1;
        } else {
            initial = 0;
        }

        if (readingTail == 1) {
            if ((i != 255) && (i != 254)) {
                if (readSuccess == 0) {
                    quo = rem;
                    rem = i;
                }
                m++;
            } else if (((i == 254) || (i == 255)) && (m >= 2)) {
                cycleCount++;
                m = 0;
                readSuccess = 1;
            } else if (m >= 2) {
                cycleCount++;
                m = 0;
                readSuccess = 1;
            } else if (i == 254) {
                m = 0;
            } else {
                // YO
            }

            if ((i == 255) && (readSuccess == 0)) {
                for(int ind = 0;ind < 10;ind++) {
                    if (tempOut[ind] == 250) {
                        tempOut[ind] = 235;
                    }
                }
            }

            if ((readSuccess == 1) && (er == 1)) {
                int rSum = (quo * 245) + rem;

                for(int ind = 0;ind < 10;ind++) {
                    if (tempOut[ind] == 250) {
                        if (erCount > 1) {
                            tempOut[ind] = 235;
                        } else {
                            tempOut[ind] = rSum - tSum;
                        }
                    }
                }


                er = 0;
            }

            if ((i == 255) || (cycleCount == 3)) {
                readingTail = 0;
                tSum = 0;
                tCount = 0;
                initial = 0;
                cycleCount = 0;
                m = 0;
                erCount = 0;
                readSuccess = 0;
                received255 = 0;

                // tempOut = 10 bytes
            } else if ((cycleCount == 2) && (m >= 3)) {
                readingTail = 0;
                tSum = 0;
                tCount = 0;
                initial = 0;
                cycleCount = 0;
                m = 0;
                erCount = 0;
                readSuccess = 0;
                received255 = 0;

            } else {
                // YO
            }
        }

        if (readingTail == 0) {
            if ((received255 == 1) && (i != 255) && (i != 254) && (tCount < 10)) {
                //tempOut.append(i)
                tSum += i;
                tCount++;
                received255 = 0;
            } else if ((received255 == 1) && (i == 255)) {
                er = 1;
                erInd = (k-1)/2;

                // tempOut.append(250)
                erCount++;
                tCount++;
                received255 = 1;
            } else if ((received255 == 1) && (i == 254)) {
                er = 1;
                erInd =(k-1)/2;

                // tempOut.append(250)
                tCount++;
                erCount++;

                readingTail = 1;
                readSuccess = 0;
            } else if ((received255 == 0) && (i != 255) && (i != 254) && (tCount < 10)) {
                received255 = 1;
            } else if ((received255 == 0) && (i == 255)) {
                received255 = 1;
            } else if (((received255 == 0) && (i == 254)) || (tCount == 10)) {
                readingTail = 1;
                readSuccess = 0;
            } else {
                // YO 
            }

            if ((readingTail == 1) && (tCount < 10)) {
                for (int x = 0;x<10-tCount;x++){
                    // tempOut.append(235)
                    erCount++;
                }
            }
        }
    }

    // this code is to be written after that for loop but withing the FRAME function
    if ((readSuccess == 1) && (er == 1)) {
        int rSum = (quo * 245) + rem;

        for(int ind = 0;ind < 10;ind++) {
            if (tempOut[ind] == 250) {
                if (erCount > 1) {
                    tempOut[ind] = 235;
                } else {
                    tempOut[ind] = rSum - tSum;
                }
            }
        }


        er = 0;
    }

    for (int x = 0;x<10-tCount;x++){
        // tempOut.append(235)
        erCount++;
    }

    // last 10 bytes of frame are now in tempOut
}