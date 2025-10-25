import positions
import chess


def get_material_values(b: chess.Board) -> int:
    
    total_material = 0
    
    values = {
        chess.PAWN: 100,
        chess.KNIGHT: 320,
        chess.BISHOP: 330,
        chess.ROOK: 500,
        chess.QUEEN: 900,
        chess.KING: 2000,  # king material ignored (checkmates handled above)
    }

    #get number of pieces in the board of each type for white
    nwp = len(b.pieces(chess.PAWN, chess.WHITE))
    nwr = len(b.pieces(chess.ROOK, chess.WHITE))
    nwk = len(b.pieces(chess.KNIGHT, chess.WHITE))
    nwb = len(b.pieces(chess.BISHOP, chess.WHITE))
    nwq = len(b.pieces(chess.QUEEN, chess.WHITE))
    nwking = len(b.pieces(chess.KING, chess.WHITE))

    #get number of pieces in the board of each type for black
    nbp = len(b.pieces(chess.PAWN, chess.BLACK))
    nbr = len(b.pieces(chess.ROOK, chess.BLACK))
    nbk = len(b.pieces(chess.KNIGHT, chess.BLACK))
    nbb = len(b.pieces(chess.BISHOP, chess.BLACK))
    nbq = len(b.pieces(chess.QUEEN, chess.BLACK))
    nbking = len(b.pieces(chess.KING, chess.BLACK))


    #get the final value for each piece
    #whites
    wpw = nwp * values[chess.PAWN] #pawn
    wrw = nwr * values[chess.ROOK] #rook
    wkw = nwk * values[chess.KNIGHT] #knight
    wbw = nwb * values[chess.BISHOP] #bishop
    wqw = nwq * values[chess.QUEEN] #queen
    wkingw = nwking * values[chess.KING] #King

    #blacks
    bpw = nbp * values[chess.PAWN] #pawn
    brw = nbr * values[chess.ROOK] #rook
    bkw = nbk * values[chess.KNIGHT] #knight
    bbw = nbb * values[chess.BISHOP] #bishop
    bqw = nbq * values[chess.QUEEN] #queen
    bkingw = nbking * values[chess.KING] #King


    # add all the values
    white_material = wpw + wrw + wkw + wbw + wqw + wkingw 
    black_material = bpw + brw + bkw + bbw + bqw + bkingw
    total_material = white_material - black_material
    
    #print(total_material, black_material, white_material)

    return total_material


def get_evaluation(b: chess.Board) -> int:
    #check for terminal outcome
    if b.is_game_over():
        outcome = b.outcome()
        if outcome is None or outcome.winner is None:
            return 0  # draw
        return 10_000_000 if outcome.winner is chess.WHITE else -10_000_000
    
    #get material
    total_material = get_material_values(b)

    #get the values for each piece(value of white - value of black)
    #pawns
    pawn_value = sum([positions.pawnTable[index] for index in b.pieces(chess.PAWN, chess.WHITE)])
    pawn_value = pawn_value + sum([-positions.pawnTable[chess.square_mirror(index)] for index in b.pieces(chess.PAWN, chess.BLACK)])

    #rooks
    rook_value = sum([positions.rookTable[index] for index in b.pieces(chess.ROOK, chess.WHITE)])
    rook_value = rook_value + sum([-positions.rookTable[chess.square_mirror(index)] for index in b.pieces(chess.ROOK, chess.BLACK)])

    #knights
    knight_value = sum([positions.knightTable[index] for index in b.pieces(chess.KNIGHT, chess.WHITE)])
    knight_value = knight_value + sum([-positions.knightTable[chess.square_mirror(index)] for index in b.pieces(chess.KNIGHT, chess.BLACK)])

    #bishops
    bishop_value = sum([positions.bishopTable[index] for index in b.pieces(chess.BISHOP, chess.WHITE)])
    bishop_value = bishop_value + sum([-positions.bishopTable[chess.square_mirror(index)] for index in b.pieces(chess.BISHOP, chess.BLACK)])

    #queen
    queen_value = sum([positions.queenTable[index] for index in b.pieces(chess.QUEEN, chess.WHITE)])
    queen_value = queen_value + sum([-positions.queenTable[chess.square_mirror(index)] for index in b.pieces(chess.QUEEN, chess.BLACK)])

    #king
    king_value = sum([positions.kingTable[index] for index in b.pieces(chess.KING, chess.WHITE)])
    king_value = king_value + sum([-positions.kingTable[chess.square_mirror(index)] for index in b.pieces(chess.KING, chess.BLACK)])

    #print(total_material, pawn_value, rook_value, knight_value,  bishop_value , queen_value , king_value)
    eval_value = total_material + pawn_value + rook_value + knight_value + bishop_value + queen_value + king_value

    return eval_value
    

def evaluate(b: chess.Board) -> int:
            # Large score for terminal outcomes
            if b.is_game_over():
                outcome = b.outcome()
                if outcome is None or outcome.winner is None:
                    return 0  # draw
                return 10_000_000 if outcome.winner is chess.WHITE else -10_000_000

            #atacker have more value
            #check
            #not check mate
            #castling
            score = get_evaluation(b)
            return score