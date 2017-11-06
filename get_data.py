# Self-dialogue corpus
# URL
# Citation 2017
import argparse, logging, csv, os, sys
import random, string
from glob import glob
from collections import defaultdict
logging.basicConfig(format='%(asctime)s - %(name)s - %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p', 
                    level=logging.INFO)
logger = logging.getLogger('self_dialogue_corpus')

def main():
    args = parse_args()
    random.seed(args.seed)
    logger.info("Will write data to {0}.".format(args.outDir))

    # Create output directories
    train_dir, val_dir, test_dir = create_dirs(args.outDir)

    if os.path.isfile("blocked_workers.txt"):
        with open("blocked_workers.txt") as f:
            blocked_workers = f.read().splitlines()
    else:
        blocked_workers = []
    logger.info("Will ignore assignments from these workers: {0}".format(blocked_workers))

    # Define topics
    topics = os.listdir(args.inDir)
    if args.include_only:
        topics = args.include_only
    if args.exclude_topic:
        topics = set(topics).difference(set(args.exclude_topic))

    # Read data
    dialogues = {}
    for topic in topics:
        logger.info("Reading data into memory for topic {0}".format(topic))
        new_data = read_data("{0}/{1}".format(args.inDir, topic), blocked_workers)
        dialogues.update(new_data)

    logger.info("Read {0} dialogues".format(len(dialogues.keys())))

    # Select keys
    train_keys, val_keys, test_keys = select_keys(dialogues, args.order, args.split)

    # Write data
    logger.info("Writing dialogues...")
    write_dialogues(dialogues, train_keys, train_dir, args)
    write_dialogues(dialogues, val_keys, val_dir, args)
    write_dialogues(dialogues, test_keys, test_dir, args)

    logger.info("Done writing to {0}, {1}, and {2}".format(train_dir, val_dir, test_dir))

def write_dialogues(dialogues, keys, directory, args):
    """Writes dialogues given keys to directory."""
    counter = 0
    for key in keys:
        if args.output_naming == "integer":
            filename = counter
        elif args.output_naming == "assignment_id":
            filename = key

        dialogue = dialogues[key]

        with open("{0}/{1}.txt".format(directory, filename), 'w') as f:

            logger.debug("Writing dialogue to {0}/{1}.txt".format(directory, filename))

            # Get count of actually completed sentences
            num_sentences = len([key for key in dialogues[key].keys() if key != None and key.startswith('Answer')])

            for i in range(1, num_sentences+1):
                sentence = dialogue["Answer.sentence{0}".format(i)]

                # Case
                if args.set_case == "upper":
                    sentence = sentence.upper()
                elif args.set_case == "lower":
                    sentence = sentence.lower()

                # Punctutation
                if args.remove_punctuation:
                    sentence = sentence.translate(None, string.punctuation)

                if sentence == "{}":
                    # Sometimes empty responses from Amazon would just include "{}"
                    continue
                f.write("{0}\n".format(sentence))

        counter += 1

def select_keys(dialogues, order, split):
    """Returns dialogue keys for splitting the dataset given
    order and split."""
    total_convos = len(dialogues)
    train_upper = total_convos * split[0] // 100
    val_upper = train_upper + (total_convos * split[1] // 100)
    keys = dialogues.keys()
    if order == "random":
        random.shuffle(keys)
        train_keys = keys[:train_upper]
        val_keys = keys[train_upper:val_upper]
        test_keys = keys[val_upper:]
    elif order == "assignment_id":
        keys.sort()
        train_keys = keys[:train_upper]
        val_keys = keys[train_upper:val_upper]
        test_keys = keys[val_upper:]
    elif order == "time":
        # map Assignment IDs to CreationTime
        time_hitid_map = defaultdict(list)
        for assignment_id in keys:
            time_hitid_map[dialogues[assignment_id]['CreationTime']].append(assignment_id)
        time_keys = time_hitid_map.keys()
        time_keys.sort()
        sorted_hitid_keys = []
        for k in time_keys:
            sorted_hitid_keys.extend(time_hitid_map[k])
        train_keys = sorted_hitid_keys[:train_upper]
        val_keys = sorted_hitid_keys[train_upper:val_upper]
        test_keys = sorted_hitid_keys[val_upper:]

    return train_keys, val_keys, test_keys

def read_data(directory, blocked_workers=[]):
    """Reads data from CSVs in a directory and 
    returns a dictionary indexed by assignment IDs.
    Ignores workers in blocked_workers list."""
    dialogues = {} # indexed by assignment IDs
    for filename in glob("{0}/*.csv".format(directory)):
        with open(filename) as f:
            csvreader = csv.DictReader(f)
            for row in csvreader:
                # if len(restrict_to) > 0:
                #     if row['WorkerId'] not in restrict_to:
                #         continue
                if (row['Reject'] == "" or row['Reject'] == None) and row['WorkerId'] not in blocked_workers:
                    dialogues[row['AssignmentId']] = row

    return dialogues

def create_dirs(root_dir):
    """Create training directories. Returns their paths."""
    train_dir = "{0}/train".format(root_dir)
    val_dir = "{0}/val".format(root_dir)
    test_dir = "{0}/test".format(root_dir)

    for d in [train_dir, val_dir, test_dir]:
        if not os.path.exists(d):
            os.makedirs(d)

    return train_dir, val_dir, test_dir

def parse_args():
    """Parse input arguments."""
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="""Writes dialogues from the corpus.""")
    parser.add_argument("inDir", 
            help="Source data directory.")
    parser.add_argument("outDir",
            help="Where to store output data.")
    parser.add_argument("--order", 
            choices=["assignment_id", "random", "time"], default="random",
            help="""How to split data: by order of sorted convo assignment ID, 
            creation time or random (see --seed).""")
    parser.add_argument("--seed", type=int, default=123,
            help="Only relevant with --order random.")
    parser.add_argument("--split", nargs=3, type=int, default=[90, 5, 5],
            help="""Train, val, test split. Must sum to 100.
            Takes three space separated integers.
            E.g. --split 80 10 10""")
    parser.add_argument("--output-naming", type=str, default="integer",
            choices=["integer", "assignment_id"],
            help="""Whether to name output files with integers (1 to
            total dialogues) or whether to name by assignment_id.
            E.g. '43.txt'.""")
    parser.add_argument("--remove-punctuation", action="store_true",
            help="""Remove punctuation from output.""")
    parser.add_argument("--set-case", choices=["original", "upper", "lower"],
            default="original", help="""Set output case.""")
    parser.add_argument("--exclude-topic", action='append',
            default=[],
            help="""Exclude one or more topics, e.g.:
            --exclude-topic transition_music_movies --exclude-topic music""")
    parser.add_argument("--include-only", action='append',
            default=[],
            help="""If set will only include one or more given topics, e.g.:
            --include-only music --include-only nfl_football""")
    
    args = parser.parse_args()
    assert sum(args.split) == 100, "--split arguments must sum to 100"
    return args

if __name__ == '__main__':
    main()
