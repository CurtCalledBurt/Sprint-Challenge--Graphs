from room import Room
from player import Player
from world import World

import random
from ast import literal_eval

# Load world
world = World()


# You may uncomment the smaller graphs for development and testing purposes.
# map_file = "maps/test_line.txt"
# map_file = "maps/test_cross.txt"
# map_file = "maps/test_loop.txt"
# map_file = "maps/test_loop_fork.txt"
map_file = "maps/main_maze.txt"

# Loads the map into a dictionary
room_graph=literal_eval(open(map_file, "r").read())
world.load_graph(room_graph)

# Print an ASCII map
world.print_rooms()

player = Player(world.starting_room)

# Fill this out with directions to walk
# traversal_path = ['n', 'n']
traversal_path = []
traversal_graph = {}

def get_opposite_direction(direction):
    # return the direction opposite to the one we enter, and None if we enter an invalid direction
    direction_to_prev = None
    if direction == 'n':
        direction_to_prev = 's'
    elif direction == 's':
        direction_to_prev = 'n'
    elif direction == 'e':
        direction_to_prev = 'w'
    elif direction == 'w':
        direction_to_prev = 'e'
    return direction_to_prev

# # add starting room to traversal_graph
exits = player.current_room.get_exits()
graph_node = {}
for exit in exits:
    graph_node[exit] = "?"
traversal_graph[player.current_room.id] = graph_node

# # main loop
while len(traversal_graph) < len(room_graph):

    # move to an unexplored room if there is an unexplored room
    unexplored_exits = [x for x in traversal_graph[player.current_room.id].keys() if traversal_graph[player.current_room.id][x] == "?"]
    if len(unexplored_exits) > 0:
        # choose a random exit direction from available exit directions
        direction = random.choice(unexplored_exits)
        # save previous room
        previous_room = player.current_room
        # move to new room
        player.travel(direction)
        # update traversal path
        traversal_path.append(direction)

    # if we've hit the end of a cycle, or dead end, bfs until we find the closest room with unexlpored neighbors
    else: 
        # create queue
        q = []
        # save first element to queue
        q.append((player.current_room, []))
        found = False
        while not found:
            node = q.pop(0)
            # get current room object
            room = node[0]
            # get path to this room from where we currently are
            direction_path = node[1].copy()
            # get all exits out of this room
            exits = room.get_exits()

            ##### not necessary for a solution, but speeds up the process considerably most of the time

            # remove the exit that leads to the room we just came from
            if len(direction_path) > 0:
                # get our most recent move
                previous_direction = direction_path[-1]
                # the reverse of that direction is where we came from, so don't go that way
                direction_of_previous_room = get_opposite_direction(previous_direction)
                # remove the unwanted direction from possible exits
                exits.remove(direction_of_previous_room)
            
            ##### -------------------------------------------------------------

            # add rooms at exits to queue, append direction to that room to direction_path
            for exit in exits:
                # get the direction path to the current room
                direction_path_copy = direction_path.copy()
                # get the room in the current exit direction
                new_room = room.get_room_in_direction(exit)
                # append the direction to this new room to our direction path
                direction_path_copy.append(exit) 
                # enqueue the new_room with its direction path
                q.append((new_room, direction_path_copy))
            # check if any exits are '?' 
            # if there are, end loop
            if '?' in traversal_graph[room.id].values():
                # end the while loop
                found = True
                # move player to the room with the '?' neighbor
                for direction in direction_path:
                    # update previous room
                    previous_room = player.current_room
                    # travel to new room
                    player.travel(direction)
                    # append the travel direction to the traversal path
                    traversal_path.append(direction)

    # add new room to traversal graph if it isn't already there
    if player.current_room.id not in traversal_graph.keys():
        # get's the list of exits
        exits = player.current_room.get_exits()
        # creates an empty graph node
        graph_node = {}
        for exit in exits:
            # populates graph node with '?'
            graph_node[exit] = "?"
        # keys the graph node to the current room's id
        traversal_graph[player.current_room.id] = graph_node
    
    # update traversal_graph with info on old room and new room if new room and old room are different
    if player.current_room.id != previous_room.id:
        # update the previous room
        traversal_graph[previous_room.id][direction] = player.current_room.id
        # update current room
        direction_to_prev = get_opposite_direction(direction)
        traversal_graph[player.current_room.id][direction_to_prev] = previous_room.id

        # if any rooms are connected to our current room that we've already explored, add them too
        for direction in player.current_room.get_exits():
            # check room in current exit direction
            room_in_direction = player.current_room.get_room_in_direction(direction)
            # if statement checks if we've been here before, if we have ...
            if room_in_direction.id in traversal_graph.keys():
                # update traversal_graph node of current room
                traversal_graph[player.current_room.id][direction] = room_in_direction.id
                # get opposite direction
                direction_to_prev = get_opposite_direction(direction)
                # update traversal_graph node of known room next to the current room
                traversal_graph[room_in_direction.id][direction_to_prev]


# TRAVERSAL TEST
visited_rooms = set()
player.current_room = world.starting_room
visited_rooms.add(player.current_room)

for move in traversal_path:
    player.travel(move)
    visited_rooms.add(player.current_room)

if len(visited_rooms) == len(room_graph):
    print(f"TESTS PASSED: {len(traversal_path)} moves, {len(visited_rooms)} rooms visited")
else:
    print("TESTS FAILED: INCOMPLETE TRAVERSAL")
    print(f"{len(room_graph) - len(visited_rooms)} unvisited rooms")


#######
# UNCOMMENT TO WALK AROUND
#######
# player.current_room.print_room_description(player)
# while True:
#     cmds = input("-> ").lower().split(" ")
#     if cmds[0] in ["n", "s", "e", "w"]:
#         player.travel(cmds[0], True)
#     elif cmds[0] == "q":
#         break
#     else:
#         print("I did not understand that command.")
