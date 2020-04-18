import discord
from discord import File
from discord.ext import commands

import time
import asyncio
import json
import random
import matplotlib.pyplot as plt
import numpy as np

# IDEAS:
# add 1% multiplier or increased starting bank account with referrals
# types of goods: gold, silver, oil, platinum
# add a bias for some stocks so the prices remain higher. There needs to be a sense of scale, for ex. diamonds can't cost lesser than wheat, etc.
# realistic exchange rate, for ex. diamonds = 1000 wheat
# rand generator for stock prediction needs to depend on market demand
# banks with interest
# implied volatility
# limits for artificial inflation
# make it extensibile and modular
# relegate stuff to functions
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
# program .sell and .sellall
# centralize goodlist list

# LONGTERM TODOLIST:
# need a bot and server pfp, cash award for dude who makes it
# async with channel.typing():
# do expensive stuff here
# await channel.send('done!')

bot = commands.Bot(command_prefix = '.')

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

def resetuser(userid=None):
    user = {
        'userid': userid,
        'money': 1000,
        'goods': setgoods("start")
    }

    setfileuser(userid,user)

def resetprices():
    prices = {}
    for x in goodslist:
        goodarray = [0]*40
        prices.update({x:goodarray})
        prices[x][0] = random.randint(11,99)

    setfileprices(prices)

async def updateprices(): #market trend algorithm goes here, asynchronous. Need to save previous prices + just do a randomization thing, fix algorithm last
    prices = getprices() #check if zero, update last term
    log = log("get")

    history = 0 #cycle through the history of all the goods to find length of good history
    while True:
        if prices[goodslist[0]][history] == 0:
            break
        history += 1

    goodnum = 0 #only cycle through all the names of goods

    #make while loop edit only a single good because right now it's editing basically everything
    while goodnum <= 11:
        bias: 0
        previousprice = prices[goodslist[goodnum]][history-1]
        prices[goodslist[goodnum]][history] = previousprice*(1+random.uniform(-0.0575+bias,0.0425+bias))
        goodnum += 1
        setfileprices(prices)

def displayprices(): #asynchronous because it needs to run periodically while rest of the bot is running
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
            if valuelength == 9: #because only 10 values should be displayed in that message
                break
        count3 = 0
        while count3 < valuelength:
            message += str(int(round(prices[goodslist[goodtype]][count3],0))) #converted to int to remove decimal
            if count3 < valuelength-1: #so that the arrow that is added doesn't point into a null value
                message += " ⟶ "
            count3 += 1
        if valuelength == 10:
            message += str(int(round(prices[goodslist[goodtype]][count3],0))) #because we don't want a stupid arrow sticking out in the end. 
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

    cost = int(amount)*prices[order][count]

    if cost < money:
        purchasedetails = [cost,True]
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
    
    earning = int(amount)*prices[order][count]

    if int(amount) <= inventory[order]:
        selldetails = [earning,True]
    else:
        selldetails = [earning,False]

    return selldetails

def log(type,good=None,amount=None): #need good-specific logs, make new function or get this to encompass everything to retrieve and send logdata 
    amount = int(amount)
    with open('/Users/adityakannan/PythonProjects/Stocks_Revamped/cache/activitylog.json','r') as logdata:
        log = json.load(logdata)

    if type == "get":
        return log

    if type == "reset":
        log = {}
        for x in goodslist:
            log.update({x:[0,0,0,0]}) # [0] amount bought, [1] for number of buyers, [2] amount sold, [3] for number of sellers
    
    if type == "buy":
        log[good][0] += amount
        log[good][1] += 1

    if type == "sell":
        log[good][2] += amount
        log[good][3] += 1

    with open('/Users/adityakannan/PythonProjects/Stocks_Revamped/cache/activitylog.json','w') as logdata:
        json.dump(log,logdata)

def getcost(type,amount=None): #implementation with goods prices. Is this really necessary? Might be needed for .totalvalue
    pass

@bot.command() #Ping
async def ping(ctx):
    await ctx.send(f'Pong! The latency is **{round(bot.latency*1000)}ms**')

@bot.event
async def on_ready(): #needs to *start* with asyncio(time) because the prices are randomized when the script begins
    await bot.change_presence(activity=discord.Game(name='(.help)'))
    
    resetprices()
    log("reset")

    print('Stockbroker is ready.')
    #while True:
    #    await asyncio.sleep(20)
    #    await updateprices()

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
        await channel.send("Welcome to Stock Exchange, @"+str(member.name)+" ("+str(userid)+")! You have been automatically been registered.")
    else:
        await channel.send("Welcome to Stock Exchange, <@"+str(userid)+">! Your data has been recovered.")

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

    if str(nick) == 'None':
        displayname = str(name)
    else:
        displayname = str(ctx.author.nick)

    embed=discord.Embed(title=displayname+"'s profile")
    
    embed.add_field(name="**Money**", value=user["money"], inline=False)
    
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
    embed.set_footer(text="Stockbroker Revamped")
    await ctx.send(embed=embed)

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

    if purchasedetails[1] is True:
        user["money"] = user["money"] - purchasedetails[0]
        user["goods"] = setgoods("buy",user["goods"],order,amount) #changed from 'inventory' to 'user["goods"]'
        log("buy",order,amount)
        await ctx.send("Purchased **" + str(amount) + " " + order + "** and paid " + str(purchasedetails[0]) + "$")
    else:
        await ctx.send("Transaction failed. You need " + str((purchasedetails[0] - user["money"])) + "$ more.")

@bot.command()
async def sell(ctx,order,amount):
    userid = ctx.author.id
    user = getuserinfo(userid)
    
    selldetails = cansell(user["goods"],order,amount) #to check if they have enough goods

    if selldetails[1] is True:
        user["money"] = user["money"] + selldetails[0]
        user["goods"] = setgoods("sell",user["goods"],order,amount)
        log("sell",order,amount)
        await ctx.send("Sold **" + str(amount) + " " + str(order) + "** and earned " + str(selldetails[0]) + "$")
    else:
        await ctx.send("Transaction failed. You need " + str(int(amount) - user["goods"][order]) + " more " + str(order))

    try:
        setfileuser(userid,user)
    except: #make this a function
        await ctx.send('Error, you are not registered. Please type ``.reset`` to register')

@bot.command()
@commands.is_owner()
async def test(ctx):
    await updateprices()

@bot.command()
@commands.is_owner()
async def test2(ctx):
    channel = bot.get_channel(697800679569358968)
    await channel.purge(limit=2)

    plt.close()
    fig = plt.figure()
    xaxis = np.arange(0,40,1)
    prices = getprices()

    plt.style.use('dark_background')
    for x in prices:
        plt.plot(xaxis,prices[x])
    plt.axis([40,0,0,100])
    plt.vlines(range(40, 0, -5), 0, 100, linestyles='dashed', linewidth=0.5,colors='#fff')
    plt.hlines(range(10, 101, 10), 40, 0, linestyles='dashed', linewidth=0.5, colors='#fff')
    plt.ylabel('Price of stock ($)')
    plt.xlabel('Time since last update (min)')
    plt.title('Commodity price index')
    plt.savefig('/Users/adityakannan/PythonProjects/Stocks_Revamped/cache/prices.png')
    plt.close()


    message = displayprices()
    channel = bot.get_channel(697800679569358968)
    await channel.send(message)
    await channel.send(file=File('/Users/adityakannan/PythonProjects/Stocks_Revamped/cache/prices.png'))

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

bot.run('Njk2MzM2NDg5OTc3NjEwMjQw.XonSQA.gcDAZmowaenwgvkWGafZ_RgkjTg')