import random
import tkinter as tk
from tkinter import messagebox
from itertools import combinations
from tkinter import ttk

def load_players_from_file(filename):
    players = []

    try:
        with open(filename, 'r') as file:
            for line in file:
                data = line.strip().split(',')
                if len(data) == 3:  # Ensure there are exactly 3 values: name, primary score, primary role
                    name = data[0]
                    primary_score = int(data[1])  # Assuming scores are integers
                    primary_role = data[2]
                    players.append({
                        'name': name,
                        'primary_score': primary_score,
                        'primary_role': primary_role,
                    })
                else:
                    print(f"Invalid line format: {line}")

    except FileNotFoundError:
        print(f"Error: The file '{filename}' was not found.")
        exit()

    return players


def save_sorted_players_to_file(filename, players):
    sorted_players = sorted(players, key=lambda x: x['name'])

    with open(filename, 'w') as file:
        for player in sorted_players:
            file.write(f"{player['name']},{player['primary_score']},{player['primary_role']}\n")


def select_players_gui(players):
    selected_players = []

    def select_player(player):
        if player in selected_players:
            selected_players.remove(player)
            update_selection_display()
        else:
            if len(selected_players) >= 10:
                messagebox.showinfo("Limit Reached", "You can only select 10 players.")
                return
            selected_players.append(player)
            update_selection_display()

    def update_selection_display():
        selection_label.config(text="Selected Players: " + ", ".join([player['name'] for player in selected_players]))

    def count_unique_roles(team):
        roles = {player['primary_role'] for player in team}
        return len(roles)

    def autodrafter():
        if len(selected_players) == 10:
            best_score_diff = float('inf')
            best_team1 = None
            best_team2 = None
            best_role_balance = -1
            
            # Shuffle the players to ensure randomness
            random.shuffle(selected_players)
            
            # Generate all combinations of 5 players from the shuffled selected players
            all_combinations = combinations(selected_players, 5)
            
            for team1 in all_combinations:
                team2 = [player for player in selected_players if player not in team1]
                
                # Calculate scores for team1 and team2
                team1_score = sum(player['primary_score'] for player in team1)
                team2_score = sum(player['primary_score'] for player in team2)
                
                # Calculate the role balance (unique roles in each team)
                team1_unique_roles = count_unique_roles(team1)
                team2_unique_roles = count_unique_roles(team2)
                
                # Calculate the score difference
                score_diff = abs(team1_score - team2_score)
                
                # Check if this combination is better: closer scores and better role balance
                if score_diff < best_score_diff:
                    best_score_diff = score_diff
                    best_team1 = team1
                    best_team2 = team2
                    best_role_balance = min(team1_unique_roles, team2_unique_roles)
                elif score_diff == best_score_diff:
                    # If scores are tied, prioritize the teams with more unique roles
                    if min(team1_unique_roles, team2_unique_roles) > best_role_balance:
                        best_team1 = team1
                        best_team2 = team2
                        best_role_balance = min(team1_unique_roles, team2_unique_roles)
            
            # Display the best teams with player stats and separator lines
            team1_text = "Team 1:\n"
            for player in best_team1:
                team1_text += f"{player['name']}, Score: {player['primary_score']}, Role: {player['primary_role']}\n"
                team1_text += "-" * 40 + "\n"  # Line separator between players
            
            team1_label.config(text=team1_text.strip())  # Remove trailing line
            team1_score_label.config(text=f"Team 1 Score: {sum(player['primary_score'] for player in best_team1)}")
            
            team2_text = "Team 2:\n"
            for player in best_team2:
                team2_text += f"{player['name']}, Score: {player['primary_score']}, Role: {player['primary_role']}\n"
                team2_text += "-" * 40 + "\n"  # Line separator between players
            
            team2_label.config(text=team2_text.strip())  # Remove trailing line
            team2_score_label.config(text=f"Team 2 Score: {sum(player['primary_score'] for player in best_team2)}")
            
            # Format the text for easy copy-pasting
            copy_paste_text = f"Team 1: {', '.join([player['name'] for player in best_team1])}\n" \
                            f"Team 2: {', '.join([player['name'] for player in best_team2])}"
            
            # Update the Text widget with the formatted copy-paste text
            copy_paste_box.delete(1.0, tk.END)  # Clear any existing content
            copy_paste_box.insert(tk.END, copy_paste_text)  # Insert the new formatted text

            # Switch to the "Team Display" tab
            notebook.select(team_display_tab)

        else:
            messagebox.showinfo("Incomplete Selection", "Please select exactly 10 players.")

    root = tk.Tk()
    root.title("Player Selection")

    notebook = ttk.Notebook(root)

    # Tab 1 (Player Selection Tab)
    tab1 = tk.Frame(notebook)
    notebook.add(tab1, text="Player Selection")

    tk.Label(tab1, text="Click on players to select them (10 players max):").grid(row=0, column=0, columnspan=5, pady=10)

    # Display buttons in a grid
    for idx, player in enumerate(players):
        row = (idx // 5) + 1  # Start placing buttons from row 1
        col = idx % 5
        button = tk.Button(tab1, text=player['name'], command=lambda p=player: select_player(p), width=16)
        button.grid(row=row, column=col, padx=5, pady=5)

    selection_label = tk.Label(tab1, text="Selected Players: ")
    selection_label.grid(row=(len(players) // 5) + 2, column=0, columnspan=5, pady=10)

    draft_button_first_tab = tk.Button(tab1, text="Draft Teams", command=autodrafter)
    draft_button_first_tab.grid(row=(len(players) // 5) + 3, column=0, columnspan=5, pady=10)

    # Tab 2 (Team Display Tab)
    team_display_tab = tk.Frame(notebook)
    notebook.add(team_display_tab, text="Team Display")

    team_display_frame = tk.Frame(team_display_tab)  # Frame to hold widgets in the second tab

    draft_button_second_tab = tk.Button(team_display_frame, text="Draft Teams", command=autodrafter)
    draft_button_second_tab.pack(pady=10)

    team1_label = tk.Label(team_display_frame, text="Team 1:")
    team1_label.pack(pady=10)

    team1_score_label = tk.Label(team_display_frame, text="Team 1 Score:")
    team1_score_label.pack(pady=10)

    team2_label = tk.Label(team_display_frame, text="Team 2:")
    team2_label.pack(pady=10)

    team2_score_label = tk.Label(team_display_frame, text="Team 2 Score:")
    team2_score_label.pack(pady=10)

    copy_paste_box = tk.Text(team_display_frame, height=3, width=80)
    copy_paste_box.pack(pady=10)

    team_display_frame.pack(fill="both", expand=True)  # Add the frame to the tab

    notebook.pack(fill="both", expand=True)  # Pack the notebook into the root window

    root.mainloop()

    return selected_players


# Main logic
players = load_players_from_file('players.txt')
select_players_gui(players)
save_sorted_players_to_file('players.txt', players)
