import plotly.graph_objects as go
import csv


class PlayerCareer:

    def __init__(self, player_id, player_name, career_phase):
        self.__player_id = player_id
        self.__player_name = player_name
        self.__player_team_names = [career_phase["nickname"]]
        self.__career_phases = [career_phase]

    def append_career_phase(self, career_phase):
        self.__career_phases.append(career_phase)
        self.__player_team_names.append(career_phase["nickname"])

    def get_player_name(self):
        return self.__player_name

    def was_player_ever_on_team(self, team_searched):
        return team_searched in self.__player_team_names

    @staticmethod
    def node_x_and_labels_method(_is_first, __current_career_phase):
        _label = ''

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
                                      "day": int(_season_and_day[2])}
        else:
            _x_position_dictionary = {"season": int(_season_and_day[0]),
                                      "day": int(_season_and_day[2]) - 1}
        if _is_first:
            _label = __current_career_phase["player_name"] + " S" + str(int(_season_and_day[0]) + 1) + "D" + str(
                int(_season_and_day[2]) + 1)
        else:
            _label = ""
        return _x_position_dictionary, _label

    def export_nodes(self, _index_of_last_node_added, _current_season_and_day):
        _node_labels = []
        _node_x_position_dictionaries = []
        _node_y_position_dictionaries = []
        _node_colors = []
        _link_sources = []
        _link_targets = []
        _link_values = []
        _i = 0
        _phase_count = 0
        _new_index = 0
        for __current_career_phase in self.__career_phases:
            _phase_count += 1
            # each career phase is a pair of nodes (start and end) with a link between,
            # a span where they were on one team
            _color = __current_career_phase["team_main_color"]
            _y_position_dictionary = {"team_name": __current_career_phase["nickname"],
                                      "position_type_id": __current_career_phase["position_type_id"],
                                      "position_id": __current_career_phase["position_id"]}

            # first node
            _x_position_dictionary, _label = self.node_x_and_labels_method(True, __current_career_phase)
            _node_labels.append(_label)
            _node_x_position_dictionaries.append(_x_position_dictionary)
            _node_y_position_dictionaries.append(_y_position_dictionary)
            _node_colors.append(_color)

            # second node
            _x_position_dictionary, _label = self.node_x_and_labels_method(False, __current_career_phase)
            _node_labels.append(_label)
            _node_x_position_dictionaries.append(_x_position_dictionary)
            _node_y_position_dictionaries.append(_y_position_dictionary)
            _node_colors.append(_color)

        while _i < len(_node_labels)-1:
            _link_sources.append(_i + _index_of_last_node_added)
            _link_targets.append(_i + _index_of_last_node_added + 1)
            _link_values.append(1)
            _i += 1

        _new_index = _index_of_last_node_added + len(_node_labels)

        return {"node_labels": _node_labels,
                "link_sources": _link_sources,
                "link_targets": _link_targets,
                "link_values": _link_values,
                "node_x_position_dictionaries": _node_x_position_dictionaries,
                "node_y_position_dictionaries": _node_y_position_dictionaries,
                "node_colors": _node_colors,
                "new_index": _new_index}


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
            this_career = PlayerCareer(row["player_id"], row["player_name"], row)
            # store a reference to the new PlayerCareer object in a dictionary
            players_index.append(
                {"player_id": row["player_id"], "player_name": row["player_name"], "player_career": this_career})

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
team_to_display = "Millennials"
current_season_and_day = ['13', '', '120', '']


for player in players_index:
    career = player["player_career"]
    if career.was_player_ever_on_team(team_to_display):
        print("doing nodes for Player:", career.get_player_name())
        was_ever_not_on_team = False
        # take our big node_export data bundle and break it into the parts we need to pass to Plotly
        # and append those to the long lists Plotly takes as input
        node_export = career.export_nodes(index_of_last_node_added, current_season_and_day)
        node_labels.extend(node_export["node_labels"])
        node_colors.extend(node_export["node_colors"])
        link_sources.extend(node_export["link_sources"])
        link_targets.extend(node_export["link_targets"])
        link_values.extend(node_export["link_values"])

        # now the more difficult problem of node positioning
        # node position on x axis is based on season and day within season
        node_x_position_dictionaries = node_export["node_x_position_dictionaries"]
        x_pos_list = []
        for x_pos_dict in node_x_position_dictionaries:
            x_pos = round(((float(x_pos_dict["season"]) + (float(x_pos_dict["day"]) / max_days_per_season)) / (float(seasons_to_view)+0.1)), 3)
            x_pos_list.append(x_pos)
        node_x.extend(x_pos_list)

        # node positioning on y-axis depends in complicated fashion on the number of players being displayed,
        # also what team they are on at the time, and (for the displayed team) which position they occupy in that team
        node_y_position_dictionaries = node_export["node_y_position_dictionaries"]
        y_pos_list = []
        for y_pos_dict in node_y_position_dictionaries:
            if y_pos_dict["team_name"] == team_to_display:
                slot_list = [int(y_pos_dict["position_type_id"]), int(y_pos_dict["position_id"]) + 1]   # +1 is hack to fix a bug, Plotly does not like 0 Y values
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
    value=link_values
)

data = go.Sankey(node=event_nodes, link=event_links, arrangement="fixed")
fig = go.Figure(data)
fig.update_layout(title_text="Slankey", font_size=10)
fig.write_html('slankey.html', auto_open=True)
