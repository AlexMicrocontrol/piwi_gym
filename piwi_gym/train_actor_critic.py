import tensorflow as tf
from piwi_gym.agents.actor_critic import ActorCritic
import keras.backend as K
import gym
import piwi_gym
import sys
import os
import numpy as np

def main(env, agent):
    env = env
    actor_critic = agent

    done = False
    _obs, rews_acts = env.reset(False, False)

    while not done:
        actions = actor_critic.act(_obs)
        action = np.argmax(actions)
        new_obs, action, reward, info, done = env.step(action)
        actor_critic.remember_sale(_obs, actions, reward, new_obs, done)
        actor_critic.train()

        _obs = new_obs


if __name__ == "__main__":
    sess = tf.Session()
    K.set_session(sess)
    env = gym.make("piwi-v0")
    actor_critic = ActorCritic(env, sess)
    try:
        main(env, actor_critic)
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            env.reset(False, True)
            sys.exit(0)
        except SystemExit:
            os._exit(0)