import argparse
import json
import pathlib
from csv import DictReader
from csv import DictWriter

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parameters apply")
    parser.add_argument("input_path", type=str, help="A path containing our original dataset")
    parser.add_argument("output_path", type=str, help="A path where we will write our updated dataset")
    parser.add_argument("parameters_path", type=argparse.FileType("r"), help="A path to a parameters.json file")

    args = parser.parse_args()

    # Let's make a copy of our original dataset
    original_dataset_path = pathlib.Path(args.input_path)

    if not original_dataset_path.exists():
        raise FileNotFoundError(f"The folder {original_dataset_path} " f"does not exists")

    dataset_files = dict()

    for _file in original_dataset_path.glob("*.csv"):
        _file_name = _file.name
        dataset_files.setdefault(_file_name, [])
        with _file.open("r") as _file_content:
            reader = DictReader(_file_content)
            for row in reader:
                dataset_files[_file_name].append(row)

    # Now that we made a memory copy of our file let's get our parameters

    with args.parameters_path as _file_parameters:
        parameters = json.load(_file_parameters)
        parameters = dict({_p["parameterId"]: _p["value"] for _p in parameters})

    # Now we can apply our parameters to our Bar file
    if "Bar.csv" not in dataset_files:
        raise FileNotFoundError(f"No Bar.csv could be found " f"in the given input folder")

    bars = dataset_files["Bar.csv"]

    for bar in bars:
        bar["Stock"] = parameters["Stock"]
        bar["NbWaiters"] = parameters["NbWaiters"]
        bar["RestockQty"] = parameters["RestockQty"]

    # and now that our dataset got updated we can write it

    target_dataset_path = pathlib.Path(args.output_path)
    if target_dataset_path.exists() and not target_dataset_path.is_dir():
        raise FileExistsError(f"{target_dataset_path} exists " f"and is not a directory")
    target_dataset_path.mkdir(parents=True, exist_ok=True)

    for _file_name, _file_content in dataset_files.items():
        _file_path = target_dataset_path / _file_name
        with _file_path.open("w") as _file:
            writer = DictWriter(_file, _file_content[0].keys())
            writer.writeheader()
            writer.writerows(_file_content)
