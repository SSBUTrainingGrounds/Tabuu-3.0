from random import choice
from typing import Optional

import discord


class BlackJackButtons(discord.ui.View):
    def __init__(self, author: discord.Member, member: discord.Member) -> None:
        super().__init__(timeout=60)
        self.author = author
        self.member = member
        self.author_hand = [[], 0]
        self.member_hand = [[], 0]
        self.folded = []
        self.turn = author
        self.message = None

    # All of the possible cards.
    card_faces = [
        "Ace",
        "2",
        "3",
        "4",
        "5",
        "6",
        "7",
        "8",
        "9",
        "10",
        "Jack",
        "Queen",
        "King",
    ]
    card_suites = ["♠️", "♦️", "♣️", "♥️"]

    def draw_card(self) -> None:
        card_deck = []
        for i, f in enumerate(self.card_faces):
            for s in self.card_suites:
                if i in (10, 11, 12):
                    i = 9
                card_deck.append([f"{f} of {s}", i + 1])

        card = choice(card_deck)

        # Checks if the card is already present in one hand, if so repeats the process.
        # I read that in real life blackjack is played with like 8 decks at once,
        # so this really isnt even needed
        if card[0] in self.author_hand[0] or card[0] in self.member_hand[0]:
            try:
                self.draw_card()
                return
            except RecursionError:
                return

        if self.turn == self.author:
            # If the card is an ace, checks if it should be worth 11 or 1.
            if card[1] == 1 and self.author_hand[1] <= 10:
                card[1] = 11
            self.author_hand[0].append(card[0])
            self.author_hand[1] += card[1]
        else:
            if card[1] == 1 and self.member_hand[1] <= 10:
                card[1] = 11
            self.member_hand[0].append(card[0])
            self.member_hand[1] += card[1]

    def get_winner(self) -> Optional[discord.Member]:
        # Checks for values greater than 21.
        if self.author_hand[1] > 21 >= self.member_hand[1]:
            return self.member

        if self.member_hand[1] > 21 >= self.author_hand[1]:
            return self.author

        # Checks for draws.
        if self.member_hand[1] == self.author_hand[1]:
            return None

        if self.author_hand[1] > self.member_hand[1]:
            return self.author

        return self.member

    async def end_game(self) -> None:
        self.stop()

        if self.get_winner():
            await self.message.reply(f"The winner is {self.get_winner().mention}!")
        else:
            await self.message.reply("The game is tied!")

    @discord.ui.button(
        label="Draw a Card", emoji="🃏", style=discord.ButtonStyle.blurple
    )
    async def draw(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        """Draws another card and checks if the players turn is over."""

        self.draw_card()

        if self.turn == self.author:
            if self.author_hand[1] > 20:
                await self.end_game()
            if self.member not in self.folded:
                self.turn = self.member
        else:
            if self.member_hand[1] > 20:
                await self.end_game()
            if self.author not in self.folded:
                self.turn = self.author

        await interaction.response.edit_message(
            content=f"{self.author.mention}'s Hand: {', '.join(self.author_hand[0])} ({self.author_hand[1]})\n"
            f"{self.member.mention}'s Hand: {', '.join(self.member_hand[0])} ({self.member_hand[1]})\n\n"
            f"It is {self.turn.mention}'s Turn.",
            view=self,
        )

    @discord.ui.button(label="Fold", emoji="❌", style=discord.ButtonStyle.red)
    async def fold(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        """Folds and switches the turn, or exits the game."""

        if self.turn == self.author:
            self.folded.append(self.author)
            self.turn = self.member
        else:
            self.folded.append(self.member)
            self.turn = self.author

        if all(x in self.folded for x in [self.member, self.author]):
            await self.end_game()

        await interaction.response.edit_message(
            content=f"{self.author.mention}'s Hand: {', '.join(self.author_hand[0])} ({self.author_hand[1]})\n"
            f"{self.member.mention}'s Hand: {', '.join(self.member_hand[0])} ({self.member_hand[1]})\n\n"
            f"It is {self.turn.mention}'s Turn.",
            view=self,
        )

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user not in (self.author, self.member):
            return False
        # We check if it's your turn.
        return interaction.user.id == self.turn.id

    async def on_timeout(self) -> None:
        await self.message.reply(
            f"The match timed out! {self.turn.mention} took too long to pick a choice!"
        )
