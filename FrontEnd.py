import pygame
import sys
from deck import Deck
from Tableau import Tableau
from foundation import Foundation
from stockpile import Stockpile
import time
import math
from hint import get_all_hints

pygame.init()

start_time = time.time()
score = 0
move = 0


def draw_timer_and_score(screen):
    current_time = time.time() - start_time
    minutes = int(current_time // 60)
    seconds = int(current_time % 60)
    time_text = f"Time: {minutes:02}:{seconds:02}"
    score_text = f"Score: {score}"
    move_text = f"Move: {move}"
    
    # Set font and color
    font = pygame.font.SysFont('Times New Roman', 24)
    text_color = (255, 255, 255)
    
    # Create surfaces for each text
    time_surface = font.render(time_text, True, text_color)
    score_surface = font.render(score_text, True, text_color)
    move_surface = font.render(move_text, True, text_color)
    
    # Define positions for the text
    start_x = 1000
    start_y = 20
    gap = 20 
    
    # Blit the text directly onto the screen
    screen.blit(time_surface, (start_x, start_y))
    screen.blit(score_surface, (start_x, start_y + time_surface.get_height() + gap))
    screen.blit(move_surface, (start_x, start_y + time_surface.get_height() + score_surface.get_height() + 2 * gap))


def check_win(foundations):
    # Check if all foundations have 13 cards (one for each rank)
    return all(len(foundation.cards) == 13 for foundation in foundations)

def display_win_screen(screen):
    width, height = 1200, 650
    pygame.display.set_caption('Solitaire Game')
    screen.fill((0,0,0))
    # Display a win message
    font = pygame.font.SysFont('Times New Roman', 36)
    text_color = (255, 255, 255)
    win_text = font.render(f"You Win! Time: {int((time.time() - start_time) // 60)}:{int((time.time() - start_time) % 60)} Moves: {move}", True, text_color)
    restart_button = pygame.Rect(500, 300, 200, 50)
    exit_button = pygame.Rect(500, 400, 200, 50)

    # Draw buttons
    pygame.draw.rect(screen, (0, 255, 0), restart_button)
    pygame.draw.rect(screen, (255, 0, 0), exit_button)

    # Button text
    restart_text = font.render("Restart", True, (0, 0, 0))
    exit_text = font.render("Exit", True, (0, 0, 0))

    screen.blit(win_text, (400, 200))
    screen.blit(restart_text, (restart_button.centerx - restart_text.get_width() // 2, restart_button.centery - restart_text.get_height() // 2))
    screen.blit(exit_text, (exit_button.centerx - exit_text.get_width() // 2, exit_button.centery - exit_text.get_height() // 2))

    pygame.display.flip()

    # Event handling for buttons
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                if restart_button.collidepoint(mouse_x, mouse_y):
                    return "restart"
                if exit_button.collidepoint(mouse_x, mouse_y):
                    pygame.quit()
                    sys.exit()


def printFoundation(foundations, screen):
    font = pygame.font.SysFont(None, 16) 
    suits = ["Heart", "Diamond", "Club", "Spade"]
    for i, suit in enumerate(suits):
        if len(foundations[i].cards) > 0:
            continue
        pygame.draw.rect(screen, (0, 0, 0), ((350 + i * 100), 20, 80, 120), 2)
        
        text_color = (0, 0, 0) if suit in ["Spade", "Club"] else (255, 0, 0)
        text = font.render(suit, True, text_color)
        text_rect = text.get_rect(center=(350 + i * 100 + 40, 20 + 60))
        screen.blit(text, text_rect)


class UndoStack:
    def __init__(self):
        self.stack = []
        
    def push(self, data):
        self.stack.append(data)
        
    def pop(self):
        if not self.is_empty():
            return self.stack.pop()
        return None
        
    def is_empty(self):
        return len(self.stack) == 0
        
    def clear(self):
        self.stack.clear()


def capture_game_state(tableau, foundations, stockpiles, score, move):
    tableau_state = []
    for pile in tableau.Piles:
        pile_cards = []
        current = pile.Head
        while current:
            card = current.Data
            pile_cards.append((card.Suits, card.Ranks, card.FaceUp))
            current = current.Next
        tableau_state.append(pile_cards)
        
    foundations_state = []
    for f in foundations:
        f_cards = []
        for card in f.cards:
            f_cards.append((card.Suits, card.Ranks, card.FaceUp))
        foundations_state.append(f_cards)
        
    stockpiles_state = {
        'cards': [(card.Suits, card.Ranks, card.FaceUp) for card in stockpiles.Cards],
        'drawn_cards': [(card.Suits, card.Ranks, card.FaceUp) for card in stockpiles.DrawnCards],
        'current_draw_index': stockpiles.CurrentDrawIndex
    }
    
    return {
        'tableau': tableau_state,
        'foundations': foundations_state,
        'stockpiles': stockpiles_state,
        'score': score,
        'move': move
    }


def restore_game_state(state, tableau, foundations, stockpiles, card_registry):
    for i, pile_cards in enumerate(state['tableau']):
        tableau.Piles[i].MakeStackEmpty()
        for suits, ranks, face_up in pile_cards:
            card = card_registry[(suits, ranks)]
            card.FaceUp = face_up
            tableau.Piles[i].Push(card)
            
    for i, f_cards in enumerate(state['foundations']):
        foundations[i].cards = []
        for suits, ranks, face_up in f_cards:
            card = card_registry[(suits, ranks)]
            card.FaceUp = face_up
            foundations[i].cards.append(card)
            
    stockpiles.Cards = []
    for suits, ranks, face_up in state['stockpiles']['cards']:
        card = card_registry[(suits, ranks)]
        card.FaceUp = face_up
        stockpiles.Cards.append(card)
        
    stockpiles.DrawnCards = []
    for suits, ranks, face_up in state['stockpiles']['drawn_cards']:
        card = card_registry[(suits, ranks)]
        card.FaceUp = face_up
        stockpiles.DrawnCards.append(card)
        
    stockpiles.CurrentDrawIndex = state['stockpiles']['current_draw_index']
    return state['score'], state['move']


def Game():
    global move, score, start_time
    width, height = 1200, 650
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption('Solitaire Game')
    foundation_positions = [((350 + i * 100), 20) for i in range(4)]
    foundations = [Foundation(suit) for suit in ['Heart', 'Diamond', 'Clubs', 'Spades']]
    column_positions = [(50 + i * 100, 180) for i in range(7)]
    deck = Deck()
    card_registry = {(card.Suits, card.Ranks): card for card in deck.Cards}
    tableau = Tableau(column_positions)
    deck = tableau.InitializeTableau(deck)
    stockpiles = Stockpile(deck)

    selected_col_index = None
    selected_card = None
    dragging = False
    dragged_card = None 

    # Hint and Undo variables
    hint_button_rect = pygame.Rect(780, 20, 100, 40)
    undo_button_rect = pygame.Rect(890, 20, 100, 40)
    undo_stack = UndoStack()
    active_hints = []
    current_hint_idx = 0
    active_hint = None

    running = True
    while running:
        screen.fill((34, 139, 34))
        stockpiles.PrintStockPile(screen, stockpiles)
        printFoundation(foundations, screen)
        for i in range(4):
            foundations[i].display_single_foundation(screen, foundations[i], foundation_positions[i])
        tableau.render_tableau(screen)
        draw_timer_and_score(screen)

        # Draw Hint Button
        mouse_pos = pygame.mouse.get_pos()
        button_color = (200, 200, 200) # Default gray
        if hint_button_rect.collidepoint(mouse_pos):
            button_color = (230, 230, 230) # Hover lighter gray
            
        pygame.draw.rect(screen, button_color, hint_button_rect, border_radius=8)
        pygame.draw.rect(screen, (100, 100, 100), hint_button_rect, width=2, border_radius=8)
        
        btn_font = pygame.font.SysFont('Times New Roman', 20, bold=True)
        btn_text = btn_font.render("HINT", True, (50, 50, 50))
        btn_rect = btn_text.get_rect(center=hint_button_rect.center)
        screen.blit(btn_text, btn_rect)

        # Draw Undo Button
        undo_button_color = (200, 200, 200) # Default gray
        if undo_button_rect.collidepoint(mouse_pos):
            undo_button_color = (230, 230, 230) # Hover lighter gray
            
        pygame.draw.rect(screen, undo_button_color, undo_button_rect, border_radius=8)
        pygame.draw.rect(screen, (100, 100, 100), undo_button_rect, width=2, border_radius=8)
        
        undo_text = btn_font.render("UNDO", True, (50, 50, 50))
        undo_text_rect = undo_text.get_rect(center=undo_button_rect.center)
        screen.blit(undo_text, undo_text_rect)

        # Draw Active Hint
        if active_hint:
            desc_font = pygame.font.SysFont('Times New Roman', 18, italic=True)
            desc_surface = desc_font.render(active_hint['description'], True, (255, 255, 150))
            desc_rect = desc_surface.get_rect(center=((hint_button_rect.centerx + undo_button_rect.centerx) // 2, hint_button_rect.bottom + 20))
            screen.blit(desc_surface, desc_rect)
            
            if 'src_pos' in active_hint and 'dst_pos' in active_hint:
                src_x, src_y = active_hint['src_pos']
                dst_x, dst_y = active_hint['dst_pos']
                
                ticks = pygame.time.get_ticks()
                pulse = 0.5 + 0.5 * math.sin(ticks * 0.01)
                thickness = 3 + int(3 * pulse)
                
                gold_color = (255, 215, 0)
                green_color = (50, 205, 50)
                
                src_rect = pygame.Rect(src_x, src_y, 80, 120)
                pygame.draw.rect(screen, gold_color, src_rect, width=thickness, border_radius=8)
                
                dst_rect = pygame.Rect(dst_x, dst_y, 80, 120)
                pygame.draw.rect(screen, green_color, dst_rect, width=thickness, border_radius=8)
                
                # Draw connecting trail of glowing yellow dots
                start_pt = src_rect.center
                end_pt = dst_rect.center
                dx, dy = end_pt[0] - start_pt[0], end_pt[1] - start_pt[1]
                dist = math.hypot(dx, dy)
                if dist > 0:
                    ux, uy = dx / dist, dy / dist
                    dot_dist = 15
                    dot_count = int(dist // dot_dist)
                    for k in range(1, dot_count):
                        px = int(start_pt[0] + ux * k * dot_dist)
                        py = int(start_pt[1] + uy * k * dot_dist)
                        pygame.draw.circle(screen, (255, 255, 200), (px, py), 4)
        
        if check_win(foundations):
            result = display_win_screen(screen)
            if result == "restart":
                # Reset the game
                move = 0
                score = 0
                start_time = time.time()
                foundations = [Foundation(suit) for suit in ['Heart', 'Diamond', 'Clubs', 'Spades']]
                tableau = Tableau(column_positions)
                deck = Deck()
                card_registry = {(card.Suits, card.Ranks): card for card in deck.Cards}
                deck = tableau.InitializeTableau(deck)
                stockpiles = Stockpile(deck)
                active_hint = None
                active_hints = []
                current_hint_idx = 0
                undo_stack.clear()
            else:
                break
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                if hint_button_rect.collidepoint(mouse_x, mouse_y):
                    # Generate/cycle hints
                    if not active_hints:
                        active_hints = get_all_hints(tableau, foundations, stockpiles, foundation_positions)
                        current_hint_idx = 0
                    else:
                        fresh_hints = get_all_hints(tableau, foundations, stockpiles, foundation_positions)
                        if len(fresh_hints) == len(active_hints):
                            current_hint_idx = (current_hint_idx + 1) % len(fresh_hints)
                        else:
                            active_hints = fresh_hints
                            current_hint_idx = 0
                    
                    if active_hints:
                        active_hint = active_hints[current_hint_idx]
                    else:
                        active_hint = {'description': "No moves available"}
                elif undo_button_rect.collidepoint(mouse_x, mouse_y):
                    # Trigger Undo
                    state = undo_stack.pop()
                    if state:
                        score, move = restore_game_state(state, tableau, foundations, stockpiles, card_registry)
                    active_hint = None
                    active_hints = []
                else:
                    active_hint = None
                    active_hints = []
                    if stockpiles.detect_stockpile_click(event) == "StockPile":
                        if stockpiles.Cards or stockpiles.DrawnCards:
                            state_snapshot = capture_game_state(tableau, foundations, stockpiles, score, move)
                            stockpiles.DrawOneCard()
                            undo_stack.push(state_snapshot)
                    else:
                        dragged_card = stockpiles.start_drag(event, stockpiles)
                    selected_col_index, selected_card = tableau.detect_card_click(event)
                    if selected_card and selected_card.FaceUp:
                        dragging = True

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_h:
                    if active_hint:
                        # Toggle Off
                        active_hint = None
                        active_hints = []
                    else:
                        # Toggle On
                        active_hints = get_all_hints(tableau, foundations, stockpiles, foundation_positions)
                        current_hint_idx = 0
                        if active_hints:
                            active_hint = active_hints[current_hint_idx]
                        else:
                            active_hint = {'description': "No moves available"}
                elif event.key == pygame.K_u or (event.key == pygame.K_z and pygame.key.get_mods() & pygame.KMOD_CTRL):
                    state = undo_stack.pop()
                    if state:
                        score, move = restore_game_state(state, tableau, foundations, stockpiles, card_registry)
                    active_hint = None
                    active_hints = []

            elif event.type == pygame.MOUSEBUTTONUP:
                if dragging and selected_card:
                    mouse_x, mouse_y = event.pos
                    valid_move = False
                    for col_index in range(len(tableau.Piles)):
                        x, y = tableau.column_position[col_index]
                        pile_rect = pygame.Rect(x, y, 100, 500)
                        if pile_rect.collidepoint(mouse_x, mouse_y):
                            state_snapshot = capture_game_state(tableau, foundations, stockpiles, score, move)
                            valid_move = tableau.move_card(selected_col_index, col_index, selected_card)
                            if valid_move:
                                undo_stack.push(state_snapshot)
                                print(f"Moved card from pile {selected_col_index} to pile {col_index}")
                                move += 1
                                score += 10
                                break
                            
                    for col_index in range(len(foundations)):
                        x, y = foundation_positions[col_index]
                        pile_rect = pygame.Rect(x, y, 100, 500)
                        if pile_rect.collidepoint(mouse_x, mouse_y):
                            state_snapshot = capture_game_state(tableau, foundations, stockpiles, score, move)
                            (valid_move, tableau.Piles) = foundations[col_index].move_card(selected_col_index, selected_card, tableau.Piles)
                            if valid_move:
                                undo_stack.push(state_snapshot)
                                print(f"Moved card from pile {selected_col_index} to foundation {col_index}")
                                move += 1
                                score += 10
                                break

                    dragging = False
                    selected_col_index = None
                    selected_card = None

                elif dragged_card:
                    state_snapshot = capture_game_state(tableau, foundations, stockpiles, score, move)
                    if stockpiles.place_card(event, dragged_card, tableau, foundations, foundation_positions):
                        undo_stack.push(state_snapshot)
                        print("Moved card from waste pile to a valid location.")
                        move += 1
                        score += 10
                    dragged_card = None

        if dragging and selected_card:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if selected_card.FaceUp:
                screen.blit(selected_card.Image, (mouse_x - selected_card.Image.get_width() // 2, mouse_y - selected_card.Image.get_height() // 2))
        elif dragged_card:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            stockpiles.drag_card(screen, dragged_card, mouse_x, mouse_y)

        pygame.display.flip()

if __name__ == "__main__":
    Game()
    pygame.quit()
    sys.exit()
