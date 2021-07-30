import discord
from discord.ext import commands, tasks
from PIL import Image, ImageDraw, ImageFilter
import asyncio
import requests
from discord.ext.commands import MissingRequiredArgument

#Initialisation
client = commands.Bot(command_prefix = '.',intents = discord.Intents.all())
client.remove_command('help')

#Global Vars
messageList = []
rank_emojis = ['🟥','🟧','🟨','🟩','🟦']
User = client
toggle_id = int
avatarImages = []
RankGrid = [[],[],[],[],[]]

@client.event
async def on_ready():
  print('utility bot is ready')

#GENERATE TIERLIST
@client.command()
async def tierlist(ctx):
  cmd = client.get_command('tierlist')
  cmd.enabled = False

  global messageList
  global rank_emojis
  global User
  User = ctx.author
  global toggle_id
  global tirelistTitle

  #Embed Set Up
  embed = discord.Embed(color = discord.Color.dark_blue())

    #Title
  await ctx.send("react to rank!")

    #Body
  for member in ctx.message.guild.members:
    embed.set_author(name=member,icon_url='{}'.format(member.avatar_url))

    body = await ctx.send(embed=embed)
    for emoji in rank_emojis:
      await body.add_reaction(emoji)
    await body.add_reaction('🗑️')

    messageList.append(body.id)

    #Footer
  footer = await ctx.send('Produce tierlist?')
  await footer.add_reaction('✅')
  await footer.add_reaction('❌')

  toggle_id = footer.id


async def updateReaction():
    while True:
      #Variables
      global messageList
      global User
      global toggle_id

      #Methods
      await TrashCollector(messageList, User)

      if toggle_id != int:
        toggle_message = discord.utils.get(client.cached_messages, id=toggle_id)
        await Toggle(toggle_message)

      await asyncio.sleep(1)

async def Toggle(message):
  global toggle_id
  global messageList
  global avatarImages
  global RankGrid

  for reaction in message.reactions:
      users = await reaction.users().flatten()
      for user in users:
        if user == User:
          if reaction.emoji == '✅':

            #Embeds
            confirmEmbed = discord.Embed(title = 'Generating Tierlist:',description = 'Confirming...',color = discord.Color.dark_blue())
            msg = await message.channel.send(embed = confirmEmbed)

            trashEmbed = discord.Embed(title = 'Generating Tierlist:',description = 'Collecting Trash...',color = discord.Color.dark_blue())
            
            rankEmbed = discord.Embed(title = 'Generating Tierlist:',description = 'Cleaning Ranks...',color = discord.Color.dark_blue())

            gridEmbed = discord.Embed(title = 'Generating Tierlist:',description = 'Reading Input...',color = discord.Color.dark_blue())

            iconEmbed = discord.Embed(title = 'Generating Tierlist:',description = 'Retrieving Avatars...',color = discord.Color.dark_blue())

            generateEmbed = discord.Embed(title = 'Generating Tierlist:',description = 'Generating Image...',color = discord.Color.dark_blue())

            finishEmbed = discord.Embed(title = 'Tierlist Generated!',color = discord.Color.dark_blue())

            errorEmbed = discord.Embed(title = 'Error:',description = 'Tierlist template is not big enough! Tierlist Generator has reset',color = discord.Color.dark_blue())
            
            #Methods
            for reaction2 in message.reactions:
              if reaction2.emoji == "❌":
                users = await reaction2.users().flatten()
                for user in users:
                  await reaction2.remove(user) 

            await msg.edit(embed = trashEmbed)
            await TrashCollector(messageList,User)

            await msg.edit(embed = rankEmbed)
            await RankCleaner()

            await msg.edit(embed = gridEmbed)
            await GenerateRankGrid()

            global RankGrid
            for row in RankGrid:
              if len(row)>9:
                toggle_id = int
                messageList = []
                avatarImages = []
                tirelistTitle = str
                RankGrid = [[],[],[],[],[]]
                cmd = client.get_command('tierlist')
                cmd.enabled = True
                await msg.edit(embed = errorEmbed)
                return
                
            await msg.edit(embed = iconEmbed)
            await GenerateMessageListIcons()

            await msg.edit(embed = generateEmbed)
            await tierlistGenerate(message.channel)

            toggle_id = int
            messageList = []
            avatarImages = []
            tirelistTitle = str
            RankGrid = [[],[],[],[],[]]
            cmd = client.get_command('tierlist')
            cmd.enabled = True

            await msg.edit(embed = finishEmbed)
            

          elif reaction.emoji == '❌':
            #Embeds
            confirmEmbed = discord.Embed(title = 'Confirming...',color = discord.Color.dark_blue())
            msg = await message.channel.send(embed = confirmEmbed)

            sucessEmbed = discord.Embed(title = 'Tierlist Canceled!',color = discord.Color.dark_blue())

            #Methods
            for reaction2 in message.reactions:
              if reaction2.emoji == "✅":
                users = await reaction2.users().flatten()
                for user in users:
                  await reaction2.remove(user) 

            toggle_id = int
            messageList = []
            avatarImages = []
            tirelistTitle = str
            RankGrid = [[],[],[],[],[]]
            cmd = client.get_command('tierlist')
            cmd.enabled = True

            await msg.edit(embed = sucessEmbed)

async def RankCleaner():
  global rank_emojis
  global User
  global messageList

  if messageList != []:
    for id in messageList:
      cache_msg = discord.utils.get(client.cached_messages, id=id)

      reactionCount = 0

      for reaction in cache_msg.reactions:
        users = await reaction.users().flatten()
        for user in users:
          if user == User:
            if reaction.emoji in rank_emojis:
              reactionCount += 1

            if reactionCount > 1:
              await reaction.remove(User)

async def TrashCollector(messageList, User):
  if messageList != []:
    for id in messageList:
      cache_msg = discord.utils.get(client.cached_messages, id=id)
      for reaction in cache_msg.reactions:
        users = await reaction.users().flatten()
        for user in users:
          if user == User:
            if reaction.emoji == '🗑️':
              await cache_msg.delete()
              messageList.remove(id)

async def GenerateMessageListIcons():
  global messageList
  global avatarImages

  avatarImages = []

  for id in messageList:
    cache_msg = discord.utils.get(client.cached_messages, id=id)
    url = cache_msg.embeds[0].author.icon_url
    Img = Image.open(requests.get(url, stream=True).raw)
    avatarImages.append(Img)

async def GenerateRankGrid():
  global rank_emojis
  global User
  global messageList
  global RankGrid

  for id in messageList:
    cache_msg = discord.utils.get(client.cached_messages, id=id)

    for reaction in cache_msg.reactions:
      users = await reaction.users().flatten()
      for user in users:
        if user == User:
          if reaction.emoji in rank_emojis:
            RankGrid[rank_emojis.index(reaction.emoji)].append(messageList.index(id))


#TIRELIST TRANSFORM AND STRETCH
async def tierlistGenerate(channel):
  template = Image.open('tierlist.png')
  global toggle_id
  global messageList
  global avatarImages
  global tirelistTitle
  global RankGrid

  #Interface Parameters
  borderPercent = 13
  xoffsetPercet = 12
  rowCount = 5
  collumnCount = 9  

  #Derived Parameters
  w,h = template.size
  cellSize = h/rowCount
  borderSize = cellSize * borderPercent / 100
  xoffsetSize = w * xoffsetPercet/100
  cellStretch = int(cellSize - 2 * borderSize)

  rowPos = [0] * rowCount
  for i in range(0,rowCount):
    rowPos[i] = int (i * cellSize + borderSize)

  collumnPos = [0] * collumnCount
  for i in range(0,collumnCount):
    collumnPos[i] = int (i * cellSize + borderSize + xoffsetSize)

  #Apply Paste
  #i = rank, j = icon position index
  for i in range(0,len(RankGrid)):
    for j in range(0,len(RankGrid[i])):
        index = RankGrid[i][j]
        icon = avatarImages[index]
        template.paste(icon.resize((cellStretch,cellStretch)),(collumnPos[j],rowPos[i]))

    #Save + Embed
    template.save("newTierlist.png")
    file = discord.File("newTierlist.png",filename="newTierlist.png")
    await channel.send(file=file)



#Simple Text Commands
@client.command()
async def hi(ctx):
  await ctx.send('good day')

@client.command()
async def help(ctx):
  newEmbed = discord.Embed(
    title = 'HELP',
    description = "Here are the bot's commands:",
    color = discord.Color.blue()
  )
  newEmbed.add_field(name='.hi', value='used to test if bot is active. If bot is active, it replies with "good day"',inline=True)

  newEmbed.add_field(name='.memberlist', value='returns a list of all the members in the server',inline=True)

  newEmbed.add_field(name='.allavatars', value='returns the avatars of all members in the server, this command may lag',inline=True)

  newEmbed.add_field(name='.avatar @name', value='returns the avatar of a specific member',inline=True)

  newEmbed.add_field(name='.tierlist', value='Invokes a tierlist generator, react to rank or remove members from the tierlist, then press confirm to generate the tierlist',inline=True)

  newEmbed.add_field(name='NOTES', value="commands that require embeds only work in channels were embed premissions are enabled, the larger the tierlist, the longer it takes to generate, tierlist only has 9 cells per row so if avatars inceed that number an error message will be returned",inline=True)

  await ctx.send(embed=newEmbed)

  
#Commands
@client.command()
async def memberlist(ctx):
  newEmbed = discord.Embed(
    title = 'MEMBER LIST',
    color = discord.Color.blue()
  )
  for member in ctx.message.guild.members:
      newEmbed.add_field(name='~~~', value=member,inline=False)

  await ctx.send(embed=newEmbed)

@client.command()
async def allavatars(ctx):
  show_avatar = discord.Embed(
    color = discord.Color.dark_blue()
  )

  for member in ctx.message.guild.members:
    show_avatar.set_image(url='{}'.format(member.avatar_url))
    await ctx.send(embed=show_avatar)


@client.command()
async def avatar(ctx, member: discord.Member):
  show_avatar = discord.Embed(

    color = discord.Color.dark_blue()

  )
  show_avatar.set_image(url='{}'.format(member.avatar_url))
  await ctx.send(embed=show_avatar)


async def on_command_error(self,ctx,exc):
  if isinstance(exc,MissingRequiredArgument):
      await ctx.send('a little gay')
  else:
    raise exc.original

client.loop.create_task(updateReaction())
client.run('ODY5NjA5NTgxNDgxOTcxNzEy.YQAtCA.OgUsnbRbr9_3dfOqK2MjXFtObYM')


