# bot_gacha_format.py
# Format for coding a discord bot to perform a gacha style card collection game
# Robert Chang
# 7/17/23

# imports
import discord
from discord.ext import commands
import certifi
import os
import random2
import json
import time

os.environ["SSL_CERT_FILE"] = certifi.where()

# function to load the card collection dictionary
def load_data():
    # try opening the json file if it exists
    try:
        with open('''["document name of json file to store card information, can be any name (ex: "data.json")"]''', "r") as f:
            data = json.load(f)
    # if the json file doesn't exist or this is the first time the program is run, a new file will be created
    except FileNotFoundError:
        data = {}
    return data

# function to save the card collection dictionary
def save_data(data):
    with open('''["document name of json file to store card information"]''', "w") as f:
        json.dump(data, f)

# function to set a member's cooldown during the cooldown duration
cooldown_duration_claim = '''[desired claim cooldown in seconds]'''
def can_claim_card(member_id, data):
    last_claimed_time = data.get(member_id, {}).get("last_claimed_time", 0)
    current_time = time.perf_counter()
    elapsed_time = current_time - last_claimed_time

    # if a member wants to know whether they can claim at that moment, and the cooldown has not ended, the function will return False and the remaining_minutes
    if elapsed_time < cooldown_duration_claim:
        remaining_time = cooldown_duration_claim - elapsed_time
        if "{0:.3g}".format(remaining_time // 60) == "0":
            remaining_minutes = "less than a minute"
        elif "{0:.3g}".format(remaining_time // 60) == "1":
            remaining_minutes = "1 minute" 
        else:
            remaining_minutes = "{0:.3g}".format(remaining_time // 60) + " minutes"
        save_data(data)
        return False, remaining_minutes

    # otherwise, the function will return True with the remaining_minutes being 0
    return True, 0

# function to set a member's max number of rolls during the cooldown duration
max_rolls = '''[desired number of rolls per cooldown duration]'''
cooldown_duration_roll = '''[desired roll cooldown in seconds]'''
def can_roll_card(member_id, data):
    last_rolled_time = data.get(member_id, {}).get("last_rolled_time", 0)
    rolls_count = data.get(member_id, {}).get("rolls_count", 0)
    current_time = time.perf_counter()
    elapsed_time = current_time - last_rolled_time

    # converting a None type for rolls_count to 0
    if rolls_count is None:
        data[member_id]["rolls_count"] = 0
 
    if rolls_count >= max_rolls:
        # if a member has rolled up to the max rolls per cooldown period and the cooldown has not yet ended, the function will return False and the remaining_minutes
        if elapsed_time < cooldown_duration_roll:
            remaining_time = cooldown_duration_roll - elapsed_time
            if "{0:.3g}".format(remaining_time // 60) == "0":
                remaining_minutes = "less than a minute"
            elif "{0:.3g}".format(remaining_time // 60) == "1":
                remaining_minutes = "1 minute" 
            else:
                remaining_minutes = "{0:.3g}".format(remaining_time // 60) + " minutes"
            save_data(data)
            return False, remaining_minutes

        # if a member has rolled up to the max rolls per cooldown period and the cooldown has ended, the function will return True with the remaining minutes being 0, and the rolls_count will reset
        else:
            data[member_id]["rolls_count"] = 1
            save_data(data)
            return True, 0

    # if a member still has rolls left in a cooldown period which has ended, the function will return True and the rolls_count will reset
    if rolls_count <= max_rolls:
        if elapsed_time > cooldown_duration_roll:
            data[member_id]["rolls_count"] = 1
            data[member_id]["last_rolled_time"] = time.perf_counter()
            save_data(data)
            return True, 0
        
    # if a member still has rolls left in a cooldown period which has not yet ended, the function will return True and the rolls_count will increment by one with each roll   
    data[member_id]["rolls_count"] = data[member_id].get("rolls_count", 0) + 1
    data[member_id]["last_rolled_time"] = time.perf_counter()

    save_data(data)
    return True, 0

# function to check how many rolls a member has left
# this function is very similar to the previous can_roll_card() function, except it doesn't increment the rolls_count if called for, the member still has rolls left, and the cooldown has not ended yet
def check_rolls(member_id, data):
    last_rolled_time = data.get(member_id, {}).get("last_rolled_time", 0)
    rolls_count = data.get(member_id, {}).get("rolls_count", 0)
    current_time = time.perf_counter()
    elapsed_time = current_time - last_rolled_time
    
    # converting a None type for rolls_count to 0
    if rolls_count is None:
        data[member_id]["rolls_count"] = 0
    
    if rolls_count >= max_rolls:
        # if a member has rolled up to the max rolls per cooldown period and the cooldown has not yet ended, the function will return False and the remaining_minutes
        if elapsed_time < cooldown_duration_roll:
            remaining_time = cooldown_duration_roll - elapsed_time
            if "{0:.3g}".format(remaining_time // 60) == "0":
                remaining_minutes = "less than a minute"
            elif "{0:.3g}".format(remaining_time // 60) == "1":
                remaining_minutes = "1 minute" 
            else:
                remaining_minutes = "{0:.3g}".format(remaining_time // 60) + " minutes"
            save_data(data)
            return False, remaining_minutes

        # if a member has rolled up to the max rolls per cooldown period and the cooldown has ended, the function will return True with the remaining minutes being 0, and the rolls_count will reset
        else:
            data[member_id]["rolls_count"] = 1
            save_data(data)
            return True, 0
        
    # if a member still has rolls left in a cooldown period which has ended, the function will return True and the rolls_count will reset
    if rolls_count <= max_rolls:
        if elapsed_time > cooldown_duration_roll:
            data[member_id]["rolls_count"] = 0
            save_data(data)
            return True, 0

    save_data(data)
    return True, 0

# function to run the discord bot
def run_discord_bot():
    # sync the bot, program, and server
    TOKEN = '''["your unique discord token"]'''
    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)

    # confirm the bot, program, and server are synced
    # print statement is just to ensure the program is running well via the shell
    @client.event
    async def on_ready():
        print(f"{client.user} is now running!")

    # eliminate the possibility of infinite loops
    @client.event
    async def on_message(message):
        if message.author == client.user:
            return

        # creating the username, user_message, channel variables
        # print statement is just to ensure the program is running well via the shell
        username = message.author
        user_message = message.content
        channel = message.channel
        print(f"{username} said:"{user_message}" ({channel})")

        # url section for pictures for the cards
        '''
        You can have as many of these as you want, depending on how many cards you want to implement into the gacha.
        Follow this format for labeling the pictures of each card's url:
        '''
        
        '''[card name]''' = '''["url of the picture of the card"]'''

        # roll command
        if user_message.lower() == '''["command to be typed to call for a roll"]''':
            
            # append the cards to the members' collections and increment as more are collected
            data = load_data()
            member_id = str(username.id)
            # if it is the member's first time rolling, they will be added to the data
            if member_id not in data:
                data[member_id] = {}

            # check whether a member can roll or not
            can_roll, remaining_minutes = can_roll_card(member_id, data)
            if not can_roll:
                await message.channel.send(f"You have reached the maximum rolls per '''[roll cooldown duration]'''. Please wait for {remaining_minutes}.")
                return
            
            # run a gacha
            number = random2.randint('''[range of odds for your cards]''')

            '''
            The gacha works by generating a random number in the range specified by the variable "number"
            in the line above (ex: 1, 10000). Each number corresponds with a different card, and you can
            increase the range of numbers that corresponds with a certain card to increase the odds of getting
            that card. A card will be send if the randomized number lands in the range of its corresponding numbers.
            
            The following section is used for choosing the card to be sent in the discord channel.
            Depending on how you want to distribute the odds for the cards, this section will vary.
            There should be one "if statement" for each card you are including in the gacha.
            Follow this format for defining the odds of getting a card and creating a clean embed format:
            '''
            
            if number == '''[range of numbers for this card]''':
                card_id = '''["card name"]'''
                embed = discord.Embed(title = '''["card name"]''', description = '''["any descriptions, emotes, etc. you want to add to the card (can be multiple lines using \n)"]''', color = discord.Color.'''[color of the embed border]'''())
                embed.set_image(url = '''[card name from the url section that corresponds to the url of the picture of the card]''')
            
            # reaction to collect the card
            card = await message.channel.send(embed = embed)
            await card.add_reaction('''["emoji of your choice"]''')
            def check(reaction, user):
                # this line was coded to prohibit stealing of cards by other members; only the member who rolled the card can claim it
                # to lift the stealing restriction, delete the sections that define user specification
                return user == message.author and str(reaction.emoji) == '''["emoji of your choice"]''' and reaction.message.id == card.id

            reaction, user = await client.wait_for("reaction_add", check = check)

            # calculating the cooldown
            can_claim, remaining_minutes = can_claim_card(member_id, data)
                
            if not can_claim:
                await message.channel.send(f"You can only claim one card per '''[claim cooldown duration]'''! Please try again in {remaining_minutes}.")
                return

            # appending and incrementing the card collection
            if card_id not in data[member_id]:
                data[member_id][card_id] = 0
            data[member_id]["last_claimed_time"] = time.perf_counter()
            data[member_id][card_id] = data[member_id][card_id] + 1

            await message.channel.send("**You just collected a " + card_id[1:] + "!**")

            save_data(data)

        # view one's card collection
        if user_message.lower() == '''["command to be typed to view a member's card collection"]''':
            data = load_data()
            member_id = str(username.id)

            if member_id not in data:
                await message.channel.send("You haven't collected any cards yet!")
                return

            # the card information in the data dictionary is converted to a list
            cards_info = []
            for card_id, count in data[member_id].items():
                '''
                Because the data dictionary also includes other items such as last_rolled_time and
                rolls_count (which we don't want to display), you need to create a condition to only
                create a list with the cards. I would recommend adding a character, such as "x", before
                each card_id in the roll section. Therefore, only items with "x" preceeding it would be
                added to the card list, if we specify a condition in the next line. However, this would
                mean that whenever we want to print the name of a card, we need to call card_id using card_id[1:]
                to maintain the formatting of the name, which you may already see in various parts of the code.
                '''
                if card_id[0] == '''["defining character preceeding card_id (ex: "x")"]''':
                    cards_info.append(f":cherry_blossom: {card_id[1:]} - Count: {count}")
                else:
                    continue

            # the list of card information is formated into an embed
            cards_info_str = "\n".join(cards_info)
            embed = discord.Embed(title = str(username) + "'s Card Collection", description = '''["any descriptions, emotes, etc. you want to add to the card (can be multiple lines using \n)"]''', color = discord.Color.'''[color of the embed border]'''())
            await message.channel.send(embed = embed)

        # check how many rolls a member has left
        if user_message.lower() == '''["command to be typed to check roll status"]''':
            data = load_data()
            member_id = str(username.id)

            # add the member to the data if they're not there
            if member_id not in data:
                data[member_id] = {}
                
            can_roll, remaining_minutes = check_rolls(member_id, data)

            if not can_roll:
                await message.channel.send(f"You can roll again in {remaining_minutes}.")
            else:
                rolls_left = 10 - int(data.get(member_id, {}).get("rolls_count", 10))
                await message.channel.send(f"You have {rolls_left} rolls left!")

        # check if a member can claim right now
        if user_message.lower() == '''["command to be typed to check claim status"]''':
            data = load_data()
            member_id = str(username.id)

            # add the member to the data if they're not there
            if member_id not in data:
                data[member_id] = {}
                
            can_claim, remaining_minutes = can_claim_card(member_id, data)
                
            if not can_claim:
                await message.channel.send(f"You can claim again in {remaining_minutes}.")
            else:
                await message.channel.send("You can claim now!")
            
        # see cards
        '''
        This section is essentially a repeat of the roll command section, which defines a range of numbers
        that corresponds to a certain card. However, these commands are to be used to simply view a card and
        its information as an embed. There are some slight differences in the format for these commands. Again,
        there should be one "if statement" for each card that you want to include in the gacha.
        Follow this format for creating an embed to view a card:
        '''
            
        if user_message.lower() == '''["command to be typed to view a certain card"]''': # this command should vary for each card
            embed = discord.Embed(title = '''["card name"]''', description = '''["any descriptions, emotes, etc. you want to add to the card (can be multiple lines using \n)"]''', color = discord.Color.'''[color of the embed border]'''())
            embed.set_image(url = '''[card name from the url section that corresponds to the url of the picture of the card]''')
            await message.channel.send(embed = embed)

        # view the cards and their odds
        if user_message.lower() == '''["command to be typed to see the cards and their odds"]''':
            '''
            This section is quite customizable. The following line is an example of how I formatted my
            embed, but of course, you can edit the description and colors and whatnot to your liking.
            '''
            embed = discord.Embed(title = "Card Pool", description = "**Here are the names and odds of the cards that" + "\n" + "are currently up for grabs:**" + "\n\n" + ":game_die: **Card 1** ----- 5%" + "\n" + ":game_die: **Card 2** ----- 10%"  + "\n" + ":game_die: **Card 3** ----- 15%")
            await message.channel.send(embed = embed)

        # view the info menu
        if user_message.lower() == '''["command to be typed to see the info menu"]''':
            '''
            This section is quite customizable as well. Essentially, it's to be used as an introduction
            to your gacha program. You can include things like rules, prizes, notes, whatever you want!
            If you don't need a section like this, then you can delete this section. The following line
            is an example of how I formatted my embed.
            '''
            embed = discord.Embed(title = ":space_invader: **GACHA INFORMATION** :space_invader:", description = "**Welcome to the Gacha!**" +"\n\n" + "Roll, claim, and flex your card collection! Here are a few points to take note of:" + "\n\n" + "Rules, Rules, Rules")
            await message.channel.send(embed = embed)
            
        # view the help menu
        if user_message.lower() == '''["command to be typed to see the help menu"]''':
            '''
            This section is quite customizable as well. If you don't need it, you can delete this section.
            But of course, it's nice for your members to have a help section in case they forget certain
            commands. You can add more lines or less lines, the following ones are just an example of what
            I included in mine.
            '''
            command_info = "**!info** = information panel"
            command_roll = "**!roll** = roll for a card"
            command_collected = "**!collected** = view your collected cards"
            command_check_rolls = "**!checkrolls** = check how many rolls you currently have"
            command_check_claim = "**!checkclaim** = check if you can claim now"
            command_cards = "**!cards** = check what cards are available, their names, and their odds"
            command_see = "**!see [card name]** = view a card"
            command_help = "**!help** = help menu"
            embed = discord.Embed(title = "Help!", description = "**Seems like " + str(username) + " needs some help! Please refer to the following information.**\n\n" + command_info + "\n" + command_roll + "\n" + command_collected + "\n" + command_check_rolls + "\n" + command_check_claim + "\n" + command_cards + "\n" + command_see + "\n" + command_help + "\n\n" + "Have fun collecting!", color = discord.Color.red())
            await message.channel.send(embed = embed)

    client.run(TOKEN)
