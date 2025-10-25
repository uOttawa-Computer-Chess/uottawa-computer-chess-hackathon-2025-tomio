"""
Some example classes for people who want to create a homemade bot.

With these classes, bot makers will not have to implement the UCI or XBoard interfaces themselves.
"""
import chess
from chess.engine import PlayResult, Limit
import random
from lib.engine_wrapper import MinimalEngine
from lib.lichess_types import MOVE, HOMEMADE_ARGS_TYPE
import logging
from collections import deque
import positions
import eval

# Use this logger variable to print messages to the console or log files.
# logger.info("message") will always print "message" to the console or log file.
# logger.debug("message") will only print "message" if verbose logging is enabled.
logger = logging.getLogger(__name__)


class ExampleEngine(MinimalEngine):
    """An example engine that all homemade engines inherit."""

class MyBot(ExampleEngine):
    """Template code for hackathon participants to modify.

    This is intentionally a very small, simple, and weak example engine
    meant for learning and quick prototyping only.

    Key limitations:
    - Fixed-depth search with only a very naive time-to-depth mapping (no true time management).
    - x No iterative deepening: the engine does not progressively deepen and use PV-based ordering.
    - x half No move ordering or capture heuristics: moves are searched in arbitrary order.
    - No transposition table or caching: repeated positions are re-searched.
    - Evaluation is material-only and very simplistic; positional factors are ignored.

    Use this as a starting point: add iterative deepening, quiescence search, move ordering (MVV/LVA, history),
    transposition table, and a richer evaluator to make it competitive.
    """

    def search(self, board: chess.Board, *args: HOMEMADE_ARGS_TYPE) -> PlayResult:
        # NOTE: The sections below are intentionally simple to keep the example short.
        # They demonstrate the structure of a search but also highlight the engine's
        # weaknesses (fixed depth, naive time handling, no pruning, no quiescence, etc.).
        # --- very simple time-based depth selection (naive) ---
        # Expect args to be (time_limit: Limit, ponder: bool, draw_offered: bool, root_moves: MOVE)
        time_limit = args[0] if (args and isinstance(args[0], Limit)) else None
        my_time = my_inc = None
        if time_limit is not None:
            if isinstance(time_limit.time, (int, float)):
                my_time = time_limit.time
                my_inc = 0
            elif board.turn == chess.WHITE:
                my_time = time_limit.white_clock if isinstance(time_limit.white_clock, (int, float)) else 0
                my_inc = time_limit.white_inc if isinstance(time_limit.white_inc, (int, float)) else 0
            else:
                my_time = time_limit.black_clock if isinstance(time_limit.black_clock, (int, float)) else 0
                my_inc = time_limit.black_inc if isinstance(time_limit.black_inc, (int, float)) else 0

        # Map a rough time budget to a coarse fixed depth.
        # Examples:
        # - >= 60s: depth 4
        # - >= 20s: depth 3
        # - >= 5s:  depth 2
        # - else:   depth 1
        remaining = my_time if isinstance(my_time, (int, float)) else None
        inc = my_inc if isinstance(my_inc, (int, float)) else 0
        budget = (remaining or 0) + 2 * inc  # crude increment bonus
        if remaining is None:
            total_depth = 2
        elif budget >= 60:
            total_depth = 2
        elif budget >= 20:
            total_depth = 2
        elif budget >= 5:
            total_depth = 2
        else:
            total_depth = 2
        total_depth = max(1, int(total_depth))

              # up to what I've done before
        # start with iterative deepening - mostly there with pv move ordering
        # move onto transposition table
        def traverseTree(b: chess.Board, depth: int, maximizing: bool, alpha, beta) -> int:
            if depth == 0 or b.is_game_over():
                return eval.evaluate(b)   
            scored_moves=deque([])
            if maximizing:
                best = -10**12
                for m in b.legal_moves:
                    b.push(m)
                    strength =eval.evaluate(b)
                    if len(scored_moves)==0 or scored_moves[0][1]<strength:
                        scored_moves.append([m, strength])
                    else:
                        scored_moves.appendleft([m,strength])    
                    b.pop()
                for m in scored_moves: 
                    b.push(m[0])   
                    val = traverseTree(b, depth - 1, False, alpha, beta)
                    b.pop()
                    if val > best:
                        best = val
                    if val > alpha:
                        alpha=val   
                    if(beta<=alpha):
                        return best 
                return best
            else:
                best = 10**12
                for m in b.legal_moves:
                    b.push(m)
                    strength = eval.evaluate(b)
                    if len(scored_moves)==0 or scored_moves[0][1]>strength:
                        scored_moves.append([m, strength])
                    else:
                        scored_moves.appendleft([m,strength])    
                    b.pop()
                for m in scored_moves: 
                    b.push(m[0])  
                    val = traverseTree(b, depth - 1, True, alpha, beta)
                    b.pop()
                    if val < best:
                        best = val
                    if val < beta:
                        beta=val    
                    if(beta<=alpha):
                        return best 
                return best

        # --- root move selection ---
        legal = list(board.legal_moves)
        if not legal:
            # Should not happen during normal play; fall back defensively
            return PlayResult(random.choice(list(board.legal_moves)), None)

        maximizing = board.turn == chess.WHITE
        best_move = None
        best_eval = -10**12 if maximizing else 10**12
        alpha=-10**12
        beta=10**12
        vals=[]
        # Lookahead depth chosen by the simple time heuristic; subtract one for the root move
        for m in legal:
            board.push(m)
            val = traverseTree(board, total_depth - 1, not maximizing, alpha, beta)
            board.pop()
            vals.append(val)
            if maximizing: 
                if val > best_eval:
                    best_eval, best_move = val, m
                if val > alpha:
                    alpha=val    
            elif not maximizing: 
                if val < best_eval:
                    best_eval, best_move = val, m
                if val < beta:
                    beta=val    

            if beta<=alpha:
                return best_eval, m

        # Fallback in rare cases (shouldn't trigger)
        print(best_eval, best_move, vals)
        if best_move is None:
            best_move = legal[0]
        
        return PlayResult(best_move, None)