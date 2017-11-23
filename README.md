# The Self dialogue corpus
This is an early release of the Self-dialogue corpus.

### Using the data
* `corpus` contains the raw CSVs from Amazon Mechanical Turk, sorted by individual tasks (topics);
* `blocked_workers.txt` lists workers who did not comply with the requirements of the tasks;
* `get_data.py` is a preprocessing script which will format the CSVs into text, along with various options (see below).

#### `get_data.py`
Example usage: `python get_data.py corpus formatted_corpus`.

Optional arguments:
* `--output-naming` whether to name output files with integers (`integer`) or by assignment_id (`assignment_id`);
* `--remove-punctuation` removes punctuation from the output;
* `--set-case` sets case of output to `original`, `upper` or `lower`;
* `--exclude-topic` excludes any of the topics (or subdirectories of `corpus`), e.g. `--exclude-topic music`;
* `--include-only` includes only the given topics, e.g. `--include-only music`.

### Citation
For research using this data, please cite:
```
@article{damonte2017edina,
  title={Edina: Building an Open Domain Socialbot with Self-dialogues},
  author={Damonte, Ben Krause Marco and Dobre, Mihai and Duma, Daniel and Fainberg, Joachim and Fancellu, Federico and Kahembwe, Emmanuel and Webber, Jianpeng Cheng Bonnie},
  journal={arXiv preprint arXiv:1709.09816},
  year={2017}
}
```
