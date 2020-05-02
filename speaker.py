import discord
import time
import logging
import random
import asyncio
import requests
import os
import xml.etree.ElementTree as ET

logging.basicConfig(level=logging.INFO)

TOKEN = ""
nation = ""
userAgent = ""
autoLogin = ""
client = discord.Client()

nsChannelName = "bot-shenanigans"
nsIssues = []

### Actual bot programming ###
@client.event
async def on_ready():
    print("--<O>--")
    print("Logged in as {}".format(client.user.name))
    print(client.user.id)
    print("--<O>--")
    nsChannel = discord.utils.get(client.get_all_channels(), name=nsChannelName)
    await botGetIssues(nation, userAgent, autoLogin)
    e = discord.Embed(title="test.issue.title")
    await botCreateVote(nsChannel, "test", 24, 4, e)

@client.event
async def on_message(message):
    if discord.utils.get(message.channel.guild.roles, name="botMaster") in message.author.roles:
        print("Valid")
        #await botPrintIssues(nsChannel)
        return
    else:
        print("invalid")
        return

### Supplemental bot methods ###
async def botRepeatIssuePrint(channel, time):
    await botPrintIssues(channel)
    await asyncio.sleep(time)
    await repeatCheck(channel, time)

async def botGetIssues(nation, userAgent, autoLogin):
    global nsIssues
    nsIssues = parseIssues(getIssues(nation, userAgent, autoLogin))

async def botPrintIssues(channel):
    global nsIssues
    colors = ["teal", "green", "blue", "purple", "magenta", "gold", "orange", "red"]
    for issue in nsIssues:
        issue.applyFormatting()
        colorNum = random.randint(0, len(colors)-1)
        event = discord.Embed(title=issue.title, description=issue.text, colour=getColor(colors[colorNum])[0]).set_footer(text=issue.id)
        print("Issue id {}".format(issue.id))
        await channel.send(embed=event)
        for option in issue.options:
            opt = discord.Embed(title="{0} - Option {1}".format(issue.title, issue.options.index(option)+1), description=option, colour=getColor(colors[colorNum])[1])
            await channel.send(embed=opt)
        del colors[colorNum]
    return

async def botCreateVote(channel, topic, hours, options, embed): #takes time in hours, options int up to 10
    footer = embed.footer.text
    embed.set_footer(text="{0} - This vote will last until {1}".format(footer, time.strftime("%a, %H:%M", time.localtime(time.time()+hours*3600))))
    msg = await channel.send(embed=embed)
    print(msg)
    for i in range(0,options+1):
        if i == 0:
            await msg.add_reaction("❌")
        elif i == 1:
            await msg.add_reaction("1️⃣")
        elif i == 2:
            await msg.add_reaction("2️⃣")
        elif i == 3:
            await msg.add_reaction("3️⃣")
        elif i == 4:
            await msg.add_reaction("4️⃣")
        elif i == 5:
            await msg.add_reaction("5️⃣")
        elif i == 6:
            await msg.add_reaction("6️⃣")
        elif i == 7:
            await msg.add_reaction("7️⃣")
        elif i == 8:
            await msg.add_reaction("8️⃣")
        elif i == 9:
            await msg.add_reaction("9️⃣")
        elif i == 10:
            await msg.add_reaction("🔟")
        else:
            print("Invalid option")
    await asyncio.sleep(hours*1)
###USE WAIT_FOR

def loadSecrets():
	cwd = os.getcwd()
	secrets = open("secrets.txt", "r").read().split("\n")
	return secrets

def getColor(color):
    if color=="teal":
        return (discord.Colour.teal(), discord.Colour.dark_teal())
    elif color=="green":
        return (discord.Colour.green(), discord.Colour.dark_green())
    elif color=="blue":
        return (discord.Colour.blue(), discord.Colour.dark_blue())
    elif color=="purple":
        return (discord.Colour.purple(), discord.Colour.dark_purple())
    elif color=="magenta":
        return (discord.Colour.magenta(), discord.Colour.dark_magenta())
    elif color=="gold":
        return (discord.Colour.gold(), discord.Colour.dark_gold())
    elif color=="orange":
        return (discord.Colour.orange(), discord.Colour.dark_orange())
    elif color=="red":
        return (discord.Colour.red(), discord.Colour.dark_red())

### Nationstates API methods ###
def getIssues(nation, userAgent, autoLogin): # Returns XML tree of the NS issues from this acct
    url = "https://www.nationstates.net/cgi-bin/api.cgi?nation="+nation+"&q=issues" #TODO: Put the nation and issues headers in the bloody headers thing
    headers = {
        'user-agent' : userAgent,
        'X-autologin' : autoLogin,
    }
    r = requests.get(url, headers=headers)
    return r.text

def parseIssues(xmlText): # Returns a list of issue objects
    root = ET.fromstring(xmlText)
    iss = []
    issues = []
    for child in root[0]:
        iss.append(child)
    for opt in iss:
        title = opt.find("TITLE").text
        num = opt.attrib["id"]
        text = opt.find("TEXT").text
        options = []
        for option in opt.findall("OPTION"):
            options.append(option.text)
        issues.append(issue(title, num, text, options))
    return issues 
            
class issue():
    def __init__(self, title, num, text, options):
        self.title = title
        self.id = num
        self.text = text
        self.options = options

    def printOptions(self):
        for option in self.options:
            print("Option " + str(self.options.index(option)+1) + ":\n" + option)

    def printIssue(self):
        print(self.title)
        print(self.text)
        self.printOptions()

    def respond(nation, userAgent, autoLogin, self, option):
        url = "https://www.nationstates.net/cgi-bin/api.cgi?"
        print(url)
        headers = {
            'X-autologin' : autoLogin,
            'user-agent' : userAgent,
        }
        data = {
            "nation" : nation,
            "c" : "issue",
            "issue" : str(self.id),
            "option" : str(option-1)
        }
        r = requests.post(url, headers=headers, data=data) #TODO get the return values
        print(r.text)

    def applyFormatting(self):
        words = self.text.split()
        newText = ""
        for word in words:
            if "<i>" in word or "</i>" in word:
                print(word)
                word = word.replace("<i>","*")
                word = word.replace("</i>","*")
                print(word)
            newText+=" " + word
        self.text = newText
        newOptions = []
        for option in self.options:
            opWords = option.split()
            newOp = ""
            for word in opWords:
                if "<i>" in word or "</i>" in word:
                    print(word)
                    word = word.replace("<i>","*")
                    word = word.replace("</i>","*")
                    print(word)
                newOp+= " " + word
            option = newOp
            newOptions.append(option)
        self.options = newOptions

secrets = loadSecrets()
TOKEN = secrets[0]
nation = secrets[1]
userAgent = secrets[2]
autoLogin = secrets[3]
client.run(TOKEN)
