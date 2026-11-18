#!/usr/bin/env python3
"""Fetch and reconcile one revision from an isolated local Git remote."""
import argparse
import subprocess
from pathlib import Path
from deploy import reconcile


def git(*args):
    return subprocess.check_output(['git', *map(str,args)], stderr=subprocess.STDOUT, text=True).strip()


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--repository',required=True)
    parser.add_argument('--checkout',required=True)
    args=parser.parse_args()
    checkout=Path(args.checkout).resolve()
    if not checkout.exists():
        git('clone',args.repository,checkout)
    git('-C',checkout,'fetch','origin','main')
    git('-C',checkout,'checkout','--detach','origin/main')
    print('Git revision:',git('-C',checkout,'rev-parse','HEAD'),flush=True)
    reconcile(checkout/'desired-state.yml')
