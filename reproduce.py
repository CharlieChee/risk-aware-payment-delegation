"""Reproduce reporting and deterministic benchmark checks without model calls."""
from pathlib import Path
import argparse, subprocess, sys

ROOT=Path(__file__).resolve().parent

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--pdf',action='store_true')
    p.add_argument('--verify-references',action='store_true',help='Recompute all 200 primary tasks using two exact implementations.')
    p.add_argument('--workers',type=int,default=4)
    args=p.parse_args()
    subprocess.run([sys.executable,'-m','unittest','discover','-s','tests'],cwd=ROOT,check=True)
    if args.verify_references:
        subprocess.run([sys.executable,'-m','risk_payment.verify','--workers',str(args.workers)],cwd=ROOT,check=True)
    subprocess.run([sys.executable,'reproduce.py']+(['--pdf'] if args.pdf else []),cwd=ROOT/'paper',check=True)

if __name__=='__main__':main()
