import pygame
import sys
from deck import Deck
from Tableau import Tableau
from foundation import Foundation
from stockpile import Stockpile
import time

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


def Game():
    global move, score, start_time
    width, height = 1200, 650
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption('Solitaire Game')
    foundation_positions = [((350 + i * 100), 20) for i in range(4)]
    foundations = [Foundation(suit) for suit in ['Heart', 'Diamond', 'Clubs', 'Spades']]
    column_positions = [(50 + i * 100, 180) for i in range(7)]
    deck = Deck()
    tableau = Tableau(column_positions)
    deck = tableau.InitializeTableau(deck)
    stockpiles = Stockpile(deck)

    selected_col_index = None
    selected_card = None
    dragging = False
    dragged_card = None 

    running = True
    while running:
        screen.fill((34, 139, 34))
        stockpiles.PrintStockPile(screen, stockpiles)
        printFoundation(foundations, screen)
        for i in range(4):
            foundations[i].display_single_foundation(screen, foundations[i], foundation_positions[i])
        tableau.render_tableau(screen)
        draw_timer_and_score(screen)
        
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
                deck = tableau.InitializeTableau(deck)
                stockpiles = Stockpile(deck)
            else:
                break
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if stockpiles.detect_stockpile_click(event) == "StockPile":
                    stockpiles.DrawOneCard()
                else:
                    dragged_card = stockpiles.start_drag(event, stockpiles)
                selected_col_index, selected_card = tableau.detect_card_click(event)
                if selected_card and selected_card.FaceUp:
                    dragging = True

            elif event.type == pygame.MOUSEBUTTONUP:
                if dragging and selected_card:
                    mouse_x, mouse_y = event.pos
                    valid_move = False
                    for col_index in range(len(tableau.Piles)):
                        x, y = tableau.column_position[col_index]
                        pile_rect = pygame.Rect(x, y, 100, 500)
                        if pile_rect.collidepoint(mouse_x, mouse_y):
                            valid_move = tableau.move_card(selected_col_index, col_index, selected_card)
                            if valid_move:
                                print(f"Moved card from pile {selected_col_index} to pile {col_index}")
                                move += 1
                                score += 10
                                break
                            
                    for col_index in range(len(foundations)):
                        x, y = foundation_positions[col_index]
                        pile_rect = pygame.Rect(x, y, 100, 500)
                        if pile_rect.collidepoint(mouse_x, mouse_y):
                            (valid_move, tableau.Piles) = foundations[col_index].move_card(selected_col_index, selected_card, tableau.Piles)
                            if valid_move:
                                print(f"Moved card from pile {selected_col_index} to foundation {col_index}")
                                move += 1
                                score += 10
                                break

                    dragging = False
                    selected_col_index = None
                    selected_card = None

                elif dragged_card:
                    if stockpiles.place_card(event, dragged_card, tableau, foundations, foundation_positions):
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
