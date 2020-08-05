#! /usr/bin/env pypy3
# ----------------------------------------------------------------------------------------
# This script runs the Q-learning algorithm for 2,000 days. Training can be stopped at any
# point by hitting Ctrl-C and restarted by running this script again. Data is collected in
# a `training` directory.
# ----------------------------------------------------------------------------------------

import datetime as dt
import pickle
import os
import threading
import time
import sys


# -------- Settings -------- #
max_runs = 2000
num_taxis = 3600
enable_sharing = True
max_taxi_size = 16
# -------------------------- #


sys.path.append('.')
import taxisim
taxisim.params.MAXSIZE = max_taxi_size


class TrainingThread(threading.Thread):

    def run(self):
        requests = {}
        for day in range(1, 30):
            with open(f"data/requests/2016-02-{day:02d}.pickle", 'rb') as file:
                requests[day] = pickle.load(file)

        with open("training/log.pickle", 'rb') as file:
            logdict = pickle.load(file)

        run_num = logdict["run_count"]
        with open(f"training/taxis-{run_num:04d}.pickle", 'rb') as file:
            taxis = pickle.load(file)

        logfile = open("training/log.txt", 'a');

        world = taxisim.World(ridesharing=enable_sharing)
        world.add_taxis(taxis)

        while run_num < max_runs:
            if self.halt:
                break

            run_num += 1
            day = run_num % 29 or 29
            start_time = time.time()
            delta_p = 1 / 500

            title = f"Run: {run_num}/{max_runs}  [2016-02-{day:02d}]  "
            title += f"[{num_taxis} taxis, ridesharing = {enable_sharing}]"
            log(f"\n**********   {title}   **********\n", logfile)

            world.time = dt.datetime(2016, 2, day, 8)
            world.reset_metrics()
            world.reset_taxis()
            world.add_requests(requests[day])

            for taxi in taxis:
                if run_num > 1000 and run_num <= 1500:
                    taxi.p_explore -= delta_p
                taxi.choose_action()

            world.run()

            for taxi in taxis:
                taxi.update_q_table()

            with open(f"training/taxis-{run_num:04d}.pickle", 'wb') as file:
                pickle.dump(taxis, file)
            print("* Taxis saved.")

            sizes = {}
            for taxi in taxis:
                sizes[taxi.size] = sizes.get(taxi.size, 0) + 1

            logdict["run_count"] = run_num
            logdict["runs"][run_num] = {
                "day": day,
                "sizes": sizes,
                "requests": world.num_requests,
                "timeouts": world.num_timeouts,
                "timeout_percent": world.timeout_percent,
                "mean_dispatch": world.mean_dispatch_time,
                "mean_pickup": world.mean_pickup_time,
                "mean_wait": world.mean_wait_time,
            }

            with open("training/log.pickle", 'wb') as file:
                pickle.dump(logdict, file)
            print("* Pickled log saved.")
            print(f"* Run {run_num} complete.\n")

            log(f"Sim time:  {(time.time() - start_time) / 60:.2f}m", logfile)
            log(f"Requests:  {world.num_requests}", logfile)
            log(f"Timeouts:  {world.num_timeouts} ({world.timeout_percent:.4f}%)", logfile)
            log(f"Mean wait: {world.mean_wait_time:.2f}m\n", logfile)
            for size, count in sorted(sizes.items()):
                log(f"{size:2d}: {count}", logfile)

            taxi = taxis[0]
            data =  f"ID: {taxi.id}  Size: {taxi.size}  LA: {taxi.last_action}  "
            data += f"LC: {taxi.last_choice.value}  P: {taxi.p_explore:.3f}"
            log(f"\nSample taxi: [{data}]\n", logfile)
            log(taxi.q_table, logfile)

        logfile.close()


def log(msg, logfile):
    print(msg)
    logfile.write(str(msg))
    logfile.write("\n")


def train():
    print("[STARTING... (Ctrl-C to halt)]")
    thread = TrainingThread()
    thread.halt = False
    thread.start()

    try:
        while thread.is_alive():
            thread.join(timeout=0.5)
    except KeyboardInterrupt:
        print("[HALTING... (may take some time)]")
        thread.halt = True

    thread.join()


def init():
    if not os.path.isdir("training"):
        os.mkdir("training")

    taxis = taxisim.make_taxis(num_taxis, size=4)
    with open("training/taxis-0000.pickle", 'wb') as file:
        pickle.dump(taxis, file)

    log = {
        "run_count": 0,
        "runs": {0: {"sizes": {4: num_taxis}}},
    }
    with open("training/log.pickle", 'wb') as file:
        pickle.dump(log, file)


if __name__ == "__main__":
    if not os.path.isfile("training/log.pickle"):
        init()
    train()
