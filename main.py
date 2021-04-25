import plotly.graph_objects as go
import csv
from operator import itemgetter

# manually set/adjusted variables (for now)
seasons_to_view = 14
max_days_per_season = 135
team_to_display = "Firefighters"
selected_season_and_day = ['13', '', '120', '' ]# season 13 day 120
x_axis_type = "DYNAMIC" # current options are "LINEAR" and "DYNAMIC"

class Player:
    def __init__(self, career_phase):
        self.__id = career_phase["player_id"]
        self.__name = career_phase["player_name"]
        self.__team_history = [career_phase["nickname"]]
        self.__career_phases = [career_phase]

    def get_id(self):
        return self.__id

    def get_name(self):
        return self.__name

    def get_team_history(self):
        return self.__team_history

    def get_career_phases(self):
        return self.__career_phases

    def was_player_ever_on_team(self, team_searched):
        return team_searched in self.__team_history

    def update_info(self, career_phase):
        self.__career_phases.append(career_phase)
        self.__team_history.append(career_phase["nickname"])

# takes in a player career phase and generates a dictionary object that will be used for plotting along the X axis
def create_player_x_axis_nodes_and_labels(player_career_phase):
    team = player_career_phase["nickname"]

    season_and_day_1 = player_career_phase["gamephase_from_timestamp"].split(",")
    season_and_day_2 = player_career_phase["gamephase_from_timestamp-2"].split(",")

    x_position_dictionary_1 = {"season": int(season_and_day_1[0]),
                                "day": int(season_and_day_1[2]),
                                "team": team}

    x_position_dictionary_2 = {"season": int(season_and_day_2[0]),
                                "day": int(season_and_day_2[2]) - 1,
                                "team": team}

    label_1 = player_career_phase["player_name"] + " S" + str(int(season_and_day_1[0]) + 1) + "D" + str(int(season_and_day_1[2]) + 1)
    label_2 = ""

    return x_position_dictionary_1, label_1, x_position_dictionary_2, label_2

# create everything used for plotting the graph
def export_processed_graphing_info(player_career_phases, index_of_last_node_added, current_season_and_day):
    node_labels = []
    node_x_position_dictionaries = []
    node_y_position_dictionaries = []
    node_colors = []
    link_sources = []
    link_targets = []
    link_values = []
    link_colors = []
    phase_count = 0
    new_index = 0
    for current_career_phase in player_career_phases:
        # each career phase is a pair of nodes (start and end) with a link between,
        # a span where they were on one team
        color = current_career_phase["team_main_color"]
        color_2 = current_career_phase["team_secondary_color"]
        x_position_dictionary_1, label_1, x_position_dictionary_2, label_2 = create_player_x_axis_nodes_and_labels(current_career_phase)
        y_position_dictionary = {"team_name": current_career_phase["nickname"],
                                    "position_type_id": current_career_phase["position_type_id"],
                                    "position_id": current_career_phase["position_id"]}

        # first node
        node_labels.append(label_1)
        node_x_position_dictionaries.append(x_position_dictionary_1)
        node_y_position_dictionaries.append(y_position_dictionary)
        node_colors.append(color)
        link_sources.append((2*phase_count) + index_of_last_node_added)
        link_targets.append((2*phase_count) + index_of_last_node_added + 1)
        link_values.append(1)
        link_colors.append(color_2)

        # second node
        node_labels.append(label_2)
        node_x_position_dictionaries.append(x_position_dictionary_2)
        node_y_position_dictionaries.append(y_position_dictionary)
        node_colors.append(color)

        # if this is the last node in the players career, don't add a link to the next node
        if (phase_count + 1) < len(player_career_phases):
            link_sources.append((2*phase_count) + index_of_last_node_added + 1)
            link_targets.append((2*phase_count) + index_of_last_node_added + 2)
            link_values.append(1)
            link_colors.append(color_2)
        phase_count += 1

    new_index = index_of_last_node_added + len(node_labels)

    return {"node_labels": node_labels,
            "link_sources": link_sources,
            "link_targets": link_targets,
            "link_values": link_values,
            "link_colors": link_colors,
            "node_x_position_dictionaries": node_x_position_dictionaries,
            "node_y_position_dictionaries": node_y_position_dictionaries,
            "node_colors": node_colors,
            "new_index": new_index}

# takes in a player career phase and calls all of our functions that help process the data.
# it then returns the career phase with the processed data.
# this way you only need to call this function once and then never worry about formatting the data again
# also makes it easy to add new methods to process career phase data if the need arises
def process_player_info(career_phase):
    career_phase["gamephase_from_timestamp"] = process_season_and_day_timestamp(career_phase["gamephase_from_timestamp"])
    career_phase["gamephase_from_timestamp-2"] = process_season_and_day_timestamp(career_phase["gamephase_from_timestamp-2"])

    return career_phase

# blaseball timestamps are generally formatted like "(13,,27,GAMEDAY)" which we parse into an array formatted like "['13', '', '27', 'GAMEDAY]" and then resave once processed as "13,,27,GAMEDAY" for Season 13 day 27
# sometimes the timestamp has words in them instead of numbers so here we clean the data so every timestamp has a number for season and day
def process_season_and_day_timestamp(timestamp):
    # turn the string timestamp into an array
    timestamp = timestamp.strip("()").split(",")
    
    # clean the timstamp
    if timestamp == ['NULL']:
        timestamp = selected_season_and_day
    if timestamp[2] == '':
        if timestamp[3] == 'PRESEASON':
            timestamp[2] = '0'
        if timestamp[3] == 'EARLY_SIESTA':
            timestamp[2] = '27'
        if timestamp[3] == 'LATE_SIESTA':
            timestamp[2] = '72'
        if timestamp[3] == 'END_REGULAR_SEASON':
            timestamp[2] = '99'
        if timestamp[3] == 'END_POSTSEASON':
            timestamp[2] = '125'
        if timestamp[3] == 'BOSS_FIGHT':
            timestamp[2] = '130'
        if timestamp[3] == 'ELECTIONS' or timestamp[3] == 'ELECTION_RESULTS':
            timestamp[2] = '135'

    # turn the timestamp array back into a string
    timestamp = ','.join(timestamp)
    return timestamp

# returns a list of unique timestamps for every season/day in a teams history
def get_teams_unique_seasons_and_days(players_dict, selected_team, index_of_last_node_added):
    unique_season_and_day_list = []

    # for every player that has been or is on the team, get their x axis nodes
    for player in players_dict.values():
        if player.was_player_ever_on_team(selected_team):
            node_export = export_processed_graphing_info(player.get_career_phases(), index_of_last_node_added, selected_season_and_day)
            node_x_position_dictionaries = node_export["node_x_position_dictionaries"]

            # for every unique season/day timestamp, add it to the list
            for node_dictionary in node_x_position_dictionaries:
                season_and_day = [node_dictionary.get("season"), node_dictionary.get("day")]
                if not season_and_day in unique_season_and_day_list:
                    unique_season_and_day_list.append(season_and_day)

    # sort the list and return
    unique_season_and_day_list.sort(key=itemgetter(0, 1))
    return unique_season_and_day_list

# a dict mapping player Id to the Player object defined above
players_index = {}

# used to graph the final product
link_sources = []
link_targets = []
link_values = []
link_colors = []
node_x = []
node_y = []
y_pos_dict_slots = []
node_labels = []
node_colors = []

index_of_last_node_added = 0 
first_unused_visiting_player_slot = 0
players_drawn = 0

# read a csv file with all player data and create a dictionary that maps player id to the player object
with open('all_roster_changes.csv', newline='') as csvfile:
    csvFile = csv.DictReader(csvfile)  
    for player_career_phase in csvFile:
        processed_player_career_phase = process_player_info(player_career_phase)
        player_id = processed_player_career_phase["player_id"]
        player_exists = (player_id in players_index)

        # if the player doesnt exist yet in our player_index dict, create a new player object and add it to the dict
        if not player_exists:
            new_player = Player(processed_player_career_phase)
            players_index[player_id] = new_player

        # if the player already exists in our dict, just update the existing player with the new info
        if player_exists:
            players_index[player_id].update_info(processed_player_career_phase)

if x_axis_type == "DYNAMIC":
    unique_season_and_day_list = get_teams_unique_seasons_and_days(players_index, team_to_display, index_of_last_node_added) 

# now we will loop through all players to assign the correct values to nodea of the Sankey plot
for player in players_index.values():
    if player.was_player_ever_on_team(team_to_display):
        print("doing nodes for Player:", player.get_name())
        was_ever_not_on_team = False
        # take our big node_export data bundle and break it into the parts we need to pass to Plotly
        # and append those to the long lists Plotly takes as input
        node_export = export_processed_graphing_info(player.get_career_phases(), index_of_last_node_added, selected_season_and_day)
        node_labels.extend(node_export["node_labels"])
        node_colors.extend(node_export["node_colors"])
        link_sources.extend(node_export["link_sources"])
        link_targets.extend(node_export["link_targets"])
        link_values.extend(node_export["link_values"])
        link_colors.extend(node_export["link_colors"])
        link_labels.extend(node_export["link_labels"])

        # now the more difficult problem of node positioning
        node_x_position_dictionaries = node_export["node_x_position_dictionaries"]
        x_pos_list = []  # the eventual target, all the values in here need to be a normalised co-ordinate from 0 to 1

        # for LINEAR VIEW: node position on x axis is based on season and day within season
        if x_axis_type == "LINEAR":
            for x_pos_dict in node_x_position_dictionaries:
                x_pos = round(((float(x_pos_dict.get("season")) +
                                (float(x_pos_dict.get("day")) / max_days_per_season)) /
                               (float(seasons_to_view)+0.1)), 3)
                x_pos_list.append(x_pos)
        # for DYNAMIC VIEW: node position on x axis is based on formula convert_season_day_to_x_axis
        elif x_axis_type == "DYNAMIC":
            for x_pos_dict in node_x_position_dictionaries:
                x_pos = convert_season_day_to_x_axis((x_pos_dict.get("season"), x_pos_dict.get("day")))
                x_pos_list.append(x_pos)

        node_x.extend(x_pos_list)

        # node positioning on y-axis depends in complicated fashion on the number of players being displayed,
        # also what team they are on at the time, and (for the displayed team) which position they occupy in that team
        node_y_position_dictionaries = node_export["node_y_position_dictionaries"]
        y_pos_list = []
        for y_pos_dict in node_y_position_dictionaries:
            if y_pos_dict.get("team_name") == team_to_display:
                slot_list = [int(y_pos_dict.get("position_type_id")), int(y_pos_dict.get("position_id")) + 1]
                # +1 is hack to fix a bug, Plotly does not like 0 Y values
                y_pos_dict_slots.append({"on team": True, "slot": slot_list})
            else:
                y_pos_dict_slots.append({"on team": False, "slot": first_unused_visiting_player_slot})
                was_ever_not_on_team = True

        if was_ever_not_on_team:
            first_unused_visiting_player_slot += 1
        index_of_last_node_added = node_export["new_index"]
        players_drawn += 1
    else:
        print("skipping Player:", player.get_name(), "as was never on ", team_to_display)

print("Total player careers drawn: ", players_drawn)
print("Total slots used for visiting players", first_unused_visiting_player_slot - 1)

# now we know how many players total are drawn and how many spend time outside the current team,
# we can normalise the y-values, so loop through them all to do so
lineup_positions = []
rotation_positions = []
bullpen_positions = []
bench_positions = []
for dictionary in y_pos_dict_slots:
    if dictionary["on team"]:
        if dictionary["slot"][0] == 0:
            lineup_positions.append(dictionary["slot"][1])
        if dictionary["slot"][0] == 1:
            rotation_positions.append(dictionary["slot"][1])
        if dictionary["slot"][0] == 2:
            bullpen_positions.append(dictionary["slot"][1])
        if dictionary["slot"][0] == 3:
            bench_positions.append(dictionary["slot"][1])

max_lineup = max(lineup_positions, default=0) + 2
max_rotation = max(rotation_positions, default=0) + 2
max_bullpen = max(bullpen_positions, default=0) + 2
max_bench = max(bench_positions, default=0) + 2

y_pos_list = []
un_normalised_y = 0
for dictionary in y_pos_dict_slots:
    if dictionary["on team"]:
        if dictionary["slot"][0] == 0:
            un_normalised_y = dictionary["slot"][1]
        if dictionary["slot"][0] == 1:
            un_normalised_y = max_lineup + dictionary["slot"][1]
        if dictionary["slot"][0] == 2:
            un_normalised_y = max_lineup + max_rotation + dictionary["slot"][1]
        if dictionary["slot"][0] == 3:
            un_normalised_y = max_lineup + max_rotation + max_bullpen + dictionary["slot"][1]
    else:
        un_normalised_y = max_lineup + max_rotation + max_bullpen + max_bench + dictionary["slot"]
    y_pos = round(float(un_normalised_y) / float(max_lineup +
                                                 max_rotation +
                                                 max_bullpen +
                                                 max_bench +
                                                 first_unused_visiting_player_slot), 4)
    y_pos_list.append(y_pos)
node_y.extend(y_pos_list)

event_nodes = dict(
    pad=0,
    thickness=5,
    line=dict(color="black", width=0.2),
    label=node_labels,
    color=node_colors,
    x=node_x,
    y=node_y
)
event_links = dict(
    source=link_sources,
    target=link_targets,
    value=link_values,
    color=link_colors,
    label=link_labels
)

data = go.Sankey(node=event_nodes, link=event_links, arrangement="fixed")
fig = go.Figure(data)
fig.update_layout(title_text="Slankey", font_size=10)
fig.write_html('slankey.html', auto_open=True)