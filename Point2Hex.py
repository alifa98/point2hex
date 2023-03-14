import logging
import os
import sys
from lib.ConfigLoader import ConfigLoader
import pandas as pd
import threading
from lib.GetPointsThread import GeneratePointsThread
from lib.api.OpenSteetMap import OpenStreetAPI
from lib.ArgsParse import parse_args_default_with_config

logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


def get_split_points(total, num_threads):
    step = (total // int(num_threads))+1
    split_points_list = [i for i in range(0, total, step)]

    # make sure all of the instaces included (last step may contain more values)
    split_points_list.pop()
    # rages are like [start,end) so we do not need to add -1 here.
    split_points_list.append(total)

    return split_points_list


if __name__ == '__main__':

    config = ConfigLoader(os.path.join(os.path.dirname(
        os.path.abspath(__file__)), 'config.json'))
    args = parse_args_default_with_config(config)

    # the API that we want to use
    api = OpenStreetAPI(args.base_url)

    data_file = pd.read_csv(args.input_file)

    if not args.point_save_off:
        data_file[args.output_route] = pd.Series(dtype=object)

    data_file[args.output_hexagone] = pd.Series(dtype=object)

    try:
        sem = threading.Semaphore(value=int(args.concurrent_requests))

        # with tqdm(total=len(data_file)) as pbar:

        split_points = get_split_points(len(data_file), args.threads)

        threads_list = []
        # Create new threads
        for i in range(len(split_points)-1):

            threads_list.append(
                GeneratePointsThread(i, data_file,
                                     split_points[i], split_points[i+1],
                                     sem, api, args)
            )

        logging.info("Starting...")
        # Starting the threads
        for t in threads_list:
            t.start()

        logging.info("Processing...")

        # waiting for threads
        for t in threads_list:
            t.join()

        logging.info("All threads are finished.")

    except KeyboardInterrupt:
        print("Exiting...")

    if not args.split:
        data_file.to_csv(f"{args.output}.csv", index=False)
