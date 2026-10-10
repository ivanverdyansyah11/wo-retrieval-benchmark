"""Dry-run or atomically import reviewed judgments, never overwrite conflicting decisions."""
import argparse
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from wo_retrieval import human_judgments as h
from wo_retrieval import human_import as importer


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=('dry-run','apply'))
    parser.add_argument('--source',required=True,type=Path)
    parser.add_argument('--audit',required=True,type=Path)
    parser.add_argument('--out',required=True,type=Path)
    parser.add_argument('--plan',type=Path)
    args=parser.parse_args()
    try:
        package=h.load_package(ROOT,ROOT/h.WORKSPACE)
        h.audit_sources(ROOT)
        if not args.out.resolve().is_relative_to(ROOT/'experiments/results/milestone_9a18_controlled_import'):
            raise ValueError('Output must be a new milestone_9a18_controlled_import directory')
        if args.command=='dry-run':
            plan,_=importer.preflight(package,args.source,args.audit)
            args.out.mkdir(parents=True,exist_ok=False)
            h.write_json(args.out/'dry_run.json',plan)
            print(plan['status'], 'to_import',len(plan['to_import']),'skipped',len(plan['skipped']),'conflicts',len(plan['conflicts']))
            return 0 if plan['status']=='PASS' else 2
        if args.plan is None:
            raise ValueError('Apply requires --plan from a successful dry-run')
        receipt=importer.apply_import(package,args.source,args.audit,h.read_json(args.plan),args.out)
        print(receipt['import_status'],'imported',receipt['imported'],'skipped',len(receipt['skipped']))
        return 0
    except (ValueError,KeyError,TypeError,OSError) as error:
        parser.exit(2,str(error)+'\n')


if __name__=='__main__':
    raise SystemExit(main())
