"""Build isolated or standalone agents from the compact 7.2 parameter vector."""

import argparse
import json
import os
import types

from tools import build_submission
from tuning import space


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def validate_vector(vector):
    clipped = space.clip_real(vector)
    for value, clipped_value, name in zip(vector, clipped, space.NAMES):
        if float(value) != clipped_value:
            raise ValueError(f"{name}={value!r} is outside its declared bounds")


def _module_from_source(source):
    module = types.ModuleType("_mapleleaf_candidate")
    module.__file__ = os.path.join(PROJECT_ROOT, "main.py")
    module.__package__ = None
    exec(compile(source, module.__file__, "exec"), module.__dict__)
    return module


def make_agent(vector, template_path=None):
    validate_vector(vector)
    module = _module_from_source(
        build_submission.build_merged_source(PROJECT_ROOT, main_path=template_path)
    )
    base_config, heuristic_config = space.vector_to_config(vector)
    module.configure_base(base_config)
    module.heuristics.configure(heuristic_config)
    return module.agent


def write_candidate(vector, output_path, template_path=None):
    validate_vector(vector)
    base_config, heuristic_config = space.vector_to_config(vector)
    override = (
        "\n# Compact CMA-ES candidate configuration.\n"
        f"configure_base({base_config!r})\n"
        f"heuristics.configure({heuristic_config!r})\n"
    )
    source = build_submission.build_merged_source(
        PROJECT_ROOT, main_path=template_path
    ) + override
    output_path = os.path.abspath(output_path)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(source)
    return output_path


def _checkpoint_vector(path):
    with open(path, encoding="utf-8") as handle:
        checkpoint = json.load(handle)
    checkpoint_names = tuple(checkpoint.get("param_names", ()))
    if checkpoint_names != space.NAMES:
        raise ValueError(
            "checkpoint parameter names do not match the compact 7.2 space; "
            "start a fresh run instead of interpreting values positionally"
        )
    return checkpoint["best_params"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", help="Compact CMA-ES checkpoint JSON")
    parser.add_argument(
        "--out",
        default=os.path.join(PROJECT_ROOT, "artifacts", "candidate", "main.py"),
    )
    parser.add_argument("--template", help="Alternative route-backbone source")
    args = parser.parse_args()
    vector = _checkpoint_vector(args.checkpoint) if args.checkpoint else space.default_vector()
    print(f"Wrote {write_candidate(vector, args.out, template_path=args.template)}")


if __name__ == "__main__":
    main()
