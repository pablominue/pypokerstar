from pypokerstar.src.game.poker import Game, Player


player1 = Player(name="Pablo", pot=100)
player2 = Player(name="Juan", pot=100)

game = Game(player1, player2)

game.pre_flop()
