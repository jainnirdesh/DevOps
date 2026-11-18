"""Verify live Lab 3 services; retain JSON responses as execution evidence."""
import json
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / 'evidence'


def get(url):
    with urllib.request.urlopen(url, timeout=15) as response:
        body = response.read().decode()
        try:
            return json.loads(body)
        except ValueError:
            return body


def retry(check, seconds=300):
    end = time.monotonic() + seconds
    while True:
        try:
            return check()
        except Exception as error:
            if time.monotonic() > end:
                raise
            print(f'Waiting: {error}', flush=True)
            time.sleep(5)


def verify():
    result = {}
    result['app'] = get('http://localhost:5003/health')
    assert result['app']['status'] == 'ok'
    for _ in range(10):
        get('http://localhost:5003/')
    result['metrics'] = get('http://localhost:5003/metrics')
    assert 'lab3_http_requests_total' in result['metrics']
    result['elasticsearch'] = get('http://localhost:9200/_cluster/health')
    assert result['elasticsearch']['status'] in ('green', 'yellow')
    result['logs'] = get('http://localhost:9200/lab3-logs-*/_search?q=service:lab3-flask')
    assert result['logs']['hits']['total']['value'] > 0, 'Application logs not indexed yet'
    result['kibana'] = get('http://localhost:5601/api/status')
    assert result['kibana']['status']['overall']['level'] == 'available'
    request = urllib.request.Request('http://localhost:5601/api/saved_objects/index-pattern/lab3-logs?overwrite=true', data=json.dumps({'attributes': {'title': 'lab3-logs-*', 'timeFieldName': '@timestamp'}}).encode(), headers={'Content-Type': 'application/json', 'kbn-xsrf': 'lab3'}, method='POST')
    with urllib.request.urlopen(request) as response:
        result['kibana_data_view'] = json.load(response)
    result['prometheus'] = get('http://localhost:9090/api/v1/targets')
    targets = result['prometheus']['data']['activeTargets']
    assert len(targets) == 3 and all(t['health'] == 'up' for t in targets), targets
    result['grafana'] = get('http://localhost:3000/api/health')
    assert result['grafana']['database'] == 'ok'
    request = urllib.request.Request('http://localhost:3000/api/dashboards/uid/lab3')
    import base64
    request.add_header('Authorization', 'Basic ' + base64.b64encode(b'admin:admin123').decode())
    with urllib.request.urlopen(request) as response:
        result['dashboard'] = json.load(response)
    assert result['dashboard']['dashboard']['title'] == 'Lab 3 Application Monitoring'
    return result


if __name__ == '__main__':
    data = retry(verify)
    (EVIDENCE / 'live-verification.json').write_text(json.dumps(data, indent=2))
    print('PASS: app, live metrics, indexed application logs, Kibana, all three Prometheus targets, Grafana dashboard')
