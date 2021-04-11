import plotly.graph_objects as go
import csv
from operator import itemgetter

class PlayerCareer:
    def __init__(self, career_phase):
        self.__player_id = career_phase["player_id"]
        self.__player_name = career_phase["player_name"]
        self.__player_team_names = [career_phase["nickname"]]
        self.__career_phases = [career_phase]

    def get_player_id(self):
        return self.__player_id

    def get_player_name(self):
        return self.__player_name

    def get_career_phases(self):
        return self.__career_phases

    def was_player_ever_on_team(self, team_searched):
        return team_searched in self.__player_team_names

    def append_career_phase(self, career_phase):
        self.__career_phases.append(career_phase)
        self.__player_team_names.append(career_phase["nickname"])

# TODO: refactor out the code that cleans the data so this function only generates the objects and labels
def create_x_axis_nodes_and_labels(_is_first, __current_career_phase):
        _label = ''
        _team = __current_career_phase["nickname"]

        if _is_first:
            _season_and_day = __current_career_phase["gamephase_from_timestamp"].strip("()").split(",")
        else:
            _season_and_day = __current_career_phase["gamephase_from_timestamp-2"].strip("()").split(",")

        if _season_and_day == ['NULL']:
            _season_and_day = current_season_and_day
        if _season_and_day[2] == '':
            if _season_and_day[3] == 'PRESEASON':
                _season_and_day[2] = '0'
            if _season_and_day[3] == 'EARLY_SIESTA':
                _season_and_day[2] = '27'
            if _season_and_day[3] == 'LATE_SIESTA':
                _season_and_day[2] = '72'
            if _season_and_day[3] == 'END_REGULAR_SEASON':
                _season_and_day[2] = '99'
            if _season_and_day[3] == 'END_POSTSEASON':
                _season_and_day[2] = '125'
            if _season_and_day[3] == 'BOSS_FIGHT':
                _season_and_day[2] = '130'
            if _season_and_day[3] == 'ELECTIONS' or _season_and_day[3] == 'ELECTION_RESULTS':
                _season_and_day[2] = '135'
        if _is_first:
            _x_position_dictionary = {"season": int(_season_and_day[0]),
                                      "day": int(_season_and_day[2]),
                                      "team": _team}
        else:
            _x_position_dictionary = {"season": int(_season_and_day[0]),
                                      "day": int(_season_and_day[2]) - 1,
                                      "team": _team}
        if _is_first:
            _label = __current_career_phase["player_name"] + " S" + str(int(_season_and_day[0]) + 1) + "D" + str(
                int(_season_and_day[2]) + 1)
        else:
            _label = ""
        return _x_position_dictionary, _label

# TODO: comment explaining what each of these returned objects do
def export_processed_graphing_info(__career_phases, _index_of_last_node_added, _current_season_and_day):
    _node_labels = []
    _node_x_position_dictionaries = []
    _node_y_position_dictionaries = []
    _node_colors = []
    _link_sources = []
    _link_targets = []
    _link_values = []
    _link_colors = []
    _phase_count = 0
    _new_index = 0
    for __current_career_phase in __career_phases:

        # each career phase is a pair of nodes (start and end) with a link between,
        # a span where they were on one team
        _color = __current_career_phase["team_main_color"]
        _color2 = __current_career_phase["team_secondary_color"]
        _y_position_dictionary = {"team_name": __current_career_phase["nickname"],
                                    "position_type_id": __current_career_phase["position_type_id"],
                                    "position_id": __current_career_phase["position_id"]}

        # first node
        _x_position_dictionary, _label = create_x_axis_nodes_and_labels(True, __current_career_phase)
        _node_labels.append(_label)
        _node_x_position_dictionaries.append(_x_position_dictionary)
        _node_y_position_dictionaries.append(_y_position_dictionary)
        _node_colors.append(_color)
        _link_sources.append((2*_phase_count) + _index_of_last_node_added)
        _link_targets.append((2*_phase_count) + _index_of_last_node_added + 1)
        _link_values.append(1)
        _link_colors.append(_color2)

        # second node
        _x_position_dictionary, _label = create_x_axis_nodes_and_labels(False, __current_career_phase)
        _node_labels.append(_label)
        _node_x_position_dictionaries.append(_x_position_dictionary)
        _node_y_position_dictionaries.append(_y_position_dictionary)
        _node_colors.append(_color)
        # if this is the last node in the players career, don't add a link to the next node
        if (_phase_count + 1) < len(__career_phases):
            _link_sources.append((2*_phase_count) + _index_of_last_node_added + 1)
            _link_targets.append((2*_phase_count) + _index_of_last_node_added + 2)
            _link_values.append(1)
            _link_colors.append(_color2)
        _phase_count += 1
    _new_index = _index_of_last_node_added + len(_node_labels)

    return {"node_labels": _node_labels,
            "link_sources": _link_sources,
            "link_targets": _link_targets,
            "link_values": _link_values,
            "link_colors": _link_colors,
            "node_x_position_dictionaries": _node_x_position_dictionaries,
            "node_y_position_dictionaries": _node_y_position_dictionaries,
            "node_colors": _node_colors,
            "new_index": _new_index}

# TODO: redo the logic on same vs different player in case sometimes the same player isnt all grouped together (key is playerId)
with open('all_roster_changes.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)  # create a dictionary with all the data in it by reading in the CSV file

    # loop through the CSV, and for each player,
    # pick out each career phase in chronological order and assign it to a PlayerCareer object

    players_index = []
    previous_entry_player_id = ""
    same_player = False
    player_count = 0
    for row in reader:
        same_player = (row["player_id"] == previous_entry_player_id)
        if not same_player:
            # Create a new PlayerCareer object
            this_career = PlayerCareer(row)
            # store a reference to the new PlayerCareer object in an array
            players_index.append(this_career)

        if same_player:
            this_career.append_career_phase(row)
        previous_entry_player_id = row["player_id"]

# construct ginormous arrays to pass to Plotly's Sankey method

node_labels = []
node_x = []
y_pos_dict_slots = []
node_y = []
node_colors = []
link_sources = []
link_targets = []
link_values = []
link_colors = []
index_of_last_node_added = 0
first_unused_visiting_player_slot = 0
players_drawn = 0
seasons_to_view = 14
max_days_per_season = 135
team_to_display = "Firefighters"
current_season_and_day = ['13', '', '120', '']
x_axis_type = "DYNAMIC"   # current options are "LINEAR" and "DYNAMIC"
unique_season_and_day_list = []

# first we will loop through all players to determine how many x-axis slots are required for the dynamic view
for career in players_index:
    if career.was_player_ever_on_team(team_to_display):
        node_export = export_processed_graphing_info(career.get_career_phases(), index_of_last_node_added, current_season_and_day)
        node_x_position_dictionaries = node_export["node_x_position_dictionaries"]
        for node_dictionary in node_x_position_dictionaries:
            season_and_day = [node_dictionary.get("season"), node_dictionary.get("day")]
            if season_and_day in unique_season_and_day_list:
                pass
            else:
                unique_season_and_day_list.append(season_and_day)
    else:
        pass

number_of_x_axis_slots = len(unique_season_and_day_list)
unique_season_and_day_list.sort(key=itemgetter(0, 1))

# now we will loop through all players to assign the correct values to nodea of the Sankey plot
for career in players_index:
    if career.was_player_ever_on_team(team_to_display):
        print("doing nodes for Player:", career.get_player_name())
        was_ever_not_on_team = False
        # take our big node_export data bundle and break it into the parts we need to pass to Plotly
        # and append those to the long lists Plotly takes as input
        node_export = export_processed_graphing_info(career.get_career_phases(), index_of_last_node_added, current_season_and_day)
        node_labels.extend(node_export["node_labels"])
        node_colors.extend(node_export["node_colors"])
        link_sources.extend(node_export["link_sources"])
        link_targets.extend(node_export["link_targets"])
        link_values.extend(node_export["link_values"])
        link_colors.extend(node_export["link_colors"])

        # now the more difficult problem of node positioning
        node_x_position_dictionaries = node_export["node_x_position_dictionaries"]
        x_pos_list = []  # the eventual target, all the values in here need to be a normalised co-ordinate from 0 to 1

        # for LINEAR VIEW: node position on x axis is based on season and day within season
        if x_axis_type == "LINEAR":
            for x_pos_dict in node_x_position_dictionaries:
                x_pos = round(((float(x_pos_dict.get("season")) + (float(x_pos_dict.get("day")) / max_days_per_season)) / (float(seasons_to_view)+0.1)), 3)
                x_pos_list.append(x_pos)
        # for DYNAMIC VIEW: node position on x axis is based on unique season,day slot and number of those slots
        elif x_axis_type == "DYNAMIC":
            for node_dictionary in node_x_position_dictionaries:
                i = 1
                for x_axis_slot in unique_season_and_day_list:
                    if [node_dictionary.get("season"), node_dictionary.get("day")] == x_axis_slot:
                        x_pos_list.append(round((i / number_of_x_axis_slots), 2))
                        break
                    else:
                        i += 1

        node_x.extend(x_pos_list)

        # node positioning on y-axis depends in complicated fashion on the number of players being displayed,
        # also what team they are on at the time, and (for the displayed team) which position they occupy in that team
        node_y_position_dictionaries = node_export["node_y_position_dictionaries"]
        y_pos_list = []
        for y_pos_dict in node_y_position_dictionaries:
            if y_pos_dict.get("team_name") == team_to_display:
                slot_list = [int(y_pos_dict.get("position_type_id")), int(y_pos_dict.get("position_id")) + 1]   # +1 is hack to fix a bug, Plotly does not like 0 Y values
                y_pos_dict_slots.append({"on team": True, "slot": slot_list})
            else:
                y_pos_dict_slots.append({"on team": False, "slot": first_unused_visiting_player_slot})
                was_ever_not_on_team = True

        if was_ever_not_on_team:
            first_unused_visiting_player_slot += 1
        index_of_last_node_added = node_export["new_index"]
        players_drawn += 1
    else:
        print("skipping Player:", career.get_player_name(), "as was never on ", team_to_display)

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
    y_pos = round(float(un_normalised_y) / float(max_lineup + max_rotation + max_bullpen + max_bench + first_unused_visiting_player_slot), 4)
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
)

data = go.Sankey(node=event_nodes, link=event_links, arrangement="fixed")
fig = go.Figure(data)
fig.update_layout(title_text="Slankey", font_size=10)
fig.write_html('slankey.html', auto_open=True)
