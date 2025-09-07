import pygame
import math
import networkx as nx
from collections import defaultdict
import json

def distribute_votes(delegations, voted, balances):
    all_people = set(delegations.keys())
    for d_list in delegations.values():
        all_people.update(d_list)
    all_people.update(balances.keys())


    final_votes = defaultdict(float)
    for p in all_people:
        if p in voted:
            final_votes[p] = balances.get(p, 1.0)

    votes_to_distribute = {p: balances.get(p, 1.0) for p in all_people if p not in voted}

    print("Initial final_votes:", dict(final_votes))
    print("Initial votes_to_distribute:", votes_to_distribute)

    num_rounds = len(all_people) * 2 # Sufficiently large number of rounds

    for _ in range(num_rounds):
        if not votes_to_distribute:
            break
            
        next_round_votes = defaultdict(float)
        
        for p, weight in votes_to_distribute.items():
            # This person is a non-voter, distribute their current weight
            delegates = delegations.get(p)
            if not delegates:
                # Vote is lost if a non-voter has no delegates
                continue

            share = weight / len(delegates)
            for d in delegates:
                if d in voted:
                    final_votes[d] += share
                else:
                    # Delegate is also a non-voter, pass the vote for the next round
                    next_round_votes[d] += share
        
        votes_to_distribute = next_round_votes

    return dict(final_votes)


def draw_graph(delegations, initial_voted, balances):
    G = nx.DiGraph()
    for person, delegates in delegations.items():
        for d in delegates:
            G.add_edge(person, d)

    # Pygame setup
    pygame.init()
    width, height = 1280, 960
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Граф делегирования голосов (интерактивный)")
    font = pygame.font.Font(None, 24)
    small_font = pygame.font.Font(None, 20)

    positions_filename = "node_positions.json"
    all_nodes = set(G.nodes())
    node_positions = None

    try:
        with open(positions_filename, 'r') as f:
            loaded_positions = json.load(f)
        if set(loaded_positions.keys()) == all_nodes:
            node_positions = loaded_positions
            print("Загружены сохраненные позиции узлов.")
        else:
            print("Узлы в файле не соответствуют текущему графу. Будет создано новое расположение.")
    except (FileNotFoundError, json.JSONDecodeError):
        pass # Файл не найден или поврежден, будет создано новое расположение

    if node_positions is None:
        # Node positions using networkx layout, scaled to screen size
        print("Создание нового расположения узлов...")
        pos = nx.kamada_kawai_layout(G)

        # Normalize positions to be in [0, 1] range
        min_x = min(p[0] for p in pos.values())
        max_x = max(p[0] for p in pos.values())
        min_y = min(p[1] for p in pos.values())
        max_y = max(p[1] for p in pos.values())

        # Avoid division by zero if all nodes are in a line
        range_x = max_x - min_x if max_x > min_x else 1
        range_y = max_y - min_y if max_y > min_y else 1

        normalized_pos = {
            node: [
                (p[0] - min_x) / range_x,
                (p[1] - min_y) / range_y
            ]
            for node, p in pos.items()
        }

        node_positions = {
            node: [
                int(p[0] * (width - 100) + 50),
                int(p[1] * (height - 100) + 50)
            ]
            for node, p in normalized_pos.items()
        }

    # Colors
    GREEN = (144, 238, 144)
    GRAY = (211, 211, 211)
    BORDER_COLOR = (255, 255, 255)
    TEXT_COLOR = (0, 0, 0)
    EDGE_COLOR = (200, 200, 200)
    NODE_RADIUS = 30

    voted = initial_voted.copy()
    results = distribute_votes(delegations, voted, balances)

    running = True
    selected_node = None

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click for dragging
                    for node, p in node_positions.items():
                        if math.hypot(event.pos[0] - p[0], event.pos[1] - p[1]) <= NODE_RADIUS:
                            selected_node = node
                            break
                elif event.button == 3:  # Right click for voting
                    clicked_node = None
                    for node, p in node_positions.items():
                        if math.hypot(event.pos[0] - p[0], event.pos[1] - p[1]) <= NODE_RADIUS:
                            clicked_node = node
                            break
                    
                    if clicked_node:
                        if clicked_node in voted:
                            voted.remove(clicked_node)
                        else:
                            voted.add(clicked_node)
                        results = distribute_votes(delegations, voted, balances)
                        print("Итоговое распределение голосов:", results)

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Stop dragging
                    selected_node = None
            elif event.type == pygame.MOUSEMOTION:
                if selected_node:
                    node_positions[selected_node] = list(event.pos)

        # Drawing
        screen.fill((0, 0, 0))

        # Draw edges
        for edge in G.edges():
            start_pos = node_positions[edge[0]]
            end_pos = node_positions[edge[1]]
            # Arrow
            dx = end_pos[0] - start_pos[0]
            dy = end_pos[1] - start_pos[1]
            angle = math.atan2(dy, dx)
            # Shorten the line so it ends at the node's edge
            end_x = end_pos[0] - NODE_RADIUS * math.cos(angle)
            end_y = end_pos[1] - NODE_RADIUS * math.sin(angle)
            pygame.draw.line(screen, EDGE_COLOR, start_pos, (end_x, end_y), 2)

            # Arrowhead
            arrow_length = 15
            arrow_angle = math.pi / 6
            p1_x = end_x - arrow_length * math.cos(angle - arrow_angle)
            p1_y = end_y - arrow_length * math.sin(angle - arrow_angle)
            p2_x = end_x - arrow_length * math.cos(angle + arrow_angle)
            p2_y = end_y - arrow_length * math.sin(angle + arrow_angle)
            pygame.draw.polygon(screen, EDGE_COLOR, [(end_x, end_y), (p1_x, p1_y), (p2_x, p2_y)])


        # Draw nodes and labels
        for node, p in node_positions.items():
            color = GREEN if node in voted else GRAY
            pygame.draw.circle(screen, color, p, NODE_RADIUS)
            pygame.draw.circle(screen, BORDER_COLOR, p, NODE_RADIUS, 1)

            # Label
            label_text = f"{node}"
            text_surf = font.render(label_text, True, TEXT_COLOR)
            text_rect = text_surf.get_rect(center=p)
            screen.blit(text_surf, text_rect)

            # Result
            result_text = f"{results.get(node, 0):.2f}"
            result_surf = small_font.render(result_text, True, TEXT_COLOR)
            result_rect = result_surf.get_rect(center=(p[0], p[1] + 20))
            screen.blit(result_surf, result_rect)


        pygame.display.flip()

    # Save positions before quitting
    with open(positions_filename, 'w') as f:
        json.dump(node_positions, f, indent=4)
    print(f"Позиции узлов сохранены в {positions_filename}")

    pygame.quit()


if __name__ == "__main__":
    # ==== Новый сложный пример ====
    # Около 20 узлов, 5 голосуют, разнообразные связи

    # Узлы: N1, N2, ..., N20
    # Голосующие узлы: N5, N10, N15, N18, N20

    delegations = {
        # Простая цепочка, ведущая к голосующему
        "N1": ["N2"],
        "N2": ["N3"],
        "N3": ["N5"],  # N5 голосует

        # Узел, делегирующий двум разным веткам
        "N4": ["N5", "N10"], # Делегирует двум голосующим

        # Хаб: несколько узлов делегируют одному, который затем делегирует дальше
        "N6": ["N7"],
        "N8": ["N7"],
        "N9": ["N7"],
        "N7": ["N10"], # N10 голосует

        # Изолированный цикл (голоса теряются)
        "N11": ["N12"],
        "N12": ["N11"],

        # Цикл, из которого есть выход к голосующему
        "N13": ["N14"],
        "N14": ["N13", "N15"], # N15 голосует

        # Длинная и более сложная цепочка
        "N16": ["N17"],
        "N17": ["N18"], # N18 голосует

        # Изолированный узел, не голосует и никому не делегирует
        "N19": [],

        # Узлы, которые просто голосуют сами по себе
        "N5": [],
        "N10": [],
        "N15": [],
        "N18": [],
        "N20": [], # N20 тоже голосует
    }

    voted = {"N5", "N10", "N15", "N18", "N20"}

    balances = {
        "N1": 10,
        "N2": 20,
        "N3": 30,
        "N4": 5,
        "N16": 50,
        "N19": 100,
    }

    # Убедимся, что все узлы есть в словаре делегаций
    all_nodes = set(delegations.keys())
    for delegates_list in delegations.values():
        all_nodes.update(delegates_list)
    
    for node in all_nodes:
        if node not in delegations:
            delegations[node] = []

    draw_graph(delegations, voted, balances)
