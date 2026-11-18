"""Store generated demo secrets and issue a scoped local pipeline token."""
import json
import secrets
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def root(command, data=None):
    result=subprocess.run(['docker','exec','-i','lab4-vault','sh','-c',
        'export VAULT_ADDR=http://127.0.0.1:8200 VAULT_TOKEN="$VAULT_DEV_ROOT_TOKEN_ID"; '+command],
        input=data,capture_output=True,text=True)
    if result.returncode: raise RuntimeError('Vault command failed: '+result.stderr)
    return result.stdout


if __name__=='__main__':
    status=json.loads(root('vault status -format=json'))
    assert status['initialized'] and not status['sealed']
    print('[PASS] Vault initialized and unsealed (development mode)')
    expected={'db_password':secrets.token_urlsafe(32),'api_key':secrets.token_urlsafe(32)}
    root('vault kv put -format=json secret/lab4/app -',json.dumps(expected))
    actual=json.loads(root('vault kv get -format=json secret/lab4/app'))['data']['data']
    assert actual==expected
    print('[PASS] Generated credentials stored and retrieved; values redacted')
    root('vault policy write lab4-ci -','path "secret/data/lab4/app" { capabilities = ["read"] }\n')
    token=json.loads(root('vault token create -policy=lab4-ci -no-default-policy -ttl=1h -format=json'))['auth']['client_token']
    token_file=ROOT/'.runtime/pipeline-token'
    token_file.write_text(token)
    token_file.chmod(0o600)
    print('[PASS] Scoped read-only pipeline token issued (1-hour TTL)')
    result=subprocess.run(['docker','exec','-i','lab4-vault','sh','-c',
        'read -r VAULT_TOKEN; export VAULT_TOKEN VAULT_ADDR=http://127.0.0.1:8200; vault kv put secret/lab4/forbidden denied=1'],
        input=token+'\n',capture_output=True,text=True)
    assert result.returncode!=0 and 'permission denied' in result.stderr.lower()
    print('[PASS] Unauthorized write denied by Vault policy')
