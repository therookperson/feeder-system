import discord
from discord.ext import commands
import os
import random

# Load token from Railway environment
TOKEN = os.getenv("TOKEN")

# Path to images folder
IMAGE_ROOT = "images"

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)


# ---- Helper: get random image ----
def get_random_image(actress_name):
    folder = os.path.join(IMAGE_ROOT, actress_name)
    files = os.listdir(folder)

    # Filter images only
    images = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]

    if not images:
        return None

    return os.path.join(folder, random.choice(images))


# ---- UI View for feeding button ----
class FeedingView(discord.ui.View):
    def __init__(self, actress):
        super().__init__(timeout=None)
        self.actress = actress

    @discord.ui.button(label="Next Image", style=discord.ButtonStyle.primary)
    async def next_image(self, interaction: discord.Interaction, button: discord.ui.Button):
        img = get_random_image(self.actress)

        if img is None:
            await interaction.response.send_message("No images found.", ephemeral=True)
            return

        file = discord.File(img)

        embed = discord.Embed(
            title=f"{self.actress} Feed",
            color=0xf5a9b8
        )
        embed.set_image(url=f"attachment://{os.path.basename(img)}")

        await interaction.response.send_message(file=file, embed=embed)


# ---- Dropdown for selecting actress ----
class ActressSelect(discord.ui.Select):
    def __init__(self):
        actresses = [folder for folder in os.listdir(IMAGE_ROOT)
                     if os.path.isdir(os.path.join(IMAGE_ROOT, folder))]

        options = [
            discord.SelectOption(label=name, description=f"Feed images of {name}")
            for name in actresses
        ]

        super().__init__(
            placeholder="Choose an actress...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        actress = self.values[0]
        img = get_random_image(actress)

        if img is None:
            await interaction.response.send_message("This actress has no images!", ephemeral=True)
            return

        file = discord.File(img)

        embed = discord.Embed(
            title=f"{actress} Feed",
            color=0xf5a9b8
        )
        embed.set_image(url=f"attachment://{os.path.basename(img)}")

        view = FeedingView(actress)

        await interaction.response.send_message(file=file, embed=embed, view=view)


# ---- View containing the dropdown ----
class ActressSelectView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(ActressSelect())


# ---- Slash Command ----
@bot.tree.command(name="feed", description="Choose an actress to start image feeding.")
async def feed(interaction: discord.Interaction):
    view = ActressSelectView()
    await interaction.response.send_message("Select an actress to start feeding:", view=view)


@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Bot logged in as {bot.user}")


bot.run(TOKEN)
