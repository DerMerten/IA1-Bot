import discord
import os
from numpy import random
import asyncio
from discord.ext import commands
from config import config
from dotenv import load_dotenv
from random import choice

# loads discord token from 'acc.env'
load_dotenv('acc.env')
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.all()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)
bot.remove_command('help')


# changes status. The values are in config.py
async def status_task():
    while True:
        await asyncio.sleep(10)
        await bot.change_presence(status=discord.Status.online,
                                  activity=discord.Game(random.choice(config.status)))


@bot.event
async def on_ready():
    bot.loop.create_task(status_task())
    print('Bot sussesful started at {0.user}'.format(bot))


# Personal feature, you can delete if you want. Its basically if someone types my name
# it pings me that someone wants to annoy me. Values in config.py
@bot.listen('on_message')
async def no(message):
    if message.content in config.bother:
        await message.channel.send(config.no)

    if message.author == bot.user:
        return


# error handler, not much to say
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(title="Unbekanntes Befehl",
                              description="Du hast den Befehl falsch geschrieben",
                              color=discord.Color.dark_teal())
        await ctx.channel.send(embed=embed)
    elif isinstance(error, commands.MemberNotFound):
        embed = discord.Embed(title="User nicht gefunden",
                              description="Ich kann dieses Mitglied nicht finden",
                              color=discord.Color.dark_teal())
        await ctx.channel.send(embed=embed)
    elif isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(title="Nicht Genügend Rechte",
                              description="Wenn du die benötigte Rechte hast, können wir dann darüber reden",
                              color=discord.Color.dark_teal())
        await ctx.channel.send(embed=embed)


# chunky help command
@bot.command(name='help')
async def help(ctx):
    embed = discord.Embed(title="**Commands**",
                          description="_**!help**_: zeigt die Befehle\n"
                                      "_**!howgay**_: zeigt wie Schwul du bist\n"
                                      "_**!opfer**_: frontet random irgendein User\n"
                                      "_**!profile**_: zeigt Infos über den User\n"
                                      "_**!clear**_: cleart die Nachrichten", color=discord.Color.dark_teal())

    await ctx.channel.send(embed=embed)


# more detailed information on mentioned user
@bot.command(name="profile")
async def profile(ctx, *, member: discord.Member):
    person = member
    personname = f"{member}"
    personid = member.id
    top_role = member.top_role.id
    role = discord.utils.get(ctx.guild.roles,
                             id=top_role)

    embed = discord.Embed(description=person.mention,
                          color=discord.Color.dark_teal())

    embed.set_author(name=personname,
                     icon_url=person.avatar_url)

    embed.set_thumbnail(url=person.avatar_url)
    embed.add_field(name="**User ID**", value=str(personid),
                    inline=False)

    embed.add_field(name="**Disocrd beigetreten**",
                    value=person.created_at.__format__('%A, %d. %B %Y @ %H:%M'),
                    inline=False)
    embed.add_field(name="**Server beigetreten**",
                    value=person.joined_at.__format__('%A, %d. %B %Y @ %H:%M'),
                    inline=False)
    embed.add_field(name="**Höchste Rolle**",
                    value=role.mention,
                    inline=False)

    await ctx.channel.send(embed=embed)


# I saw a bot do this so I wanted it myself
@bot.command(name='howgay')
async def howgay(ctx):
    x = random.randint(100)
    if ctx.author.id == config.ungayid:
        x = 0
    if ctx.author.id == config.supergayid:
        x = 100
    embed = discord.Embed(title="Gay Meter",
                          description="<@" + str(ctx.author.id) + "> ist zu " + str(x) + "% gay.",
                          color=discord.Color.dark_teal())
    await ctx.channel.send(embed=embed)


# clears messages up to 10 messages per command, if you go higher things will start to break, bc discord is stoopid
@bot.command(name='clear')
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount):
    mlimit = 100
    amount = int(amount)
    if (amount > mlimit):
        embed = discord.Embed(title="Limit überschritten",
                              description="Du kannst max. 100 Nachrichten löschen",
                              color=discord.Color.dark_teal())
        await ctx.channel.send(embed=embed, delete_after=5)

    else:
        await ctx.channel.purge(limit=amount)
        embed = discord.Embed(title="Nachrichten gelöscht.",
                              description=+ str(amount) + " Nachrichten wurden gelöscht!",
                              color=discord.Color.dark_teal())
        await ctx.channel.send(embed=embed, delete_after=5)


# auto-role
@bot.event
async def on_member_join(member):
    role = discord.utils.get(member.guild.roles, name=config.member_role)
    await member.add_roles(role)


@bot.event
async def manage_reaction(payload: discord.RawReactionActionEvent, type=None):
    try:
        if str(payload.message_id) in config.reactionroles.keys():
            if str(payload.emoji) in config.reactionroles[str(payload.message_id)].keys():
                guild = bot.get_guild(config.ServerID)
                member = guild.get_member(payload.user_id)
                if member.bot:
                    return
                for r in config.reactionroles[str(payload.message_id)][str(payload.emoji)]["roles"]:
                    role = guild.get_role(int(r))
                    if not role:
                        print(f"Rolle {r} nicht gefunden")
                        continue
                    if type == "add":
                        await member.add_roles(role, reason="Reaction Role")
                    elif type == "remove":
                        await member.remove_roles(role, reason="Reaction Role")
    except Exception as e:
        print(
            f"Fehler aufgetreten: \nAchte darauf, dass die JSON-Datei richtig formatiert ist und die Emojis bzw die Rollen ID´s korrekt sind!\nError:\n{e}")


@bot.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
    if payload.guild_id == config.ServerID:
        await manage_reaction(payload, "add")


@bot.event
async def on_raw_reaction_remove(payload: discord.RawReactionActionEvent):
    if payload.guild_id == config.ServerID:
        await manage_reaction(payload, "remove")


@commands.has_permissions(administrator=True)
async def react(ctx, message: discord.message):
    await ctx.message.delete()
    if not str(message.id) in config.reactionroles.keys():
        return await ctx.send("Diese Nachricht wurde nicht konfiguiert.", delete_after=5)
    else:
        for emoji in config.reactionroles[str(message.id)].keys():
            await message.add_reaction(emoji)
        await ctx.send("Erledigt!", delete_after=5)


@bot.command(pass_context=True)
async def opfer(ctx):
    user = random.choice(ctx.message.channel.guild.members)
    await ctx.send(f'{user.mention} {random.choice(config.beleigiungen)}')


# @bot.command(name='nigger')
# async def nigger_command(ctx=None):
#   embed = discord.Embed(title="Nigger.", color=discord.Color.dark_teal())
#  embed.set_image(url='https://tenor.com/view/caught-in-5000k-gif-20880260')
# await ctx.channel.send(embed=embed)


bot.run(DISCORD_TOKEN)
