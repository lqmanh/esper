#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gc
import pickle
import sys
import time
import optparse

import esper

######################
# Commandline options:
######################
parser = optparse.OptionParser()
parser.add_option("-c", "--cached", dest="cached", action="store_true", default=False,
                  help="Benchmark esper.CachedWorld instead of esper.World.")
parser.add_option("-p", "--plot", dest="plot", action="store_true", default=False,
                  help="Display benchmark. Requires matplotlib module.")
parser.add_option("-w", "--walltime", dest="walltime", action="store_true", default=False,
                  help="Benchmark the 'wall clock' time, instead of process time.")
parser.add_option("-e", "--entities", dest="entities", action="store", default=5000, type="int",
                  help="Change the maximum number of Entities to benchmark. Default is 5000.")

(options, arguments) = parser.parse_args()

MAX_ENTITIES = options.entities
if MAX_ENTITIES <= 500:
    print("The number of entities must be greater than 500.")
    sys.exit(1)

if options.walltime:
    print("Benchmarking wall clock time...\n")
    time_query = time.time
else:
    time_query = time.process_time


##########################
# Simple timing decorator:
##########################
def timing(f):
    def wrap(*args):
        time1 = time_query()
        ret = f(*args)
        time2 = time_query()
        result_times.append((time2 - time1)*1000.0)
        return ret
    return wrap


##############################
#  Instantiate the game world:
##############################
if options.cached:
    print("Benchmarking CachedWorld...\n")
    world = esper.CachedWorld()
else:
    world = esper.World()


#################################
# Define some generic components:
#################################
class Velocity:
    def __init__(self):
        self.x = 0
        self.y = 0


class Position:
    def __init__(self):
        self.x = 0
        self.y = 0


class Health:
    def __init__(self):
        self.hp = 100


class Command:
    def __init__(self):
        self.attack = False
        self.defend = True


class Projectile:
    def __init__(self):
        self.size = 10
        self.lifespan = 100


class Damageable:
    def __init__(self):
        self.defense = 45


class Brain:
    def __init__(self):
        self.smarts = 9000


#############################
# Set up some dummy entities:
#############################
def create_entities(number):
    for _ in range(number // 2):
        enemy = world.create_entity()
        world.add_component(enemy, Position())
        world.add_component(enemy, Velocity())
        world.add_component(enemy, Health())
        world.add_component(enemy, Command())

        thing = world.create_entity()
        world.add_component(thing, Position())
        world.add_component(thing, Health())
        world.add_component(thing, Damageable())


#############################
# Some timed query functions:
#############################
@timing
def single_comp_query():
    for _, _ in world.get_component(Position):
        pass


@timing
def two_comp_query():
    for _, (_, _) in world.get_components(Position, Velocity):
        pass


@timing
def three_comp_query():
    for _, (_, _, _) in world.get_components(Position, Damageable, Health):
        pass


#################################################
# Perform several queries, and print the results:
#################################################
results = {1: {}, 2: {}, 3: {}}
result_times = []

for amount in range(500, MAX_ENTITIES, MAX_ENTITIES//50):
    create_entities(amount)
    for _ in range(50):
        single_comp_query()

    result_min = min(result_times)
    print("Query one component, {} Entities: {:f} ms".format(amount, result_min))
    results[1][amount] = result_min
    result_times = []
    world.clear_database()
    gc.collect()

for amount in range(500, MAX_ENTITIES, MAX_ENTITIES//50):
    create_entities(amount)
    for _ in range(50):
        two_comp_query()

    result_min = min(result_times)
    print("Query two components, {} Entities: {:f} ms".format(amount, result_min))
    results[2][amount] = result_min
    result_times = []
    world.clear_database()
    gc.collect()

for amount in range(500, MAX_ENTITIES, MAX_ENTITIES//50):
    create_entities(amount)
    for _ in range(50):
        three_comp_query()

    result_min = min(result_times)
    print("Query three components, {} Entities: {:f} ms".format(amount, result_min))
    results[3][amount] = result_min
    result_times = []
    world.clear_database()
    gc.collect()


#############################################
# Save the results to disk, or plot directly:
#############################################

if not options.plot:
    print("\nRun 'benchmark.py --help' for details on plotting this benchmark.")

if options.plot:
    try:
        from matplotlib import pyplot as plt
    except ImportError:
        print("\nThe matplotlib module is required for plotting results.")
        sys.exit(1)

    lines = []
    for num, result in results.items():
        x, y = zip(*sorted(result.items()))
        label = '%i Component%s' % (num, '' if num == 1 else 's')
        lines.extend(plt.plot(x, y, label=label))

    plt.ylabel("Query Time (ms)")
    plt.xlabel("Number of Entities")
    plt.legend(handles=lines, bbox_to_anchor=(0.5, 1))
    plt.show()