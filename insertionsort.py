leaderboard = [6,3,4,1,9,5,3,2]
  
for x in range(1, len(leaderboard)): 

    key = leaderboard[x] 
    j = x-1
    while j >= 0 and key < leaderboard[j]: 
            arr[j + 1] = leaderboard[j] 
            j -= 1
    arr[j + 1] = key