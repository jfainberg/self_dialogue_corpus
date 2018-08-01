# Self-dialogue corpus
# https://github.com/jfainberg/self_dialogue_corpus
# 2017
from __future__ import absolute_import, division, print_function
import argparse, logging, csv, os, sys
import random, string
from glob import glob
from collections import defaultdict
logging.basicConfig(format='%(asctime)s - %(name)s - %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p', 
                    level=logging.INFO)
logger = logging.getLogger('Self dialogue corpus')

def main():
    args = parse_args()
    logger.info("Will write data to {0}.".format(args.outDir))

    # Create output directories
    train_dir = create_dirs(args.outDir)

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

    # Write data
    logger.info("Writing dialogues...")
    write_dialogues(dialogues, dialogues.keys(), train_dir, args)

    logger.info("Done writing to {0}.".format(train_dir))

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
                    for ch in string.punctuation:
                        sentence = sentence.replace(ch, "")

                if sentence == "{}":
                    # Sometimes empty responses from Amazon would just include "{}"
                    continue
                f.write("{0}\n".format(sentence))

        counter += 1

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
    train_dir = "{0}/".format(root_dir)

    for d in [train_dir]:
        if not os.path.exists(d):
            os.makedirs(d)

    return train_dir 

def parse_args():
    """Parse input arguments."""
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="""Prepares data directories with dialogues from the
            self-dialogue corpus.""",
            epilog="Example usage: python get_data.py")
    parser.add_argument("--inDir", 
            help="Source data directory.",default="corpus")
    parser.add_argument("--outDir",
            help="Where to store output data directories (train, dev, test).",default="dialogues")
    parser.add_argument("--exclude-topic", action='append',
            default=[],
            help="""Exclude one or more topics, e.g.:
            --exclude-topic transition_music_movies --exclude-topic music""")
    parser.add_argument("--include-only", action='append',
            default=[],
            help="""If set will only include one or more given topics, e.g.:
            --include-only music --include-only nfl_football""")
    parser.add_argument("--output-naming", type=str, default="integer",
            choices=["integer", "assignment_id"],
            help="""Whether to name output files with integers (1 to
            the number of total dialogues) or whether to name by assignment_id.
            E.g. '43.txt'.""")
    parser.add_argument("--remove-punctuation", action="store_true",
            help="""Remove punctuation from output.""")
    parser.add_argument("--set-case", choices=["original", "upper", "lower"],
            default="original", help="""Set output case.""")
    
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    main()
