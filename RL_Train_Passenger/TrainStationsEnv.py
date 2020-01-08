import numpy as np
import gym
from gym import spaces

from utils.wmata_static import get_line_paths, get_station_codes

letter_lookup = ['a','b','c','d','e','f','g','h','i','j','k','l',
                 'm','n','o','p','q','r','s','t','u','v','w','x','y','z']
lines = ["Blue", "Green", "Orange", "Red", "Silver", "Yellow"]

class TrainStationsENV():
    """Custom Environment that follows gym interface"""

    def __init__(self):
        # Define action and observation space
        # They must be gym.spaces objects
        # Example when using discrete actions:
        self.curr_station = self.target_station = self.state = None
        self.steps = 0
        self.action_space = spaces.Discrete(12)
        self.time_limit = 30
        self.paths = get_line_paths()
        self.stations = get_station_codes()
        # Example for using image as input:
        #self.observation_space = spaces.Box(low=-1, high=1, dtype=np.uint8)

    def take_action(self, action):
        act_line = np.floor(action/2)
        right = action % 2 == 0
        for ix, (line, path) in enumerate(self.paths.items()):
            if ix != act_line:
                continue

            for iy, station in enumerate(path):
                if station.get('StationCode') == self.curr_station:
                    if right:
                        self.set_current_station(path[iy - 1])
                    else:
                        self.set_current_station(path[iy + 1])

                    break
            break


    def step(self, action):
        done = False
        info = None
        available_dirs = self.get_available_directions()
        if available_dirs[action] == 1:
            self.take_action(action)
            avail_dirs = self.get_available_directions()
            curr_stat = self.convert_station_code(self.curr_station)
            target_stat = self.convert_station_code(self.target_station)
            self.state = np.array([curr_stat, target_stat] + avail_dirs)

            if self.curr_station == self.target_station:
                reward = 30 + (self.time_limit - self.steps)
                done = True
            else:
                reward = 1


        else:
            reward = -1

        self.steps += 1
        if self.steps > self.time_limit:
            done = True

        return self.state, reward, done, info

    def get_available_directions(self):
        available_dirs = []
        for line, path in self.paths.items():
            station_found = False
            for ix, station in enumerate(path):
                if station['StationCode'] == self.curr_station:
                    station_found = True
                    if ix > 0:
                        available_dirs.append(1)
                    else:
                        available_dirs.append(-1)
                    if ix < len(path) - 1:
                        available_dirs.append(1)
                    else:
                        available_dirs.append(-1)
                    break

            if not station_found:
                available_dirs.extend([-1, -1])
        return available_dirs

    def convert_station_code(self, station_code):
        letter = station_code[0].lower()
        letter_num = letter_lookup.index(letter)
        new_code = f'{letter_num}{station_code[1:]}'
        return int(new_code)/100


    def set_current_station(self, station):
        self.curr_station = station.get('StationCode')
        self.curr_station_name = station.get('StationName')

    def reset(self):
        self.set_current_station(np.random.choice(self.stations, 1)[0])
        target_station = np.random.choice(self.stations, 1)[0]
        self.target_station = target_station.get('StationCode')
        self.target_station_name = target_station.get('StationName')

        avail_dirs = self.get_available_directions()
        curr_stat = self.convert_station_code(self.curr_station)
        target_stat = self.convert_station_code(self.target_station)
        self.state = np.array([curr_stat, target_stat] + avail_dirs)
        self.steps = 0

        return self.state  # reward, done, info can't be included

    def render(self, mode='human'):
        pass

    def close(self):
        pass

if __name__ == "__main__":
    tracks = TrainStationsENV()
    tracks.reset()
    tracks.step(1)
    print("Finished")