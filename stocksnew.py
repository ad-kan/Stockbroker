import discord
from discord import File
from discord.ext import commands
import logging

import time
import asyncio
import json
import random
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)

# IDEAS:
# add 1% multiplier or increased starting bank account with referrals
# types of goods: gold, silver, oil, platinum
# add a bias for some stocks so the prices remain higher. There needs to be a sense of scale, for ex. diamonds can't cost lesser than wheat, etc.
# realistic exchange rate, for ex. diamonds = 1000 wheat
# rand generator for stock prediction needs to depend on market demand
# banks with interest
# implied volatility
# limits for artificial inflation
# unbought/dead stocks need to depreciate by a standard factor but RNG must be stronger 
# events, stock upturns/dowturns, etc.
# have periodic events with high IV goods
# set up permission based commands, need admins/helpers
# make bot add reaction based commands
# trend changes based on volume of stocks bought, not number of times
# stock based businesses
# x + (random.uniform(-0.0575,0.0425)*x) add constant to the random number bounds, but increase bounds by a small amount. also, influencing power will reduce exponentially with people

# CONVENTIONAL DEFINITIONS:
# Order = Type of good being ordered, Amount = Amount of goods being ordered
# Inventory = Goods in user's inventory
# Type = Method of manipulating the said data, ex: type "start" in getgoods() means the amount of goods a user is assigned while starting off

# TODOLIST:
# add .help

# LONGTERM TODOLIST:
# need a bot and server pfp, cash award for dude who makes it
# async with channel.typing():
# do expensive stuff here
# await channel.send('done!')

# Amazon switching:
# /Users/adityakannan/PythonProjects/
# /Users/adityakannan/PythonProjects/

bot = commands.Bot(command_prefix = '.')
bot.remove_command('help')

with open('/Users/adityakannan/PythonProjects/Stocks_Revamped/key.json','r') as keys:
    key = json.load(keys)

goodslist = (
    "gold",
    "silver",
    "oil",
    "platinum",
    "diamond",
    "corn",
    "copper",
    "cotton",
    "sugar",
    "coal",
    "wheat",
    "uranium",
)

def setfileuser(userid,user):
    with open('/Users/adityakannan/PythonProjects/Stocks_Revamped/userdata/'+str(userid)+'.json','w') as userdata:
        json.dump(user,userdata)

def setfileprices(prices): #modularized function because expect future integration with SQL
    with open('/Users/adityakannan/PythonProjects/Stocks_Revamped/prices/prices.json','w') as pricedata:
        json.dump(prices,pricedata)

def getuserinfo(userid):
    try:
        with open('/Users/adityakannan/PythonProjects/Stocks_Revamped/userdata/'+str(userid)+'.json','r') as userdata:
            user = json.load(userdata)
        return user 
    except Exception:
        return None #return ERROR instead!

def getprices():
    with open('/Users/adityakannan/PythonProjects/Stocks_Revamped/prices/prices.json','r') as pricedata:
        return json.load(pricedata)

def resetuser(userid=None,r_link=None,r_uses=0,r_redeemed=0):
    user = {
        'userid': userid,
        'money': 1000,
        'goods': setgoods("start"),
        'referral': r_link,
        'r_uses': r_uses,
        'r_redeemed': r_redeemed,
    }

    setfileuser(userid,user)

def resetprices():
    prices = {}
    for x in goodslist:
        goodarray = [0]*40
        prices.update({x:goodarray})
        prices[x][0] = random.randint(30,70)

    setfileprices(prices)

async def updateprices(): #market trend algorithm goes here, asynchronous. Need to save previous prices + just do a randomization thing, fix algorithm last
    prices = getprices() #check if zero, update last term
    log = logger("get")

    history = 0 #cycle through the history of all the goods to find length of good history
    while True:
        if history == 39:
            break
        if prices[goodslist[0]][history] == 0:
            break
        history += 1

    goodnum = 0
    #make while loop edit only a single good because right now it's editing basically everything
    while goodnum <= 11:
        #if log[goodslist[goodnum]][1] >= 5: #0 is number of goods, 1 is number of users
        #    userbias = 5
        #else:
        userbias = log[goodslist[goodnum]][1]
        
        #if log[goodslist[goodnum]][0] >= 30:
        #    goodbias = 30
        #elif log[goodslist[goodnum]][0] <= -30:
        #    goodbias = -30
        #else:
        goodbias = log[goodslist[goodnum]][0]

        #print(goodbias*userbias)

        bias = (-((75*np.log(-(goodbias*userbias)+150))/np.log(12.24744872))+150)/150*3

        if history == len(prices[goodslist[goodnum]])-1:
            count = 0
            while count < len(prices[goodslist[goodnum]])-1:
                prices[goodslist[goodnum]][count] = prices[goodslist[goodnum]][count+1]
                count += 1

        previousprice = prices[goodslist[goodnum]][history-1]
        prices[goodslist[goodnum]][history] = previousprice+50*random.uniform(-0.0575+bias,0.0425+bias)
        
        if prices[goodslist[goodnum]][history] >= 100: #check if good hits 100, needs another solution
            prices[goodslist[goodnum]][history] = 99
        goodnum += 1
    setfileprices(prices)
    return history

def displayprices(): #asynchronous because it needs to run periodically while rest of the bot is running
    plt.close()
    fig = plt.figure()
    prices = getprices()

    history = 0
    while True:
        if history == 39:
            break
        if prices[goodslist[0]][history] == 0:
            break
        history += 1

    linestyles = [(0,(5,1)),(0,(1,1)),(0,(1,1)),'solid',(0,(5,1)),(0,(1,1)),(0,(5,1)),(0,(3,1,1,1)),'solid',(0, (3, 10, 1, 10, 1, 10)),(0, (3, 1, 1, 1, 1, 1)),'solid']

    plt.style.use('dark_background')

    count = 0
    for x in prices:
        prices[x].reverse()
        reversehistory = len(prices[x])-history
        last = 1
        if history == len(prices[x])-1: # spoof an extra step at 40 because there are 41 x axis points (0,40) but only 40 data points in price[x]
            reversehistory = len(prices[x])-history-1
            prices[x].append(prices[x][len(prices[x]-1)])
            last = 0
        xaxis = np.arange(reversehistory+last,len(prices[x])+1,1)
        plt.plot(xaxis,prices[x][reversehistory:],linestyle=linestyles[count]) # xaxis 3, reverse 2
        count += 1

    plt.axis([40,0,0,100])
    plt.vlines(range(40, 0, -5), 0, 100, linestyles='dashed', linewidth=0.5,colors='#fff')
    plt.hlines(range(10, 101, 10), 40, 0, linestyles='dashed', linewidth=0.5, colors='#fff')
    plt.ylabel('Price of stock ($)')
    plt.xlabel('Time since last update (min)')
    plt.title('Commodity price index')
    plt.legend(goodslist, bbox_to_anchor=(1.01, 1), borderaxespad=0.0)
    plt.savefig('/Users/adityakannan/PythonProjects/Stocks_Revamped/cache/prices.png',bbox_inches='tight')
    plt.close()
    
    indentedgoods = (
    "gold:        ",
    "silver:      ",
    "oil:         ",
    "platinum:    ",
    "diamond:     ",
    "corn:        ",
    "copper:      ",
    "cotton:      ",
    "sugar:       ",
    "coal:        ",
    "wheat:       ",
    "uranium:     ",
    )
    prices = getprices()
    message = "```autohotkey" + "\nGoods prices\n"
    goodtype = 0
    for x in prices: #make front value bold
        message += "\n" + indentedgoods[goodtype].capitalize()
        
        valuelength = 0
        for y in prices[goodslist[goodtype]]: #checking length of filled historical values
            if y == 0:
                break
            valuelength += 1
        
        count3 = 0
        if valuelength >= 10:
            count3 = valuelength-9
        while count3 < valuelength:
            message += str(int(round(prices[goodslist[goodtype]][count3],0))) #converted to int to remove decimal
            if count3 < valuelength-1: #so that the arrow that is added doesn't point into a null value
                message += " ⟶ "
            count3 += 1
        if valuelength-count3 == 10:
            message += str(int(round(prices[goodslist[goodtype]][count3],0))) #because we don't want a stupid arrow sticking out in the end. 
        if prices[goodslist[goodtype]][count3-2] > prices[goodslist[goodtype]][count3-1]:
            message += " ⇣ "
        elif prices[goodslist[goodtype]][count3-2] < prices[goodslist[goodtype]][count3-1]:
            message += " ⇡ "
        else:
            message += " ● "
        goodtype += 1    
    message += "```"
    return message

def setgoods(type,inventory=None,order=None,amount=None):
    if type == "start":
        inventory = {}
        for x in goodslist:
            inventory.update({x:0})

    if type == "buy":
        inventory[order] += int(amount)

    if type == "sell":
        inventory[order] -= int(amount)

    return inventory

def canafford(money,order,amount): #returns True/False + money required in the form of a list. Also, make sure that "amount" is an int and try/except to check if good exists
    prices = getprices()
    count = -1 #because 1 is being added by default
    for x in prices[order]:
        if x == 0:
            break
        count += 1
    
    if amount == "all":
        amount = int(money/prices[order][count])
        cost = int(prices[order][count])
    else:
        cost = int(amount)*int(prices[order][count])

    if cost < money and cost != 0:
        purchasedetails = [cost,True,amount]
    else:
        purchasedetails = [cost,False]

    return purchasedetails

def cansell(inventory,order,amount): #returns T/F and how much money made
    prices = getprices()
    count = -1
    for x in prices[order]:
        if x == 0:
            break
        count += 1

    if amount == "all":
        if inventory[order] != 0:
            amount = inventory[order]
        else:
            amount = 0

    earning = int(amount)*prices[order][count]

    if int(amount) <= inventory[order] and amount != 0:
        selldetails = [earning,True,amount]
    else:
        selldetails = [earning,False]

    return selldetails

def logger(type,good=None,amount=None): #need good-specific logs, make new function or get this to encompass everything to retrieve and send logdata 
    if amount != None:
        amount = int(amount)
    
    with open('/Users/adityakannan/PythonProjects/Stocks_Revamped/cache/activitylog.json','r') as logjson:
        logdata = json.load(logjson)

    if type == "get":
        return logdata

    if type == "reset":
        logdata = {}
        for x in goodslist:
            logdata.update({x:[0,0]}) # [0] total amount bought/sold, [1] for number of buyers/sellers
    
    if type == "buy":
        logdata[good][0] += amount
        logdata[good][1] += 1

    if type == "sell":
        logdata[good][0] -= amount
        logdata[good][1] -= 1

    with open('/Users/adityakannan/PythonProjects/Stocks_Revamped/cache/activitylog.json','w') as logjson:
        json.dump(logdata,logjson)

def getcost(type,amount=None): #implementation with goods prices. Is this really necessary? Might be needed for .totalvalue
    pass

def userlist(type,userid=None):
    with open('/Users/adityakannan/PythonProjects/Stocks_Revamped/cache/userlist.json','r') as idlist:
        userlist = json.load(idlist)

    if type == "join":
        userlist.append(userid)
    if type == "leave":
        userlist.remove(userid)
    if type == "get":
        return userlist

    with open('/Users/adityakannan/PythonProjects/Stocks_Revamped/cache/userlist.json','w') as idlist:
        json.dump(userlist,idlist)

def leaderboardupdate():
    lister = userlist("get")
    leaderboard = {}
    for i in lister:
        with open('/Users/adityakannan/PythonProjects/Stocks_revamped/userdata/' + str(i) + '.json','r') as userdata:
            user = json.load(userdata)
        leaderboard.update({user["money"]:i})

    leaderboard = sorted(leaderboard.items(),reverse=True)

    return leaderboard

@bot.event
async def on_ready(): #needs to *start* with asyncio(time) because the prices are randomized when the script begins
    #await bot.change_presence(activity=discord.Game(name='(.help)'))

    resetprices()
    logger("reset")

    print('Stockbroker is ready.')

    logcount = 0
    while True:
        message = displayprices()
        channel = bot.get_channel(697800679569358968)
        await channel.purge(limit=2)
        await channel.send(message)
        await channel.send(file=File('/Users/adityakannan/PythonProjects/Stocks_Revamped/cache/prices.png'))

        logcount += 1
        if logcount == 3:
            logger("reset")
            logcount = 0

        count = 60
        while count>0:
            await bot.change_presence(activity=discord.Game(name='.help | Time for reiteration: < ' + str(count) + ' seconds'))
            await asyncio.sleep(15)
            count -= 15
        await updateprices()

@bot.command() #Ping
async def ping(ctx):
    await ctx.send(f'Pong! The latency is **{round(bot.latency*1000)}ms**')

#@bot.event
#async def on_message(message):
#    await bot.process_commands(message)

@bot.command()
@commands.is_owner()
async def postupdates(ctx):
    await ctx.channel.purge(limit=1)
    channel = bot.get_channel(697416757488648243)
    await channel.send("@everyone Update #2: Front end for .buy and .profile is ready, but there currently is no method of earning money. **If you were a member of this bot before update #1, you need to type .reset to register yourself with the bot**. If you noticed, the channel #price-index was recently created - it's where everyone can check goods prices, etc. On a different note, I'm considering adding this new featur where you can create and invest in a businesses to grow it and recieve periodic payouts, etc., but this is something I'll be shelfing for the near future at least. More updates coming soon.")

@bot.event
async def on_member_join(member): #direct them to rules or #verification or whatever
    channel = bot.get_channel(696825250033434634)
    userid = member.id

    if getuserinfo(userid) == None:
        resetuser(userid)
        await channel.send("Welcome to Stock Exchange, <@"+str(userid)+">! You have been automatically been registered.")
    else:
        await channel.send("Welcome to Stock Exchange, <@"+str(userid)+">! Your data has been recovered.")
    userlist("join",userid)

@bot.event
async def on_member_remove(member):
    userid = member.id
    userlist("leave",userid)

@bot.command()
async def reset(ctx,*,member: discord.Member = None): #add user as an argument so ONLY admins can reset, figure out roles, add referrals, lottos, etc.
    if member == None:
        userid = ctx.author.id
    else:
        if ctx.author.id == 305784264140652554:
            userid = member.id
        else:
            await ctx.send("You don't have the permissions to do this.")

    resetuser(userid)

    await ctx.send('(Re)registered successfully.')

@bot.command()
@commands.is_owner()
async def resetmarket(ctx): #prices
    resetprices()

@bot.command()
async def profile(ctx,*,member: discord.Member = None):
    if member == None:
        userid = ctx.author.id
        nick = ctx.author.nick
        name = ctx.author.name
    else:
        userid = member.id
        nick = member.nick
        name = member.name        

    user = getuserinfo(userid)

    if user != None:
        if str(nick) == 'None':
            displayname = str(name)
        else:
            displayname = str(ctx.author.nick)

        embed=discord.Embed(title=displayname+"'s profile")
        
        embed.add_field(name="**Money**", value=int(round(user["money"],0)), inline=False)
        
        embed.add_field(name="Gold", value=user["goods"]["gold"], inline=True)
        embed.add_field(name="Silver", value=user["goods"]["silver"], inline=True)
        embed.add_field(name="Oil", value=user["goods"]["oil"], inline=True)
        embed.add_field(name="Platinum", value=user["goods"]["platinum"], inline=True)
        embed.add_field(name="Diamond", value=user["goods"]["platinum"], inline=True)
        embed.add_field(name="Corn", value=user["goods"]["corn"], inline=True)
        embed.add_field(name="Copper", value=user["goods"]["copper"], inline=True)
        embed.add_field(name="Cotton", value=user["goods"]["cotton"], inline=True)
        embed.add_field(name="Sugar", value=user["goods"]["sugar"], inline=True)
        embed.add_field(name="Coal", value=user["goods"]["coal"], inline=True)
        embed.add_field(name="Wheat", value=user["goods"]["wheat"], inline=True)
        embed.add_field(name="Uranium", value=user["goods"]["uranium"], inline=True)
        embed.set_footer(text="Stockbroker")
        await ctx.send(embed=embed)
    else:
        await ctx.send('Error, you are not registered. Please type ``.reset`` to register.')

@bot.command()
@commands.is_owner()
async def credit(ctx,member: discord.Member,amount):
    userid = member.id
    user = getuserinfo(userid)
    user["money"] = user["money"]+int(amount)

    # ADD dictionary appending, etc. for logging. Long term proj.
    # with open('/Users/adityakannan/PythonProjects/Stocks_Revamped/userdata/creditlog.json','r') as creditlog:
    #    json.load(creditlog)
    
    # with open('/Users/adityakannan/PythonProjects/Stocks_Revamped/userdata/creditlog.json','w') as creditlog:
    #    json.dump(creditlog,log) 

    setfileuser(userid,user)

    await ctx.send("Credited " + member.name + " " + amount + "$ and logged.")

@bot.command()
async def buy(ctx,order,amount):
    userid = ctx.author.id
    try:
        user = getuserinfo(userid)
    except: #make this a function
        await ctx.send('Error, you are not registered. Please type ``.reset`` to register')

    purchasedetails = canafford(user["money"],order,amount)
    
    if amount == "all":
        if purchasedetails[1] is True:
            amount = purchasedetails[2]
        else:
            amount = 0

    amount = int(amount) #for sales too

    if purchasedetails[1] is True:
        user["money"] = user["money"] - purchasedetails[0]
        user["goods"] = setgoods("buy",user["goods"],order,amount) #changed from 'inventory' to 'user["goods"]'
        logger("buy",order,amount)
        await ctx.send("Purchased **" + str(amount) + " " + order + "** and paid " + str(int(purchasedetails[0])) + "$")
    else:
        await ctx.send("Transaction failed. You need " + str(int(purchasedetails[0] - user["money"])) + "$ more.")

    setfileuser(userid,user)

@bot.command()
async def sell(ctx,order,amount=None):
    userid = ctx.author.id
    user = getuserinfo(userid)

    if order == "all":
        ownedgoods = []
        totalearning = 0
        for x in user["goods"]:
            if user["goods"][x] != 0:
                ownedgoods.append(x)
        for x in ownedgoods:
            selldetails = cansell(user["goods"],x,"all")
            user["goods"] = setgoods("sell",user["goods"],x,selldetails[2])
            totalearning += selldetails[0]
        user["money"] += totalearning
        if totalearning != 0:
            await ctx.send("Sold all of your goods and earned " + str(int(totalearning)) + "$")
        else:
            await ctx.send("Transaction failed. You don't currently own any goods.")
    else:
        selldetails = cansell(user["goods"],order,amount) #to check if they have enough goods

        if amount == "all":
            if selldetails[1] is True:
                amount = selldetails[2]
            else:
                amount = 0

        if selldetails[1] is True:
            user["money"] += selldetails[0]
            user["goods"] = setgoods("sell",user["goods"],order,amount)
            logger("sell",order,amount)
            await ctx.send("Sold **" + str(amount) + " " + str(order) + "** and earned " + str(int(selldetails[0])) + "$")
        elif user["goods"][order] == 0:
            await ctx.send("Transaction failed. You don't own any " + str(order) + ".")
        else:
            await ctx.send("Transaction failed. You need " + str(int(amount) - user["goods"][order]) + " more " + str(order) + ".")

    try:
        setfileuser(userid,user)
    except: #make this a function
        await ctx.send('Error, you are not registered. Please type ``.reset`` to register')

@bot.command()
async def referral(ctx,type=None):
    userid = ctx.author.id
    user = getuserinfo(userid)
    userobject = bot.get_user(userid)

    if type == "None":
        pass
    if type == "create":
        channel = bot.get_channel(696825250033434634)
        link = await channel.create_invite(max_uses = 5)
        invitelinkexists = 0
        try:
            if user["r_link"] == None:
                user["r_link"] = link.url
                user["r_uses"] = 0
                user["r_redeemed"] = 0
            else:
                await ctx.send("You already have an active referral link. Type ``.referral check`` to see more details on it.")
                invitelinkexists = 1
        except:
            user.update({"r_link":link.url})
            user.update({"r_uses":0})
            user.update({"r_redeemed":0})

        if invitelinkexists != 1:
            setfileuser(userid,user)
            await ctx.send("Your referral link is generated successfully and has been sent to you privately.")
            await userobject.send("Here's your referral link: " + link.url + ". \n \n This referral link can be used for a maximum of 5 times. \n If you want more details on your referrals, type ``.referral check`` anywhere on the server.")

    if type == "check":
        guild = ctx.guild

        invitemeta = await guild.invites()
        for invite in invitemeta:
            if invite.url == user["r_link"]:
                break

        user["r_uses"] = invite.uses
        
        embed=discord.Embed(title="Referral details", url="https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        embed.add_field(name="Your referral link", value=invite.url, inline=True)
        embed.add_field(name="Total users referred", value=invite.uses, inline=False)
        embed.add_field(name="Total rewards redeemed", value=user["r_redeemed"],inline=False)
        embed.add_field(name="Number of remaining referrals", value=5-invite.uses, inline=False)
        embed.set_footer(text="Stockbroker")

        await ctx.send("Your referral details have been sent to you privately.")
        await userobject.send(embed=embed)

    if type == "redeem":
        user = getuserinfo(ctx.author.id)
        channel = ctx.channel
        guild = ctx.guild

        invitemeta = await guild.invites()
        for invite in invitemeta:
            if invite.url == user["r_link"]:
                break
        user["r_uses"] = invite.uses
        reward = user["r_uses"]-user["r_redeemed"]
        
        def check(m):
            return m.content in ['yes','exit'] and m.channel == channel and ctx.author.id == user["userid"]
        def check2(m):
            return m.channel == channel and ctx.author.id == user["userid"]

        s = ""
        if reward != 1:
            s = "s"
        await channel.send(str(user["r_uses"]) + ' out of 5 people have used your referral link, and you have **' + str(reward) + '** new reward' + s + ' to redeem.')
        if (user["r_uses"]-user["r_redeemed"]) > 0:
            await ctx.send('If you want to redeem them now, type ``yes``. If not, ``exit``.')
            try:
                response = await bot.wait_for('message', check=check, timeout = 30.0)
                response = response.content.lower()
            except asyncio.TimeoutError:
                await ctx.send('You did not respond in 30 seconds')
            if response == "yes":
                await ctx.send('Your reward is **' + str(100*reward) + '** goods of your choice! Type the name of the good you want to redeem. Type ``exit`` to exit.')
                try:
                    response2 = await bot.wait_for('message',check=check2, timeout = 30.0)
                    response2 = response2.content.lower()
                except asyncio.TimeoutError:
                    await ctx.send('You did not respond in 30 seconds')
                nogood = 0
                if response2 != 'exit':
                    for x in goodslist:
                        if x == response2:
                            user["goods"] = setgoods("buy",user["goods"],response2,(100*reward))
                            user["r_redeemed"] += reward
                            await ctx.send(str("**"+ (100*reward) + " " + response2 + "** was credited to your account successfully."))
                            nogood = 1
                            break
                    if nogood != 1:
                        await ctx.send("Invalid response. Type ``.referral redeem`` to try again.")
                elif response2 == 'exit':
                    await ctx.send(':thumbsup: Your rewards are still available for redeeming.')
            elif response == 'exit':
                await ctx.send(':thumbsup: Your rewards are still available for redeeming.')
            setfileuser(ctx.author.id,user)
        # await user.send('ey')
    # 'check', 'create', 'redeem' more the users invited, more the reward (like FoE's tavern house)

@bot.command()
@commands.is_owner()
async def test(ctx):
    await updateprices()

@bot.command()
@commands.is_owner()
async def test2(ctx):
    channel = bot.get_channel(697800679569358968)
    await channel.purge(limit=2)

    message = displayprices()
    channel = bot.get_channel(697800679569358968)
    await channel.send(message)
    await channel.send(file=File('/Users/adityakannan/PythonProjects/Stocks_Revamped/cache/prices.png'))

@bot.command()
@commands.is_owner()
async def l_update(ctx):
    leaderboard = leaderboardupdate()
    
    message = "```autohotkey" + "\nLeaderboard\n\n"
    count = 0
    for x in leaderboard:
        user = bot.get_user(leaderboard[count][1])
        message += '(' + str(count+1) + ') ' + user.name + ': ' + str(int(leaderboard[count][0])) + '\n'
        count += 1
    
    message += "```"
    
    channel = bot.get_channel(704978980666867763)
    await channel.send(message)

@bot.command()
@commands.is_owner()
async def parrot(ctx,message):
    await ctx.channel.purge(limit=1)
    await ctx.send(message)

@bot.event
async def on_command_error(context, error):
    if type(error) == discord.ext.commands.CommandNotFound:
        await context.message.channel.send('Command does not exist, use ``.help`` to see the list of commands')

@bot.command()
@commands.is_owner()
async def shutdown(ctx):
    print ('Stockbroker is shutting down.')
    await ctx.bot.logout()

bot.run(key)