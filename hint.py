def get_card_position(tableau, pile_idx, card):
    pile = tableau.Piles[pile_idx]
    current = pile.Head
    i = 0
    x, y = tableau.column_position[pile_idx]
    while current:
        if current.Data == card:
            return (x, y + i * 30)
        current = current.Next
        i += 1
    return (x, y)

def get_pile_top_position(tableau, pile_idx):
    pile = tableau.Piles[pile_idx]
    x, y = tableau.column_position[pile_idx]
    size = pile.Size()
    if size == 0:
        return (x, y)
    return (x, y + (size - 1) * 30)

def get_all_hints(tableau, foundations, stockpiles, foundation_positions):
    hints = []
    
    # 1. Tableau to Foundation
    for i, pile in enumerate(tableau.Piles):
        top_card = pile.top()
        if top_card and top_card.FaceUp:
            for j, foundation in enumerate(foundations):
                if foundation.can_add_card(top_card):
                    hints.append({
                        'type': 'tableau_to_foundation',
                        'src_pos': get_card_position(tableau, i, top_card),
                        'dst_pos': foundation_positions[j],
                        'description': f"Move {top_card.Ranks} of {top_card.Suits} to Foundation",
                        'priority': 10
                    })
                    
    # 2. Waste to Foundation
    if stockpiles.DrawnCards:
        waste_card = stockpiles.DrawnCards[-1]
        for j, foundation in enumerate(foundations):
            if foundation.can_add_card(waste_card):
                hints.append({
                    'type': 'waste_to_foundation',
                    'src_pos': (150, 20),
                    'dst_pos': foundation_positions[j],
                    'description': f"Move {waste_card.Ranks} of {waste_card.Suits} to Foundation",
                    'priority': 10
                })
                
    # 3. Tableau to Tableau
    for i, pile in enumerate(tableau.Piles):
        current = pile.Head
        prev = None
        while current:
            card = current.Data
            if card.FaceUp:
                for j, target_pile in enumerate(tableau.Piles):
                    if i == j:
                        continue
                    if tableau.CanAddCard(target_pile, card):
                        # Filter redundant King moves
                        if target_pile.IsEmpty():
                            if card.Ranks == 'K' and prev is None:
                                continue
                        
                        # Check if this move reveals a face-down card
                        reveals_card = False
                        if prev and not prev.Data.FaceUp:
                            reveals_card = True
                        
                        priority = 8 if reveals_card else 4
                        hints.append({
                            'type': 'tableau_to_tableau',
                            'src_pos': get_card_position(tableau, i, card),
                            'dst_pos': get_pile_top_position(tableau, j),
                            'description': f"Move {card.Ranks} of {card.Suits} to Pile {j+1}",
                            'priority': priority
                        })
            prev = current
            current = current.Next
            
    # 4. Waste to Tableau
    if stockpiles.DrawnCards:
        waste_card = stockpiles.DrawnCards[-1]
        for j, target_pile in enumerate(tableau.Piles):
            if tableau.CanAddCard(target_pile, waste_card):
                hints.append({
                    'type': 'waste_to_tableau',
                    'src_pos': (150, 20),
                    'dst_pos': get_pile_top_position(tableau, j),
                    'description': f"Move {waste_card.Ranks} of {waste_card.Suits} to Pile {j+1}",
                    'priority': 5
                })
                
    # 5. Stockpile Draw / Recycle
    if stockpiles.Cards:
        hints.append({
            'type': 'draw_stockpile',
            'src_pos': (50, 20),
            'dst_pos': (150, 20),
            'description': "Draw a card from Stockpile",
            'priority': 1
        })
    elif stockpiles.DrawnCards:
        hints.append({
            'type': 'recycle_stockpile',
            'src_pos': (50, 20),
            'dst_pos': (150, 20),
            'description': "Recycle Waste Pile",
            'priority': 1
        })
        
    # Sort hints by priority descending
    hints.sort(key=lambda h: h['priority'], reverse=True)
    return hints
