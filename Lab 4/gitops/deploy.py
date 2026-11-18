#!/usr/bin/env python3
"""Reconcile one local, Git-sourced Docker manifest; fail on Docker errors."""
import argparse
import json
import subprocess
from pathlib import Path
import yaml


def docker(*args, check=True):
    result = subprocess.run(['docker', *args], capture_output=True, text=True)
    if check and result.returncode:
        raise RuntimeError(result.stderr.strip())
    return result


def reconcile(path):
    state = yaml.safe_load(Path(path).read_text())
    changes = 0
    for service in state['services']:
        name = service['name']
        if not name.startswith('lab4-gitops-') or service.get('replicas', 1) != 1:
            raise ValueError('Only single-instance lab4-gitops-* resources are supported')
        existing = docker('container', 'inspect', name, check=False)
        drift = []
        desired_env = {str(k): str(v) for k,v in service.get('env', {}).items()}
        container_port = str(service.get('container_port', 5000)) + '/tcp'
        desired_binding = [{'HostIp': '127.0.0.1', 'HostPort': str(service['port'])}]
        if existing.returncode == 0:
            actual = json.loads(existing.stdout)[0]
            if actual['Config'].get('Labels', {}).get('lab') != 'lab4-gitops':
                raise RuntimeError(f'Refusing to replace unowned container {name}')
            if not actual['State']['Running']: drift.append('stopped')
            if actual['Config']['Image'] != service['image']: drift.append('image')
            image_id = docker('image', 'inspect', service['image'], '--format', '{{.Id}}').stdout.strip()
            if actual['Image'] != image_id: drift.append('image content')
            actual_env = dict(value.split('=',1) for value in actual['Config']['Env'])
            if any(actual_env.get(k) != v for k,v in desired_env.items()): drift.append('environment')
            if actual['HostConfig']['PortBindings'] != {container_port: desired_binding}: drift.append('ports')
        else:
            drift.append('missing')
        if not drift:
            print(f'[OK] {name}: no drift', flush=True)
            continue
        print(f'[DRIFT] {name}: {", ".join(drift)}', flush=True)
        if existing.returncode == 0:
            docker('rm', '-f', name)
        args = ['run', '-d', '--name', name, '--label', 'lab=lab4-gitops', '-p', f'127.0.0.1:{service["port"]}:{service.get("container_port",5000)}']
        for k,v in desired_env.items(): args.extend(['-e', f'{k}={v}'])
        docker(*args, service['image'])
        assert json.loads(docker('inspect', name).stdout)[0]['State']['Running']
        changes += 1
        print(f'[APPLIED] {name} -> {service["image"]}', flush=True)
    print(f'[PASS] Reconciled {len(state["services"])} services; changed={changes}', flush=True)
    return changes


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--manifest', default=str(Path(__file__).with_name('desired-state.yml')))
    reconcile(parser.parse_args().manifest)
