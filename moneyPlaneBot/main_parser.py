import discord
from discord.ext import commands

import json
import os 

from typing import Union
import random

from moneyPlaneBot import emojis
from moneyPlaneBot.database import DataBase, NULL_MONEY
from moneyPlaneBot.moneyplane import MoneyPlaneResult

with open(os.path.join(os.path.dirname(__file__), "quotes.txt"),'rt') as obj:
    quotes = obj.readlines()


db = DataBase()

_obj = open(os.path.join(os.path.dirname(__file__), "config.json"),'rt')
config = json.load(_obj)
_obj.close()

token = config["token"]

def list_format(*users):
    namelist = ""
    for i_n, name in enumerate(users):
        if i_n == 0:
            namelist+=name
        elif i_n == len(users)-1:
            namelist += ", and " + name
        else:
            namelist += ", " + name
    return namelist

class Bot(commands.Bot):
    """
    Run sync command on bot
    """
    async def async_cleanup(self):  # example cleanup function
        print("Cleaning up!")
        db.sync()

    async def close(self):
        await self.async_cleanup()
        
        await super().close()  # don't forget this!

intents=discord.Intents.all()

client = Bot(intents= intents, command_prefix="$")

@client.event
async def on_message(message:discord.Message):
    if message.author ==client.user:
        return

    received = message.content.lower()

    if received.startswith("$moneyplane"):
        if received.startswith("$moneyplane-fix"):
            """
                is used to fix moneyplanes 
            """
        content = message.content
        # trim the $moneyplane at the beginning 
        content = " ".join(content.split(" ")[1:])
        content = '"' + content + '"'

        db.new_moneyplane(message.id, message.author.id, content)

        full_text = "MoneyPlane!\n"
        full_text += "Moneyplane ID is {}".format(message.id)
        await message.channel.send(full_text)

    elif received.startswith("$getscore"):
        await message.channel.send("Your scores...")

        scores= db.get_score_dict()
        out_str = ""
        if len(scores.keys())==0:
            await message.channel.send("No points yet")
            return

        for user_id in scores.keys():
            user = await client.fetch_user(user_id)

            out_str += "{} : {} Moneybucks \n".format(user.display_name, 100+scores[user_id])
        
        await message.channel.send(out_str)
            
    elif received.startswith("$getstatus"):
        id_str = " ".join(received.split(" ")[1:])
        try:
            money_id = int(id_str)
        except ValueError:
            await message.channel.send("Failed to parse id '{}' as int".format(id_str))
            return
        
        mp = db.get_moneyplane(money_id)
        if mp == NULL_MONEY:
            await message.channel.send("Found no moneyplane with ID {}".format(money_id))
            return
        
        await send_mp_details(message.channel, money_id)


    elif received.startswith("$help"):

        quote = random.choice(quotes)
        await message.channel.send(quote)

        full_text = ""
        full_text+="Add moneyplanes with the command `$moneyplane <your moneyplane>`\n"
        full_text+="Check the high scores with `$getscore`\n"
        full_text+="See a moneyplane's status with `$getstatus <money_id>`\n"
        emoji_str=""
        emoji_str+= " "+ " ".join(emojis.RAWCOSIGN)
        emoji_str+= " "+ " ".join(emojis.RAWLAND)
        emoji_str+= " "+ " ".join(emojis.RAWCRASH)
        emoji_str+= " "+ " ".join(emojis.RAWWITNESS)
        emoji_str+= " "+ " ".join(emojis.RAWRUMBLE)
        
        full_text+="Be sure to only use these emoji: {}".format(emoji_str)
        await message.channel.send(full_text)

async def send_mp_details(channel:discord.channel, message_id):
    mp = db.get_moneyplane(message_id) 

    if mp == NULL_MONEY:
        await channel.send("No such moneyplane with ID {}".format(message_id))

    full_message = ""
    witness_names = [(await client.fetch_user(witness_id)).display_name for witness_id in  mp.witnesses]
    witness_names = list_format(*witness_names)
    rumble_names = list_format(*[(await client.fetch_user(witness_id)).display_name for witness_id in  mp.rumbles])
    cosign_names = list_format(*[(await client.fetch_user(witness_id)).display_name for witness_id in  mp.cosigners])
    author = (await client.fetch_user(mp.owner)).display_name

    possessive = author+"s" if author[-1]=="s" else author+"'s"
    full_message += "{} moneyplane: _{}_\n".format(possessive, mp.details)
    full_message += "No Witnesses. \n" if len(witness_names)==0 else "Witnessed by "+ witness_names+". \n"
    full_message += "" if len(rumble_names) == 0 else "Rumble by " +rumble_names +". \n"
    full_message += "" if len(cosign_names) == 0 else "Cosigned by " + cosign_names + ". \n"
    
    result = mp.result.name
    result = result[0].upper() + result[1:].lower()
    full_message+="Moneyplane "+result + ". \n"

    await channel.send(full_message)

@client.event
async def on_raw_reaction_add(payload:discord.RawReactionActionEvent):
    """
    
    """
    
    user_id = payload.user_id
    
    message_id = payload.message_id
    channel_id = payload.channel_id

    channel = client.get_channel(channel_id)    
    message = await channel.fetch_message(message_id)

    author = message.author.display_name
    possessive = author+"s" if author[-1]=="s" else author+"'s"

    reaction = payload.emoji.id
    received = message.content.lower()

    if received.startswith("$moneyplane"):
        pass
    else:
        return

    # check that it's in the database... 
    mp = db.get_moneyplane(message.id) 
    if mp == NULL_MONEY:
        print("Reacted on moneyplane with no database entry! Bad! ")
        return 

    async def witness_text(message_id):
        mp = db.get_moneyplane(message_id) 
        do_send = False
        if len(mp.witnesses)==2:
            do_send = True
        
        mp = db.get_moneyplane(message_id)
        if do_send:
            witnesses = mp.witnesses
            wit_names = []
            for witness_id in witnesses:
                user = await client.fetch_user(witness_id)
                name = user.display_name
                wit_names.append(name)

            namelist = list_format(*wit_names)

            await channel.send("{} witnessed ".format(namelist) + possessive + " moneyplane: '{}'".format(mp.details))

    # definitely ways to make this better... 
    if reaction in emojis.LAND:
        do_send = True
        db.land_add(message.id, user_id)
        mp = db.get_moneyplane(message_id)
        #if mp.result == MoneyPlaneResult.landed:
        #    do_send= False

        

        outtext = "{} moneyplane, \"{}\", landed! {}".format(possessive, mp.details, random.choice(emojis.RAWNUT))
        
        if do_send:
            await channel.send(outtext)

    elif reaction in emojis.COSIGN:
        if message.author.id == user_id:
            return
        db.cosign_add(message_id, user_id)
        db.witness_add(message.id, user_id)
        await witness_text(message.id)
    elif reaction in emojis.CRASH:

        outtext =  "{} moneyplane crashed. There were no survivors".format(possessive)
        await channel.send(outtext)
        await channel.send("This didn't happen: {}".format(mp.details))
        db.crash_add(message_id, user_id)
    elif reaction in emojis.WITNESS:
        if message.author.id == user_id:
            await channel.send("You can't witness your own moneyplane, {}".format(message.author.display_name))
            return 

        
        mp = db.get_moneyplane(message.id)
        
        db.witness_add(message.id, user_id)
        await witness_text(message.id)

    elif reaction in emojis.RUMBLE:
        if message.author.id == user_id:
            return

        db.witness_add(message.id, user_id)
        db.rumble_add(message.id, user_id)
        await witness_text(message.id)

    elif reaction in emojis.LONG:
        if message.author.id == user_id:
            return
        db.longshot_add(message.id, user_id)
        await witness_text(message.id)
    


@client.event
async def on_raw_reaction_remove(payload:discord.RawReactionActionEvent):
    reaction  = payload.emoji
    message_id = payload.message_id
    user = payload.user_id

    channel_id = payload.channel_id

    mp = db.get_moneyplane(message_id)


    # only care about this if the reaction is to a moneyplane 
    if mp!=NULL_MONEY:
        # definitely ways to make this better... 
        if reaction in emojis.LAND:
            pass
        elif reaction in emojis.COSIGN:
            db.cosign_remove(message_id, user.id)
        elif reaction in emojis.CRASH:
            pass
        elif reaction in emojis.WITNESS:
            db.witness_remove(message_id, user.id)
        elif reaction in emojis.RUMBLE:
            db.rumble_remove(message_id, user.id)
        elif reaction in emojis.LONG:
            db.longshot_remove(message_id, user.id)

client.run(token)
