# I understand the instructions and academic honesty policy for this project: 
# Write your name here Karl Liu 
# Define all your functions here
import random

def StartNewGame():
    '''
    generate a nested list including suits and values
          create a sublist that contains one suit and one value
          then apped the sublist to the larger list to creake a deck with 48 cards
    generate a list including players'names
    generate three list for three players'hands
    return these lists

'''
    players=list()
    for i in range(1,4):
        name=input("Enter player {}'s name:\n".format(i))
        players.append(name) 
    card=[]
    deck=[]
    for i in ['Clubs','Golds','Cups','Swords']:
        for j in ['1','2','3','4','5','6','7','8','9','10','11','12']:
            card.append(i)
            card.append(int(j))
            deck.append(card)
            card=[]
    hands1=[]
    hands1.clear()
    hands2=[]
    hands2.clear()
    hands3=[]
    hands3.clear()
    return players,deck,hands1,hands2,hands3

def PullCards(deck,hands1,hands2,hands3):
    '''
    use random.randint to get a random index in the deck list
        this genrate random card from deck
    then add it to players' hands and remove from deck
    '''
    if len(deck)>=9:
        for i in range(3):
            index=random.randint(0,len(deck)-1)
            card=deck[index]
            hands1.append(card)
            deck.remove(card)
            index=random.randint(0,len(deck)-1)
            card=deck[index]
            hands2.append(card)
            deck.remove(card)
            index=random.randint(0,len(deck)-1)
            card=deck[index]
            hands3.append(card)
            deck.remove(card)
    

def sortcards(lst):
    '''
   most important one
   first create a list of suit to sort the hand based on the index,
   which perfectly present a sequence of "Clubs","Golds","Cups","Swords".
   then sort the list with its value without mess up the suits
   
   '''
    suit=["Clubs","Golds","Cups","Swords"]
    lst.sort(key=lambda x:(suit.index(x[0]),x[1]),reverse=False)
    return lst

def Outputdeck(deck):
    '''
    print the deck
    '''
    for i in deck:
        print("{} {}".format(i[0],i[1]))


def OutputHands(palyers,deck,hands1,hands2,hands3):
    '''
    print the players'names for players[]
    then sort the hands of them
    then print them out one by one
    '''
    if len(hands1)>0:
        print("{}".format(players[0]))
        sortedcards1=sortcards(hands1)
        for i in sortedcards1:
            print("{} {}".format(i[0],i[1]))
        print()

        sortedcards2=sortcards(hands2)
        print("{}".format(players[1]))
        for i in sortedcards2:
            print("{} {}".format(i[0],i[1]))
        print()

        sortedcards3=sortcards(hands3)
        print("{}".format(players[2]))
        for i in sortedcards3:
            print("{} {}".format(i[0],i[1]))
        print()
    else:
        print("No one has cards now. Please enter p first.")

    


def ExchangeCars(hands1,hands2,hands3):
    '''
   sort the hand using lambda to create a acsending values list
   then generate three variables to store the minimun value of each hands
   then remove those values from hands
   following the insturction, each hands append its designed variables
    '''
    if len(hands1)>0:
        hands1.sort(key=lambda val:int(val[1]))
        hands2.sort(key=lambda val:int(val[1]))
        hands3.sort(key=lambda val:int(val[1]))
        hands1_min=hands1[0]
        hands2_min=hands2[0]
        hands3_min=hands3[0]
        hands1.remove(hands1_min)
        hands1.append(hands3_min)
        hands2.remove(hands2_min)
        hands2.append(hands1_min)
        hands3.remove(hands3_min)
        hands3.append(hands2_min)
    else:
        print("Please enter p first")
    return hands1,hands2,hands3



def DeclareWinner(hands1,hands2,hands3):
    '''
    add up the values of each hands by using for loop
    create three variables to store values
    generate a dictionary to connect hands and its players
    sort the dictionary in order of their values
    the first one should be the winner
    then using the dictionary cordination to print the result
    '''
    result1=0
    for i in hands1:
            result1+=i[1]
    result2=0
    for i in hands2:
            result2+=i[1]
    result3=0
    for i in hands3:
            result3+=i[1]

    results=dict()
    results[players[0]]=result1
    results[players[1]]=result2
    results[players[2]]=result3
    final=sorted(results.items(),key=lambda x:x[1],reverse=True)
    print("{} has {} points.".format(final[0][0],final[0][1]))
    print("{} has {} points.".format(final[1][0],final[1][1]))
    print("{} has {} points.".format(final[2][0],final[2][1]))
    print('The winner is "{}" with {} points!'.format(final[0][0],final[0][1]))
    if final[0][1]==final[1][1]:
        print('The winner is "{}" with {} points!'.format(final[1][0],final[1][1]))
    if final[0][1]==final[2][1]:
        print('The winner is "{}" with {} points!'.format(final[2][0],final[2][1]))
    
     

def printMenu():
    print("s: start new game")
    print("p: Pull cards for all players")
    print("o: output deck")
    print("h: output players' hand")
    print("e: exchange one card")
    print("d: declare winner")
    print("q: quit",end='\n')
    


# Write the program that uses those functions here
printMenu()
op = input('Select an option:\n')
i=0
while __name__ == '__main__':
    if op =='s':        
        players,deck,hands1,hands2,hands3=StartNewGame()
        printMenu()
        i+=1
    elif op == 'p':
        if i == 0:
            print('Please select option s to start a new game')
            printMenu()
        else:
            PullCards(deck,hands1,hands2,hands3)
            print()
            printMenu()
    elif op == 'o':
        if i == 0:
            print('Please select option s to start a new game')
            printMenu()
        else:
            print()
            Outputdeck(deck)
            print()
            printMenu()
    elif op == 'h':
        if i == 0:
            print('Please select option s to start a new game')
            printMenu()
        else:
            print()
            OutputHands(players,deck,hands1,hands2,hands3)
            print()
            printMenu()
    elif op == 'e':
        if i == 0:
            print('Please select option s to start a new game')
            printMenu()
        else:
            ExchangeCars(hands1,hands2,hands3)
            print()
            printMenu()
    elif op == 'd':
        if i == 0:
            print('Please select option s to start a new game')
            printMenu()
        else:
            DeclareWinner(hands1,hands2,hands3)              
            break
    elif op == 'q':
        break
    else:
        print("Please select the correct one")
        printMenu()
    op = input('Select an option:\n')

##Thank you! Though I use dumb methods to finish this program, coding brings me lots of fun! 
