"""
This script will postprocess the action sent from the RL env (might in undetermined frequency) and send the action to
the robot. In this file, we will do:

1. Receive the action from the RL env. (via a listening thread)
2. Postprocess the action, computing the velocity inertia etc, and prepare a velocity command.
3. Send the velocity command to the robot.

The usage of this file:

1. Create an instance of ActionPostprocessor.
2. Call the run() method to start the postprocessing thread.
"""
import logging
import threading


# from logger import get_logger, set_log_level
# from logger import get_logger, set_log_level

import logging
import time
from collections import deque
from dataclasses import dataclass

# from actions import RemixAction
from typing import Union, Tuple

# import config as velocity_profile_config

# logger = get_logger()

# set_log_level(logging.DEBUG)

ACTION_TOPIC = '/gogogo/high_action'

WIDTH = 1280
HEIGHT = 720

NUM_CHANNELS = 3

OBSERVATION_TOPIC = '/camera/camera/color/image_raw/compressed'
ACTION_TOPIC = '/gogogo/high_action'

WINDOW_WIDTH = 2560
WINDOW_HEIGHT = 1440
TRAFFIC_LIGHT_POS = (WINDOW_WIDTH - 150, 50)
TEXT_OFFSET = 100

HEARTBEAT_TIMEOUT = 0.5  # seconds

VELOCITY_TOPIC = '/gogogo/velocity'


@dataclass
class StepAction:
    action: Union[int, Tuple[float, float]]
    time: float

    def __repr__(self):
        return "StepAction(action={}, time={:.2f})".format(RemixAction.get_string(self.action),
                                                           -(time.time() - self.time))


@dataclass
class Velocity:
    vx: float
    vy: float
    vyaw: float
    stop: bool
    time: float

    def __repr__(self):
        return "Velocity(vx={:.2f}, vy={:.2f}, vyaw={:.2f}, stop={})".format(self.vx, self.vy, self.vyaw, self.stop)


@dataclass
class VelocityProfile:
    # Unit: m/(s^2)
    vx_decrease_rate_positive: float
    vx_decrease_rate_negative: float
    vy_decrease_rate: float
    vyaw_decrease_rate: float

    vx: float  # = 0.0
    vy: float  # = 0.0
    vyaw: float  # = 0.0

    deadzone_vx: float  # = 0.1
    deadzone_vy: float  # = 0.1
    deadzone_vyaw: float  # = 0.001

    # vx:  取值范围[-2.5~5] (m/s)； vy:  取值范围[-2.5~5] (m/s)； vyaw:  取值范围[-4~4] (rad/s)。
    # vx_max: float = 1.0
    # vx_min: float = -0.0
    # vy_max: float = 5.0
    # vy_min: float = -2.5
    # vyaw_max: float = 0.5
    # vyaw_min: float = -0.5
    vx_max: float  # = 2.0
    vx_min: float  # = 0.0
    vy_max: float  # = 5.0
    vy_min: float  # = -2.5
    vyaw_max: float  # = 4.0
    vyaw_min: float  # = -4.0

    should_run = None

    last_update_time: float = time.time()

    def update(self, dvx=None, dvy=None, dvyaw=None, vx=None, vy=None, vyaw=None, stop=False):

        # TODO: vy increase rate is not defined / used.
        assert dvy is None

        dt = time.time() - self.last_update_time

        if dt > 0.2:
            # Something wrong, just stop.
            logger.warning("[VelocityProfile.update] Something wrong, just stop. dt={}".format(dt))
            stop = True

        # If not None, then override the value.
        if stop:
            self.vx = 0.0
            self.vy = 0.0
            self.vyaw = 0.0
        else:
            if dvx is not None:
                assert vx is None
                self.vx += dvx * dt

                # print("[postprocess_action.py] dvx: ", dvx)
            if dvy is not None:
                assert vy is None
                self.vy += dvy * dt
            if dvyaw is not None:
                assert vyaw is None
                self.vyaw += dvyaw * dt
            if vx is not None:
                assert dvx is None
                self.vx = vx
            if vy is not None:
                assert dvy is None
                self.vy = vy
            if vyaw is not None:
                assert dvyaw is None
                self.vyaw = vyaw

        # Reduce the value as time goes by.
        if dvx is None and vx is None:
            if self.vx > self.deadzone_vx:
                self.vx -= self.vx_decrease_rate_positive * dt
                self.vx = max(self.vx, 0.0)
            elif self.vx < -self.deadzone_vx:
                self.vx += self.vx_decrease_rate_negative * dt
                self.vx = min(self.vx, 0.0)
            else:
                if dvx is None:
                    self.vx = 0.0

        if dvy is None and vy is None:
            if self.vy > self.deadzone_vy:
                self.vy -= self.vy_decrease_rate * dt
                self.vy = max(self.vy, 0.0)
            elif self.vy < -self.deadzone_vy:
                self.vy += self.vy_decrease_rate * dt
                self.vy = min(self.vy, 0.0)
            else:
                if dvy is None:
                    self.vy = 0.0

        if dvyaw is None and vyaw is None:
            if self.vyaw > self.deadzone_vyaw:
                self.vyaw -= self.vyaw_decrease_rate * dt
                self.vyaw = max(self.vyaw, 0.0)
            elif self.vyaw < -self.deadzone_vyaw:
                self.vyaw += self.vyaw_decrease_rate * dt
                self.vyaw = min(self.vyaw, 0.0)
            else:
                if dvyaw is None:
                    self.vyaw = 0.0

        # Limit the value.
        self.vx = max(self.vx_min, min(self.vx_max, self.vx))
        self.vy = max(self.vy_min, min(self.vy_max, self.vy))
        self.vyaw = max(self.vyaw_min, min(self.vyaw_max, self.vyaw))

        stop = stop or (self.vx == 0.0 and self.vy == 0.0 and self.vyaw == 0.0)

        self.last_update_time = time.time()
        ret = Velocity(self.vx, self.vy, self.vyaw, stop, time=self.last_update_time)
        logger.debug("[VelocityProfile.update] Velocity is updated to: {}".format(ret))
        return ret


class History(deque):
    def __init__(self, default, maxlen=20):
        super().__init__(maxlen=maxlen)
        self.default = default
        self.num_valid = 0
        self.clear()

    def append(self, data):
        super().append(data)
        self.num_valid += 1
        self.num_valid = min(self.num_valid, len(self))

    def clear(self):
        super().clear()
        self.extend([self.default] * self.maxlen)
        self.num_valid = 0

    def __repr__(self):
        return "History: [\n" + "\n".join(["\t" + str(x) for x in self]) + "\n]"


class ActionPostprocessor:
    debounce_time = 0.3  # debounce time in seconds

    in_emergency_stop = False

    state_map = None

    action_history = History(StepAction(action=0, time=time.time()), maxlen=20)
    velocity_history = History(Velocity(vx=0, vy=0, vyaw=0, stop=True, time=time.time()), maxlen=20)

    start_time = time.time()

    current_velocity = None

    running = False

    def __init__(self, config=None, debug=False, init_channel=True):
        self.key_state = {
            "R1": 0,
            "L1": 0,
            "start": 0,
            "select": 0,
            "R2": 0,
            "L2": 0,
            "F1": 0,
            "F2": 0,
            "A": 0,
            "B": 0,
            "X": 0,
            "Y": 0,
            "up": 0,
            "right": 0,
            "down": 0,
            "left": 0,
        }
        self.key_map = [
            "R1", "L1", "start", "select", "R2", "L2", "F1", "F2", "A", "B", "X", "Y", "up", "right", "down", "left"
        ]
        self.last_pressed_time = {key: 0 for key in self.key_map}

        from unitree_sdk2py.go2.obstacles_avoid.obstacles_avoid_client import ObstaclesAvoidClient
        from unitree_sdk2py.core.channel import ChannelSubscriber, ChannelFactoryInitialize
        from unitree_sdk2py.idl.unitree_go.msg.dds_ import WirelessController_
        from unitree_sdk2py.go2.sport.sport_client import SportClient

        if init_channel:
            ChannelFactoryInitialize(0)

        self.sub = ChannelSubscriber("rt/wirelesscontroller", WirelessController_)
        self.sub.Init(self.wireless_controller_handler, 10)
        self.client = SportClient()

        TIMEOUT = 0.001 if debug else 0.5
        self.debug = debug
        # self.config = config

        self.always_use_run = False

        self.client.SetTimeout(TIMEOUT)

        self.client.Init()

        print("==============================================================================")
        self.obstacle_avoid_client = ObstaclesAvoidClient()
        self.obstacle_avoid_client.SetTimeout(TIMEOUT)
        self.obstacle_avoid_client.Init()

        code, enable1 = self.obstacle_avoid_client.SwitchGet()
        if code != 0:
            logger.error("switch get error. code: {}".format(code))
        else:
            if enable1 is True:
                code = self.obstacle_avoid_client.SwitchSet(False)
                if code != 0:
                    logger.error("switch set error. code:", code)
                else:
                    print("switch set success.")
                time.sleep(3)
                print("Turning off obstacle avoidance")
            else:
                print("Obstacle avoidance is already off")
        print("==============================================================================")

        self.logger = logger
        self.logger.log(logging.INFO, "UnitreeMiddleware initialized. We will hijack the joystick now.")

        # All units are in international unit. m/s, m/s2, rad/s, rad/s2 etc.

        # if self.config.use_continuous_action_space:
        vx_decrease_rate_positive = 1.0
        vx_decrease_rate_negative = 1.0
        # else:
        #     vx_decrease_rate_positive = self.config.action.vx_decrease_rate_positive
        #     vx_decrease_rate_negative = self.config.action.vx_decrease_rate_negative

        deadzone_vx = 0.1
        deadzone_vy = 0.1
        deadzone_vyaw = 0.001

        # self.velocity_profile = VelocityProfile(
        #     vx_decrease_rate_positive=vx_decrease_rate_positive,
        #     vx_decrease_rate_negative=vx_decrease_rate_negative,
        #     # vy_decrease_rate=self.config.action.vy_decrease_rate,  # Useless
        #     # vyaw_decrease_rate=self.config.action.vyaw_decrease_rate,
        #     vx=0.0,
        #     vy=0.0,
        #     vyaw=0.0,
        #     deadzone_vx=deadzone_vx,
        #     deadzone_vy=deadzone_vy,
        #     deadzone_vyaw=deadzone_vyaw,
        #     vx_max=self.config.action.vx_max,
        #     vx_min=self.config.action.vx_min,
        #     vy_max=self.config.action.vy_max,
        #     vy_min=self.config.action.vy_min,
        #     vyaw_max=self.config.action.vyaw_max,
        #     vyaw_min=self.config.action.vyaw_min
        # )
        # self.vx_increase_rate_positive = self.config.vx_increase_rate_positive  # velocity increment when you push forward
        # self.vx_increase_rate_negative = self.config.vx_increase_rate_negative
        # self.vyaw_increase_rate = self.config.vyaw_increase_rate
        # self.run_velocity_threshold = self.config.run_velocity_threshold
        # self.run_time_threshold = self.config.run_time_threshold

        self.stop_event = threading.Event()  # Event to signal stopping

    def update_key_state(self, keys):
        for i in range(16):
            self.key_state[self.key_map[i]] = (keys & (1 << i)) >> i

    def is_key_pressed(self, key):
        return self.key_state.get(key, 0) == 1

    def debounce(self, key):
        current_time = time.time()
        if current_time - self.last_pressed_time[key] > self.debounce_time:
            self.last_pressed_time[key] = current_time
            return True
        return False

    def wireless_controller_handler(self, msg):
        self.update_key_state(msg.keys)

        pressed_keys = [key for key, state in self.key_state.items() if state == 1]
        if pressed_keys:
            self.logger.log(logging.DEBUG, "Keys pressed: {}".format(pressed_keys))

        if self.is_key_pressed("L2") and self.is_key_pressed("B"):
            self.emergency_stop()

        # if self.is_key_pressed("L2") and self.is_key_pressed("A"):
        #     self.resume()

        # if self.is_key_pressed("start") and self.debounce("start"):
        #     self.toggle_joystick(allow_joystick_control=None)

        if self.is_key_pressed("down") and self.debounce("down"):
            self.print_robot_state()

    def update_robot_state(self):
        state_keys = [
            "state", "bodyHeight", "footRaiseHeight", "speedLevel",
            "gait", "joystick", "dance", "continuousGait", "economicGait"
        ]

        if self.debug:
            self.state_code = 0
            self.state_map = {
                "state": "locomotion",
                "bodyHeight": 0.0,
                "footRaiseHeight": 0.0,
                "speedLevel": 0,
                "gait": "walk",
                "joystick": "normal",
                "dance": "none",
                "continuousGait": "none",
                "economicGait": "none"
            }
            return

        code, state_map = self.client.GetState(state_keys)

        self.state_code = code
        if self.state_code == 0 and state_map is not None:
            self.state_map = state_map
            for key, value in self.state_map.items():
                value = eval(value)["data"]
                self.state_map[key] = value

    def print_robot_state(self):
        if self.state_code == 0 and self.state_map is not None:
            self.state_map = {k: self.state_map[k] for k in sorted(self.state_map.keys())}
            print("Current Robot State:")
            for key, value in self.state_map.items():
                print(f"  {key}: {value}")
        else:
            print("Failed to get robot state. Error code:", self.state_code)

    def emergency_stop(self):
        if self.in_emergency_stop:
            return
        self.logger.warning("[L2 + B] Emergency stop is executing...")
        self.client.Damp()
        self.in_emergency_stop = True
        time.sleep(self.debounce_time)
        self.logger.info("[L2 + B] Emergency stop activated. Press [L2 + A] to resume.")

    def action_callback(self, action):
        """
        This function should be called explicitly by the RL env.
        """
        logger.debug("[action_callback] Safety Layer: Received action: {}".format(RemixAction.get_string(action)))
        self.action_history.append(StepAction(action=action, time=time.time()))

    def run(self):
        try:
            while True:
                action_postprocessor_tick_interval = 0.02

                time.sleep(action_postprocessor_tick_interval)  # Run in 50HZ
                self.update_robot_state()
                self.tick()
        finally:
            self.close()

    # def update_velocity_profile(self):
    #     if self.action_history[-1].action == RemixAction.ACTION_STOP:
    #         vel = self.velocity_profile.update(stop=True)
    #
    #     elif self.action_history[-1].action == RemixAction.ACTION_FORWARD:
    #
    #         if self.velocity_profile.vx > 0:
    #             vel = self.velocity_profile.update(dvx=self.config.forward_vx_increase_rate_when_positive)
    #         else:
    #             vel = self.velocity_profile.update(dvx=self.config.forward_vx_increase_rate_when_negative)
    #
    #     elif self.action_history[-1].action == RemixAction.ACTION_BACKWARD:
    #         if self.velocity_profile.vx > 0:
    #             vel = self.velocity_profile.update(dvx=-self.config.backward_vx_decrease_rate_when_positive)
    #         else:
    #             vel = self.velocity_profile.update(dvx=-self.config.backward_vx_decrease_rate_when_negative)
    #
    #     elif self.action_history[-1].action == RemixAction.ACTION_NEUTRAL:
    #         vel = self.velocity_profile.update()
    #
    #     elif self.action_history[-1].action == RemixAction.ACTION_LEFT:
    #
    #         if self.velocity_profile.vyaw > 0:
    #             vel = self.velocity_profile.update(dvyaw=self.config.vyaw_increase_rate)
    #         else:
    #             vel = self.velocity_profile.update(dvyaw=self.config.reverse_vyaw_decrease_rate)
    #
    #     elif self.action_history[-1].action == RemixAction.ACTION_RIGHT:
    #
    #         if self.velocity_profile.vyaw > 0:
    #             vel = self.velocity_profile.update(dvyaw=-self.config.reverse_vyaw_decrease_rate)
    #         else:
    #             vel = self.velocity_profile.update(dvyaw=-self.config.vyaw_increase_rate)
    #
    #     elif self.action_history[-1].action == RemixAction.ACTION_LOOK_DOWN:
    #         vel = self.velocity_profile.update(stop=True)
    #
    #     else:
    #         raise ValueError("Invalid action: ", self.action_history[-1].action)
    #
    #     return vel

    def tick(self):

        t = time.time()

        logger.debug("[Tick] {:.2f}s Enter tick. Current history: {}".format(
            t - self.start_time, self.action_history)
        )

        if not self.running:
            # self.action_history.clear()
            return

        # if t > self.action_history[-1].time and (t - self.action_history[-1].time) > 0.2:
        #     # Something wrong, clear the action sequence
        #     self.execute_stop()
        #
        #     if not self.debug:
        #         logger.warning("[Tick] {:.2f}s No action received since past {:.2f}s. Clear action history.".format(
        #             t - self.start_time, t - self.action_history[-1].time)
        #         )
        #
        #     self.action_history.clear()

        # if len(self.action_history) == 0:
        #     return

        # Update current velocity profile.
        # vel = self.update_velocity_profile()

        # Save velocity
        # self.velocity_history.append(vel)

        # Execute the velocity profile.
        # should_run = self.should_run()
        # vel.should_run = should_run

        # self.current_velocity = vel

        logger.debug("Sending velocity profile: {}".format(vel))

        if vel.stop:
            self.execute_stop()

        else:
            # if should_run:
            #     self.execute_run_velocity(vel)
            # else:
                # When not ready to run, do walk first.
            self.execute_walk_velocity(vel)

        # One more action to do:
        if self.action_history[-1].action == RemixAction.ACTION_LOOK_DOWN:
            self.execute_look_down()

    # def should_run(self):
    #     # Read the velocity sequence as see if you are ready to run.
    #     if not self.velocity_history:
    #         return False
    #
    #     if self.always_use_run:
    #         return True
    #
    #     t = time.time()
    #     accumulated_time = 0.0
    #     for v in reversed(self.velocity_history):
    #         dt = t - v.time
    #         accumulated_time += dt
    #         if v.vx > self.config.action.run_velocity_threshold:
    #             # good, the targeted speed is good.
    #             # TODO: Maybe we should use real robot velocity instead of the speed command history here.
    #             pass
    #         else:
    #             return False
    #         if accumulated_time > self.config.action.run_time_threshold:
    #             break
    #
    #     return True

    def execute_stop(self):
        if self.debug:
            return

        if self.always_use_run:
            ret = self.client.Euler(0, 0.0, 0)
            if ret != 0:
                logger.error("[stop_move] Failed to set euler")

            ret = self.client.BodyHeight(0.0)
            if ret != 0:
                logger.error("[stop_move] Failed to set body height")

            ret = self.client.StopMove()
            if ret != 0:
                logger.error("[stop_move] Failed to stop move")

        elif self.state_map is None or self.state_map["gait"] != "walk":
            ret = self.switch_gait(1)

        else:
            ret = self.client.Euler(0, 0.0, 0)
            if ret != 0:
                logger.error("[stop_move] Failed to set euler")

            ret = self.client.BodyHeight(0.0)
            if ret != 0:
                logger.error("[stop_move] Failed to set body height")

            ret = self.client.StopMove()
            if ret != 0:
                logger.error("[stop_move] Failed to stop move")

    def execute_walk_velocity(self, vel: Velocity):
        if self.debug:
            return

        if self.state_map is None or self.state_map["gait"] != "walk":
            self.switch_gait(1)
            logger.info("[execute_walk_velocity] Not in walk state, switch to walk state. Current state: {}".format(
                self.state_map))
        else:
            self.move(vel.vx, vel.vy, vel.vyaw)
            logger.debug(
                "[execute_walk_velocity] vx: {:.2f}, vy: {:.2f}, vyaw: {:.2f}".format(vel.vx, vel.vy, vel.vyaw))

    def execute_run_velocity(self, vel: Velocity):
        if self.debug:
            return

        if self.state_map is None or self.state_map["gait"] != "run":
            self.switch_gait(2)
            logger.info("[execute_run_velocity] Not in run state, switch to run state. Current state: {}".format(
                self.state_map))
        else:
            self.move(vel.vx, vel.vy, vel.vyaw)
            logger.debug("[execute_run_velocity] vx: {:.2f}, vy: {:.2f}, vyaw: {:.2f}".format(vel.vx, vel.vy, vel.vyaw))

    def execute_look_down(self):
        if self.debug:
            return

        # roll:  取值范围  [-0.75~0.75] (rad)； pitch:  取值范围  [-0.75~0.75] (rad)； yaw:  取值范围  [-0.6~0.6] (rad)。
        if self.state_map is not None and self.state_map["state"] != "locomotion":
            self.client.Euler(0, 0.75, 0)
            self.client.BodyHeight(-0.07)
            # self.client.Wallow()
            # self.client.Pose(True)
            # self.client.FrontFlip()
            # self.client.FrontPounce()
            # self.client.Dance1()
            # self.client.Dance2()
            # self.client.Scrape()
            # self.client.Hello()

        else:
            self.execute_stop()
            logger.debug(
                "[execute_look_down] Not in locomotion state, switch to other state. State: {}".format(self.state_map))

    def switch_gait(self, gait):
        if self.debug:
            return

        ret = self.client.SwitchGait(gait)
        if ret != 0:
            logger.warning("Failed to switch gait to: {}".format(gait))

    def balance_stand(self):
        if self.debug:
            return

        ret = self.client.BalanceStand()
        if ret != 0:
            logger.warning("Failed to balance stand")

    def move(self, x, y, z):
        if self.debug:
            return
        ret = self.client.Move(x, y, z)
        if ret != 0:
            logger.warning("Failed to move")

    def close(self):
        # self.toggle_joystick(allow_joystick_control=True)
        # self.resume()
        self.sub.Close()
        self.logger.info("UnitreeMiddleware shutdown complete.")



if __name__ == '__main__':
    action_postprocessor = ActionPostprocessor()

    action_postprocessor.run()

    # logger.info("Starting action postprocessor thread.")
    # self.action_postprocessor_thread = threading.Thread(target=action_postprocessor.run, daemon=True)
    # self.action_postprocessor_thread.start()