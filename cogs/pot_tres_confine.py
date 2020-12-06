"""
POT TRES CONFINE EXTENSION - December 2020
Authors : Mathis Faucheux, Louis Gombert

Commands to manage the event : create channels and distribute participants to play games together
"""

from random import shuffle
import discord
from discord.ext import commands
from myutils import MyUtils


def setup(bot: commands.bot.Bot):
    """
    Setup function for the Discord extension
    :param bot: Discord bot reference
    """
    print("Pot très confiné load")
    bot.add_cog(CogPotTresConfine(bot))


class CogPotTresConfine(commands.Cog):
    """
    Cog class defining Discord commands to manage the "Pot Très Confiné" event
    """

    def __init__(self, bot):
        self.bot = bot
        self.microwave = [
            "https://tenor.com/view/microwave-gif-18041779",
        ]

    def has_orga_soiree_role():
        """
        Decorator used to verify if the user has the "Orga Soirée" rôle set.
        If they don't, raise an error
        """
        async def decorator(ctx):
            return MyUtils(ctx.guild).OrgaSoireeCheck(ctx)

        return commands.check(decorator)

    @commands.command()
    @has_orga_soiree_role()
    async def create_pot(self, ctx: commands.context.Context):
        """
        A command which sets up the channels for the event : in a group named "Pot Très Confiné",
        create one "general" text channel and one "General"  voice channel
        :param ctx: context object
        """
        category = await ctx.guild.create_category("Pot Très Confiné")
        await ctx.guild.create_text_channel("General", category=category)
        await ctx.guild.create_voice_channel("General", category=category)

    @commands.command()
    @has_orga_soiree_role()
    async def destroy_pot(self, ctx: commands.context.Context):
        """
        A command to destroy 1 event channels
        Destroys the first "Pot Très Confiné" channel group found
        :param ctx: context object
        """
        category = MyUtils(ctx.guild).getPotTresConfineCategory()
        for channels in category.channels:
            await channels.delete()
        await category.delete()

    @commands.command()
    @has_orga_soiree_role()
    async def repartition(self, ctx: commands.context.Context, max_by_channel: int = 8):
        """
        Distributes the participants placed in the general voice channel to random lobbies
        :param ctx: context object
        :param max_by_channel: number of maximum players placed in a channel
        """
        category = MyUtils(ctx.guild).getPotTresConfineCategory()
        general_channel_id = discord.utils.get(category.voice_channels, name="General").id
        member_ids = list(self.bot.get_channel(general_channel_id).voice_states.keys())
        nb_users = len(member_ids)

        # Create the right number of lobbies
        for i in range(int((nb_users / max_by_channel)) + 1):
            await ctx.guild.create_voice_channel(f"lobby-{i + 1}", category=category)

        voice_channels = category.voice_channels
        shuffle(member_ids)  # Randomize the ids

        # Move the participant to the right channel
        for index, _ in enumerate(member_ids):
            member = await ctx.guild.fetch_member(member_ids[index])
            await member.move_to(voice_channels[index // max_by_channel + 1])

    @commands.command()
    @has_orga_soiree_role()
    async def rassemblement(self, ctx: commands.context.Context):
        """
        Move every participant in the lobbies to the general channel
        :param ctx: context object
        """
        category = MyUtils(ctx.guild).getPotTresConfineCategory()
        general_channel_id = discord.utils.get(category.voice_channels, name="General").id
        voice_channel = category.voice_channels
        voice_channel.pop(0)

        for i in range(len(voice_channel) + 1):
            members = voice_channel[i].voice_states
            for member_id in members.keys():
                member = await ctx.guild.fetch_member(member_id)
                await member.move_to(self.bot.get_channel(general_channel_id))
            await voice_channel[i].delete()