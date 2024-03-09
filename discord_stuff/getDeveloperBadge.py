from discord import app_commands, Intents, Client, Interaction

class Bot(Client):
    def __init__(self, *, intents: Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
 
    async def setup_hook(self) -> None:
        await self.tree.sync(guild=None)

bot = Bot(intents=Intents.default())

@bot.event
async def on_ready():
    print(f"Conectado como: {bot.user}")

@bot.tree.command()
async def givemebadge(interaction: Interaction):
    await interaction.response.send_message("# Listo!\n> Esperá 24 horas para reclamar la insignia.\n> Podés reclamarla [acá](https://discord.com/developers/active-developer)") 

token = input("Pega el TOKEN del bot de Discord: ")
bot.run()