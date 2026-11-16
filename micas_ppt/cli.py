import argparse
import sys
from .engine import convert


def main():
    parser = argparse.ArgumentParser(description='Convert PPTX using the registered Micas official template')
    parser.add_argument('input')
    parser.add_argument('output')
    parser.add_argument('--report')
    parser.add_argument('--repo-root', help='Template repository root; required when installed outside this checkout')
    parser.add_argument('--allow-risk', action='store_true', help='Accept explicitly reported unsupported object risks')
    args = parser.parse_args()
    try:
        result = convert(args.input, args.output, args.report, repo_root=args.repo_root, allow_risk=args.allow_risk)
    except Exception as exc:
        print(f'Conversion failed: {exc}', file=sys.stderr)
        return 1
    print(f"{result['status']}: {result['integrity']['output_slides']} slides")
    return 0


if __name__ == '__main__':
    sys.exit(main())
