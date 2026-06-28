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


def create_gradient_surface(width, height, top_color, bottom_color):
    grad_surf = pygame.Surface((1, height))
    for y in range(height):
        t = y / height
        r = int(top_color[0] * (1 - t) + bottom_color[0] * t)
        g = int(top_color[1] * (1 - t) + bottom_color[1] * t)
        b = int(top_color[2] * (1 - t) + bottom_color[2] * t)
        grad_surf.set_at((0, y), (r, g, b))
    return pygame.transform.scale(grad_surf, (width, height))


def StartScreen(screen):
    width, height = 1200, 650
    bg_gradient = create_gradient_surface(width, height, (24, 88, 48), (10, 36, 20))
    
    play_base = pygame.Rect(450, 250, 300, 55)
    diff_base = pygame.Rect(450, 335, 300, 55)
    exit_base = pygame.Rect(450, 420, 300, 55)
    
    difficulties = ["Easy", "Medium", "Hard"]
    diff_idx = 0
    
    font = pygame.font.SysFont('Times New Roman', 24, bold=True)
    title_font = pygame.font.SysFont('Times New Roman', 72, bold=True)
    subtitle_font = pygame.font.SysFont('Times New Roman', 20, italic=True)
    
    running = True
    while running:
        screen.blit(bg_gradient, (0, 0))
        
        # Title Shadow
        title_shadow = title_font.render("K L O N D I K E   S O L I T A I R E", True, (5, 20, 10))
        screen.blit(title_shadow, title_shadow.get_rect(center=(600 + 4, 130 + 4)))
        
        # Title
        title_surf = title_font.render("K L O N D I K E   S O L I T A I R E", True, (255, 215, 0))
        screen.blit(title_surf, title_surf.get_rect(center=(600, 130)))
        
        # Subtitle
        sub_text = subtitle_font.render("A Classic Card Game Experience", True, (200, 220, 200))
        screen.blit(sub_text, sub_text.get_rect(center=(600, 185)))
        
        mouse_pos = pygame.mouse.get_pos()
        
        is_play_hovered = play_base.collidepoint(mouse_pos)
        play_rect = play_base.inflate(12, 6) if is_play_hovered else play_base
        
        is_diff_hovered = diff_base.collidepoint(mouse_pos)
        diff_rect = diff_base.inflate(12, 6) if is_diff_hovered else diff_base
        
        is_exit_hovered = exit_base.collidepoint(mouse_pos)
        exit_rect = exit_base.inflate(12, 6) if is_exit_hovered else exit_base
        
        for r in [play_rect, diff_rect, exit_rect]:
            shadow_rect = r.copy()
            shadow_rect.x += 4
            shadow_rect.y += 4
            pygame.draw.rect(screen, (5, 20, 10), shadow_rect, border_radius=12)
            
        play_bg = (40, 55, 48) if is_play_hovered else (30, 42, 36)
        play_border = (255, 215, 0) if is_play_hovered else (150, 170, 155)
        pygame.draw.rect(screen, play_bg, play_rect, border_radius=12)
        pygame.draw.rect(screen, play_border, play_rect, width=3 if is_play_hovered else 2, border_radius=12)
        
        play_txt_surf = font.render("PLAY", True, (245, 245, 240))
        screen.blit(play_txt_surf, play_txt_surf.get_rect(center=play_rect.center))
        
        diff_bg = (40, 55, 48) if is_diff_hovered else (30, 42, 36)
        diff_border = (255, 215, 0) if is_diff_hovered else (150, 170, 155)
        pygame.draw.rect(screen, diff_bg, diff_rect, border_radius=12)
        pygame.draw.rect(screen, diff_border, diff_rect, width=3 if is_diff_hovered else 2, border_radius=12)
        
        difficulty = difficulties[diff_idx]
        diff_colors = {
            "Easy": (100, 220, 100),
            "Medium": (255, 180, 50),
            "Hard": (255, 100, 100)
        }
        
        diff_label = font.render("DIFFICULTY: ", True, (245, 245, 240))
        val_label = font.render(difficulty.upper(), True, diff_colors[difficulty])
        
        total_w = diff_label.get_width() + val_label.get_width()
        start_x = diff_rect.centerx - total_w // 2
        screen.blit(diff_label, (start_x, diff_rect.centery - diff_label.get_height() // 2))
        screen.blit(val_label, (start_x + diff_label.get_width(), diff_rect.centery - val_label.get_height() // 2))
        
        exit_bg = (40, 55, 48) if is_exit_hovered else (30, 42, 36)
        exit_border = (255, 215, 0) if is_exit_hovered else (150, 170, 155)
        pygame.draw.rect(screen, exit_bg, exit_rect, border_radius=12)
        pygame.draw.rect(screen, exit_border, exit_rect, width=3 if is_exit_hovered else 2, border_radius=12)
        
        exit_txt_surf = font.render("EXIT", True, (245, 245, 240))
        screen.blit(exit_txt_surf, exit_txt_surf.get_rect(center=exit_rect.center))
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if play_rect.collidepoint(event.pos):
                    return difficulty
                elif diff_rect.collidepoint(event.pos):
                    diff_idx = (diff_idx + 1) % 3
                elif exit_rect.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()


def Game(screen, difficulty="Easy"):
    global move, score, start_time
    move = 0
    score = 0
    start_time = time.time()
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

    # Toolbar variables
    menu_button_rect = pygame.Rect(740, 20, 80, 40)
    hint_button_rect = pygame.Rect(830, 20, 80, 40)
    undo_button_rect = pygame.Rect(920, 20, 80, 40)
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

        # Draw Menu Button
        mouse_pos = pygame.mouse.get_pos()
        menu_button_color = (200, 200, 200) # Default gray
        if menu_button_rect.collidepoint(mouse_pos):
            menu_button_color = (230, 230, 230) # Hover lighter gray
            
        pygame.draw.rect(screen, menu_button_color, menu_button_rect, border_radius=8)
        pygame.draw.rect(screen, (100, 100, 100), menu_button_rect, width=2, border_radius=8)
        
        btn_font = pygame.font.SysFont('Times New Roman', 18, bold=True)
        menu_text = btn_font.render("MENU", True, (50, 50, 50))
        menu_rect = menu_text.get_rect(center=menu_button_rect.center)
        screen.blit(menu_text, menu_rect)

        # Draw Hint Button
        hint_button_color = (200, 200, 200) # Default gray
        if hint_button_rect.collidepoint(mouse_pos):
            hint_button_color = (230, 230, 230) # Hover lighter gray
            
        pygame.draw.rect(screen, hint_button_color, hint_button_rect, border_radius=8)
        pygame.draw.rect(screen, (100, 100, 100), hint_button_rect, width=2, border_radius=8)
        
        hint_text = btn_font.render("HINT", True, (50, 50, 50))
        hint_rect = hint_text.get_rect(center=hint_button_rect.center)
        screen.blit(hint_text, hint_rect)

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
            desc_rect = desc_surface.get_rect(center=((menu_button_rect.centerx + undo_button_rect.centerx) // 2, hint_button_rect.bottom + 20))
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
                return "restart"
            else:
                return "exit"
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                if menu_button_rect.collidepoint(mouse_x, mouse_y):
                    return "restart"
                elif hint_button_rect.collidepoint(mouse_x, mouse_y):
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
                            draw_max = 1
                            if difficulty == "Hard":
                                draw_max = 3
                            elif difficulty == "Medium":
                                draw_max = 2
                                
                            if draw_max > 1:
                                if not stockpiles.Cards and stockpiles.DrawnCards:
                                    stockpiles.DrawOneCard()
                                    for _ in range(draw_max - 1):
                                        if stockpiles.Cards:
                                            stockpiles.DrawOneCard()
                                else:
                                    for _ in range(draw_max):
                                        if stockpiles.Cards:
                                            stockpiles.DrawOneCard()
                            else:
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
    return "exit"

if __name__ == "__main__":
    pygame.init()
    width, height = 1200, 650
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption('Solitaire Game')
    
    while True:
        difficulty = StartScreen(screen)
        result = Game(screen, difficulty)
        if result != "restart":
            break
            
    pygame.quit()
    sys.exit()
