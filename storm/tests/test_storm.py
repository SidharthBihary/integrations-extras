# (C) Datadog, Inc. 2010-2016
# All rights reserved
# Licensed under Simplified BSD License (see LICENSE)
from collections import defaultdict

from datadog_checks.base import AgentCheck
from datadog_checks.storm import StormCheck
from .common import (
    TEST_STORM_CLUSTER_SUMMARY,
    TEST_STORM_NIMBUSES_SUMMARY, TEST_STORM_SUPERVISOR_SUMMARY,
    TEST_STORM_TOPOLOGY_SUMMARY, TEST_STORM_TOPOLOGY_RESP,
    TEST_STORM_TOPOLOGY_METRICS_RESP
)

import pytest
import responses
import mock

CHECK_NAME = 'storm'
STORM_CHECK_CONFIG = {'instances': [{'server': 'http://localhost:8080', 'environment': 'test'}]}
STORM_CHECK_INTEGRATION_CONFIG = {'instances': [{'server': 'http://localhost:8080', 'environment': 'integration'}]}


def test_load_from_config():
    check = StormCheck(STORM_CHECK_CONFIG, {})
    check.update_from_config(STORM_CHECK_CONFIG['instances'][0])
    assert('http://localhost:8080' == check.nimbus_server)
    assert('test' == check.environment_name)
    assert([] == check.additional_tags)
    assert([] == check.excluded_topologies)
    assert([60] == check.intervals)


def test_get_storm_cluster_summary():
    with mock.patch(
        'datadog_checks.storm.StormCheck.get_request_json',
        return_value=TEST_STORM_CLUSTER_SUMMARY
    ):
        check = StormCheck(STORM_CHECK_CONFIG, {})
        check.update_from_config(STORM_CHECK_CONFIG['instances'][0])
        result = check.get_storm_cluster_summary()
        assert(TEST_STORM_CLUSTER_SUMMARY == result)


def test_get_storm_nimbus_summary():
    with mock.patch(
        'datadog_checks.storm.StormCheck.get_request_json',
        return_value=TEST_STORM_NIMBUSES_SUMMARY
    ):
        check = StormCheck(STORM_CHECK_CONFIG, {})
        check.update_from_config(STORM_CHECK_CONFIG['instances'][0])
        result = check.get_storm_nimbus_summary()
        assert(TEST_STORM_NIMBUSES_SUMMARY == result)


def test_get_storm_supervisor_summary():
    with mock.patch(
        'datadog_checks.storm.StormCheck.get_request_json',
        return_value=TEST_STORM_SUPERVISOR_SUMMARY
    ):
        check = StormCheck(STORM_CHECK_CONFIG, {})
        check.update_from_config(STORM_CHECK_CONFIG['instances'][0])
        result = check.get_storm_supervisor_summary()
        assert(TEST_STORM_SUPERVISOR_SUMMARY == result)


def test_get_storm_topology_summary():
    with mock.patch(
        'datadog_checks.storm.StormCheck.get_request_json',
        return_value=TEST_STORM_TOPOLOGY_SUMMARY
    ):
        check = StormCheck(STORM_CHECK_CONFIG, {})
        check.update_from_config(STORM_CHECK_CONFIG['instances'][0])
        result = check.get_storm_topology_summary()
        assert(TEST_STORM_TOPOLOGY_SUMMARY == result)


def test_get_storm_topology_info():
    with mock.patch(
        'datadog_checks.storm.StormCheck.get_request_json',
        return_value=TEST_STORM_TOPOLOGY_RESP
    ):
        check = StormCheck(STORM_CHECK_CONFIG, {})
        check.update_from_config(STORM_CHECK_CONFIG['instances'][0])
        result = check.get_topology_info('my_topology-1-1489183263')
        assert(TEST_STORM_TOPOLOGY_RESP == result)


def test_get_storm_topology_metrics():
    with mock.patch(
        'datadog_checks.storm.StormCheck.get_request_json',
        return_value=TEST_STORM_TOPOLOGY_METRICS_RESP
    ):
        check = StormCheck(STORM_CHECK_CONFIG, {})
        check.update_from_config(STORM_CHECK_CONFIG['instances'][0])
        result = check.get_topology_metrics('my_topology-1-1489183263')
        assert(TEST_STORM_TOPOLOGY_METRICS_RESP == result)


def test_process_cluster_stats():
    check = StormCheck(STORM_CHECK_CONFIG, {})

    check.update_from_config(STORM_CHECK_CONFIG['instances'][0])

    results = defaultdict(list)

    def report_gauge(metric, value, tags, additional_tags):
        results[metric].append(value)

    check.report_gauge = report_gauge

    check.process_cluster_stats(TEST_STORM_CLUSTER_SUMMARY)
    assert(13 == len(results))

    # Check Cluster Stats
    assert(33 == results['storm.cluster.executorsTotal'][0])
    assert(10 == results['storm.cluster.slotsTotal'][0])
    assert(4 == results['storm.cluster.slotsFree'][0])
    assert(1 == results['storm.cluster.topologies'][0])
    assert(1 == results['storm.cluster.supervisors'][0])
    assert(33 == results['storm.cluster.tasksTotal'][0])
    assert(6 == results['storm.cluster.slotsUsed'][0])


def test_process_nimbus_stats():
    check = StormCheck(STORM_CHECK_CONFIG, {})
    check.update_from_config(STORM_CHECK_CONFIG['instances'][0])

    results = defaultdict(list)

    def report_gauge(metric, value, tags, additional_tags):
        results[metric].append(value)

    check.report_gauge = report_gauge

    check.process_nimbus_stats(TEST_STORM_NIMBUSES_SUMMARY)
    assert(5 == len(results))

    # Check Leader Stats
    assert(0 == results['storm.nimbus.upTimeSeconds'][0])
    assert(25842 == results['storm.nimbus.upTimeSeconds'][1])

    # Check General Stats
    assert(1 == results['storm.nimbus.numLeaders'][0])
    assert(0 == results['storm.nimbus.numFollowers'][0])
    assert(1 == results['storm.nimbus.numOffline'][0])
    assert(0 == results['storm.nimbus.numDead'][0])


def test_process_supervisor_stats():
    check = StormCheck(STORM_CHECK_CONFIG, {})
    check.update_from_config(STORM_CHECK_CONFIG['instances'][0])

    results = defaultdict(list)

    def report_gauge(metric, value, tags, additional_tags):
        results[metric].append(value)

    check.report_gauge = report_gauge

    check.process_supervisor_stats(TEST_STORM_SUPERVISOR_SUMMARY)
    assert(7 == len(results))

    # Check Supervisor Stats
    assert(31559 == results['storm.supervisor.uptimeSeconds'][0])
    assert(10 == results['storm.supervisor.slotsTotal'][0])
    assert(6 == results['storm.supervisor.slotsUsed'][0])
    assert(3072 == results['storm.supervisor.totalMem'][0])
    assert(4992 == results['storm.supervisor.usedMem'][0])
    assert(900 == results['storm.supervisor.totalCpu'][0])
    assert(0 == results['storm.supervisor.usedCpu'][0])


def test_process_topology_stats():
    check = StormCheck(STORM_CHECK_CONFIG, {})
    check.update_from_config(STORM_CHECK_CONFIG['instances'][0])

    results = defaultdict(list)

    def report_histogram(metric, value, tags, additional_tags):
        results[metric].append((value, tags, additional_tags))

    check.report_histogram = report_histogram

    check.process_topology_stats(TEST_STORM_TOPOLOGY_RESP, interval=60)
    assert(47 == len(results))

    # Check Topology Stats
    assert(307606 == results['storm.topologyStats.last_60.emitted'][0][0])
    assert(307606 == results['storm.topologyStats.last_60.transferred'][0][0])
    assert(104673 == results['storm.topologyStats.last_60.acked'][0][0])
    assert(0 == results['storm.topologyStats.last_60.failed'][0][0])
    assert(285.950 == results['storm.topologyStats.last_60.completeLatency'][0][0])
    assert(1525788 == results['storm.topologyStats.last_60.uptimeSeconds'][0][0])
    assert(33 == results['storm.topologyStats.last_60.executorsTotal'][0][0])
    assert(6 == results['storm.topologyStats.last_60.numBolts'][0][0])
    assert(1 == results['storm.topologyStats.last_60.replicationCount'][0][0])
    assert(33 == results['storm.topologyStats.last_60.tasksTotal'][0][0])
    assert(1 == results['storm.topologyStats.last_60.numSpouts'][0][0])
    assert(6 == results['storm.topologyStats.last_60.workersTotal'][0][0])

    # Check Bolt Stats
    assert(3 == results['storm.bolt.last_60.tasks'][0][0])
    assert('bolt:Bolt1' in results['storm.bolt.last_60.tasks'][0][1])
    assert(0.001 == results['storm.bolt.last_60.executeLatency'][0][0])
    assert(201.474 == results['storm.bolt.last_60.processLatency'][0][0])
    assert(0.000 == results['storm.bolt.last_60.capacity'][0][0])
    assert(0 == results['storm.bolt.last_60.failed'][0][0])
    assert(101309 == results['storm.bolt.last_60.emitted'][0][0])
    assert(212282 == results['storm.bolt.last_60.acked'][0][0])
    assert(101309 == results['storm.bolt.last_60.transferred'][0][0])
    assert(106311 == results['storm.bolt.last_60.executed'][0][0])
    assert(3 == results['storm.bolt.last_60.executors'][0][0])
    assert(1E10 == results['storm.bolt.last_60.errorLapsedSecs'][0][0])

    # Check Spout Stats
    assert(8 == results['storm.spout.last_60.tasks'][0][0])
    assert('spout:source' in results['storm.spout.last_60.tasks'][0][1])
    assert(285.950 == results['storm.spout.last_60.completeLatency'][0][0])
    assert(0 == results['storm.spout.last_60.failed'][0][0])
    assert(104673 == results['storm.spout.last_60.acked'][0][0])
    assert(104673 == results['storm.spout.last_60.transferred'][0][0])
    assert(104673 == results['storm.spout.last_60.emitted'][0][0])
    assert(8 == results['storm.spout.last_60.executors'][0][0])
    assert(38737 == results['storm.spout.last_60.errorLapsedSecs'][0][0])


def test_process_topology_metrics():
    check = StormCheck(STORM_CHECK_CONFIG, {})
    check.update_from_config(STORM_CHECK_CONFIG['instances'][0])

    results = defaultdict(list)

    def report_histogram(metric, value, tags, additional_tags):
        results[metric].append((value, tags, additional_tags))

    check.report_histogram = report_histogram

    check.process_topology_metrics('test', TEST_STORM_TOPOLOGY_METRICS_RESP, 60)
    assert(10 == len(results))

    # Check Bolt Stats
    assert(120 == results['storm.topologyStats.metrics.bolts.last_60.emitted'][0][0])
    assert('stream:__metrics' in results['storm.topologyStats.metrics.bolts.last_60.emitted'][0][1])
    assert(190748180 == results['storm.topologyStats.metrics.bolts.last_60.emitted'][1][0])
    assert('stream:default' in results['storm.topologyStats.metrics.bolts.last_60.emitted'][1][1])
    assert(190718100 == results['storm.topologyStats.metrics.bolts.last_60.emitted'][2][0])
    assert('stream:__ack_ack' in results['storm.topologyStats.metrics.bolts.last_60.emitted'][2][1])
    assert(20 == results['storm.topologyStats.metrics.bolts.last_60.emitted'][3][0])
    assert('stream:__system' in results['storm.topologyStats.metrics.bolts.last_60.emitted'][3][1])
    assert(120 == results['storm.topologyStats.metrics.bolts.last_60.transferred'][0][0])
    assert(190733160 == results['storm.topologyStats.metrics.bolts.last_60.acked'][0][0])
    assert(0 == len(results['storm.topologyStats.metrics.bolts.last_60.failed']))
    assert(0 == len(results['storm.topologyStats.metrics.bolts.last_60.complete_ms_avg']))
    assert(0.004 == results['storm.topologyStats.metrics.bolts.last_60.process_ms_avg'][0][0])
    assert(190733140 == results['storm.topologyStats.metrics.bolts.last_60.executed'][0][0])
    assert(0.005 == results['storm.topologyStats.metrics.bolts.last_60.executed_ms_avg'][0][0])

    # Check Spout Stats
    assert(20 == results['storm.topologyStats.metrics.spouts.last_60.emitted'][0][0])
    assert('stream:__metrics' in results['storm.topologyStats.metrics.spouts.last_60.emitted'][0][1])
    assert(17350280 == results['storm.topologyStats.metrics.spouts.last_60.emitted'][1][0])
    assert('stream:default' in results['storm.topologyStats.metrics.spouts.last_60.emitted'][1][1])
    assert(17328160 == results['storm.topologyStats.metrics.spouts.last_60.emitted'][2][0])
    assert('stream:__ack_init' in results['storm.topologyStats.metrics.spouts.last_60.emitted'][2][1])
    assert(20 == results['storm.topologyStats.metrics.spouts.last_60.emitted'][3][0])
    assert('stream:__system' in results['storm.topologyStats.metrics.spouts.last_60.emitted'][3][1])
    assert(20 == results['storm.topologyStats.metrics.spouts.last_60.transferred'][0][0])
    assert(17339180 == results['storm.topologyStats.metrics.spouts.last_60.acked'][0][0])
    assert(0 == len(results['storm.topologyStats.metrics.spouts.last_60.failed']))
    assert(0 == len(results['storm.topologyStats.metrics.spouts.last_60.process_ms_avg']))
    assert(0 == len(results['storm.topologyStats.metrics.spouts.last_60.executed_ms_avg']))
    assert(0 == len(results['storm.topologyStats.metrics.spouts.last_60.executed']))
    assert(920.497 == results['storm.topologyStats.metrics.spouts.last_60.complete_ms_avg'][0][0])


@responses.activate
def test_check(aggregator):
    """
    Testing Storm check.
    """
    check = StormCheck(STORM_CHECK_CONFIG, {})

    responses.add(
        responses.GET,
        'http://localhost:8080/api/v1/cluster/summary',
        json=TEST_STORM_CLUSTER_SUMMARY,
        status=200
    )
    responses.add(
        responses.GET,
        'http://localhost:8080/api/v1/nimbus/summary',
        json=TEST_STORM_NIMBUSES_SUMMARY,
        status=200
    )
    responses.add(
        responses.GET,
        'http://localhost:8080/api/v1/supervisor/summary',
        json=TEST_STORM_SUPERVISOR_SUMMARY,
        status=200
    )
    responses.add(
        responses.GET,
        'http://localhost:8080/api/v1/topology/summary',
        json=TEST_STORM_TOPOLOGY_SUMMARY,
        status=200
    )
    responses.add(
        responses.GET,
        'http://localhost:8080/api/v1/topology/my_topology-1-1489183263',
        json=TEST_STORM_TOPOLOGY_RESP,
        status=200
    )
    responses.add(
        responses.GET,
        'http://localhost:8080/api/v1/topology/my_topology-1-1489183263/metrics',
        json=TEST_STORM_TOPOLOGY_METRICS_RESP,
        status=200
    )

    check.check(STORM_CHECK_CONFIG['instances'][0])

    topology_tags = ['topology:my_topology']
    env_tags = ['stormEnvironment:test']
    storm_version_tags = ['stormVersion:1.0.3']

    # Service Check
    aggregator.assert_service_check(
        'topology_check.my_topology',
        count=1,
        status=AgentCheck.OK,
        tags=env_tags + storm_version_tags
    )

    # Cluster Stats
    test_cases = (
        ('executorsTotal', 1, 33),
        ('slotsTotal', 1, 10),
        ('slotsFree', 1, 4),
        ('topologies', 1, 1),
        ('supervisors', 1, 1),
        ('tasksTotal', 1, 33),
        ('slotsUsed', 1, 6),
        ('availCpu', 1, 0),
        ('totalCpu', 1, 0),
        ('cpuAssignedPercentUtil', 1, 0),
        ('availMem', 1, 0),
        ('totalMem', 1, 0),
        ('memAssignedPercentUtil', 1, 0)
    )
    test_tags = env_tags + storm_version_tags
    for name, count, value in test_cases:
        aggregator.assert_metric(
            'storm.cluster.{}'.format(name),
            count=count,
            value=value,
            tags=test_tags
        )

    # Nimbus Stats
    test_cases = (
        ('upTimeSeconds', 1, 25842, ['stormStatus:leader', 'stormHost:1.2.3.4']),
        ('upTimeSeconds', 1, 0, ['stormStatus:offline', 'stormHost:nimbus01.example.com']),
        ('numLeaders', 1, 1, ['stormStatus:leader', 'stormHost:1.2.3.4']),
        ('numFollowers', 1, 0, ['stormStatus:leader', 'stormHost:1.2.3.4']),
        ('numOffline', 1, 1, ['stormStatus:leader', 'stormHost:1.2.3.4']),
        ('numDead', 1, 0, ['stormStatus:leader', 'stormHost:1.2.3.4'])
    )
    test_tags = env_tags + storm_version_tags

    for name, count, value, additional_tags in test_cases:
        aggregator.assert_metric(
            'storm.nimbus.{}'.format(name),
            count=count,
            value=value,
            tags=test_tags + additional_tags
        )

    # Supervisor Stats
    test_cases = (
        ('uptimeSeconds', 1, 31559),
        ('slotsTotal', 1, 10),
        ('slotsUsed', 1, 6),
        ('totalMem', 1, 3072),
        ('usedMem', 1, 4992),
        ('totalCpu', 1, 900),
        ('usedCpu', 1, 0),

    )

    for name, count, value in test_cases:
        aggregator.assert_metric(
            'storm.supervisor.{}'.format(name),
            count=count,
            value=value
        )

    # Topology Stats
    test_cases = (
        ('emitted', 1, 307606),
        ('transferred', 1, 307606),
        ('acked', 1, 104673),
        ('failed', 1, 0),
        ('completeLatency', 1, 285.950),
        ('uptimeSeconds', 1, 1525788),
        ('executorsTotal', 1, 33),
        ('numBolts', 1, 6),
        ('replicationCount', 1, 1),
        ('tasksTotal', 1, 33),
        ('numSpouts', 1, 1),
        ('workersTotal', 1, 6),
        ('assignedMemOnHeap', 1, 4992),
        ('assignedMemOffHeap', 1, 0),
        ('assignedTotalMem', 1, 4992),
        ('requestedMemOnHeap', 1, 0),
        ('requestedMemOffHeap', 1, 0),
        ('requestedCpu', 1, 0),
        ('assignedCpu', 1, 0),
        ('msgTimeout', 1, 300),
        ('debug', 1, 0),
        ('samplingPct', 1, 10)
    )

    test_tags = topology_tags + env_tags + storm_version_tags
    interval = 'last_60'

    for name, count, value in test_cases:
        aggregator.assert_metric(
            'storm.topologyStats.{}.{}'.format(interval, name),
            count=count,
            value=value,
            tags=test_tags
        )

    # Bolt Stats
    for name, values in [
        ('Bolt1', (3, 0.001, 201.474, 0.000, 0, 212282, 101309, 106311, 101309, 3, 1E10, 0, 0, 0)),
        ('Bolt2', (2, 0.015, 0.010, 0.000, 0, 3153, 0, 3153, 0, 2, 1E10, 0, 0, 0)),
        ('Bolt3', (3, 0.009, 0.003, 0.000, 0, 4704, 0, 4704, 0, 3, 1E10, 0, 0, 0)),
        ('Bolt4', (4, 0.001, 291.756, 0.000, 0, 218808, 101607, 110946, 101607, 4, 1E10, 0, 0, 0)),
        ('Bolt5', (2, 0.001, 1014.634, 0.000, 0, 208890, 17, 104445, 17, 2, 1E10, 0, 0, 0)),
        ('Bolt6', (3, 0.010, 0.005, 0.000, 0, 4705, 0, 4705, 0, 3, 1E10, 0, 0, 0))
    ]:
        test_tags = storm_version_tags + env_tags + topology_tags + ['bolt:{}'.format(name)]
        for i, metric_name in enumerate([
            'tasks', 'executeLatency', 'processLatency', 'capacity', 'failed', 'acked', 'transferred', 'executed',
            'emitted', 'executors', 'errorLapsedSecs', 'requestedMemOnHeap', 'requestedCpu', 'requestedMemOffHeap'
        ]):
            aggregator.assert_metric(
                'storm.bolt.last_60.{}'.format(metric_name),
                value=values[i],
                tags=test_tags,
                count=1
            )

    # Spout Stats
    for name, values in [
        ('source', (8, 285.950, 0, 104673, 104673, 104673, 8, 38737, 0, 0, 0)),
    ]:
        test_tags = storm_version_tags + topology_tags + env_tags + ['spout:{}'.format(name)]
        for i, metric_name in enumerate([
            'tasks', 'completeLatency', 'failed', 'acked', 'transferred', 'emitted', 'executors', 'errorLapsedSecs',
            'requestedMemOffHeap', 'requestedCpu', 'requestedMemOnHeap'
        ]):
            aggregator.assert_metric(
                'storm.spout.last_60.{}'.format(metric_name),
                value=values[i],
                tags=test_tags,
                count=1
            )

    # Topology Metrics
    metric_cases = (
        # Topology Metrics By Bolt
        ('storm.topologyStats.metrics.bolts.last_60.transferred', 0.0,
            storm_version_tags + topology_tags + env_tags + ['bolts:count', 'stream:__system']),
    )
    for m in ['acked', 'complete_ms_avg', 'emitted', 'transferred']:
        aggregator.assert_metric(
            'storm.topologyStats.metrics.spouts.last_60.{}'.format(m),
            at_least=1
        )

    for m in ['acked', 'emitted', 'executed', 'executed_ms_avg', 'process_ms_avg', 'transferred']:
        aggregator.assert_metric(
            'storm.metrics.bolts.last_60.{}'.format(m),
            at_least=1
        )

    for case in metric_cases:
        aggregator.assert_metric(case[0], value=case[1], tags=case[2], count=1)

    # Raises when COVERAGE=true and coverage < 100%
    aggregator.assert_all_metrics_covered()


# @pytest.mark.integration
# def test_integration_with_ci_cluster(dd_environment, aggregator):
#     check = StormCheck(STORM_CHECK_INTEGRATION_CONFIG, {})

#     # run your actual tests...
#     check.check(STORM_CHECK_INTEGRATION_CONFIG['instances'][0])

#     # Service Check
#     aggregator.assert_service_check(
#         'topology_check.topology',
#         count=1,
#         status=AgentCheck.OK,
#         tags=['stormEnvironment:integration', 'stormVersion:1.1.1']
#     )

#     topology_tags = ['topology:topology']
#     env_tags = ['stormEnvironment:integration']
#     storm_version_tags = ['stormVersion:1.1.1']

#     aggregator.assert_metric(
#         'storm.cluster.supervisors', value=1, count=1,
#         tags=storm_version_tags + env_tags
#     )

#     # Cluster Stats
#     test_cases = [
#         'executorsTotal',
#         'slotsTotal',
#         'slotsFree',
#         'topologies',
#         'supervisors',
#         'tasksTotal',
#         'slotsUsed',
#         'availCpu',
#         'totalCpu',
#         'cpuAssignedPercentUtil',
#         'availMem',
#         'totalMem',
#         'memAssignedPercentUtil'
#     ]

#     test_tags = storm_version_tags + env_tags
#     for name in test_cases:
#         aggregator.assert_metric(
#             'storm.cluster.{}'.format(name),
#             count=1,
#             tags=test_tags
#         )

#     # Nimbus Stats
#     test_cases = [
#         'numLeaders',
#         'numFollowers',
#         'numOffline',
#         'numDead'
#     ]
#     test_tags = env_tags + storm_version_tags

#     for name in test_cases:
#         aggregator.assert_metric(
#             'storm.nimbus.{}'.format(name),
#             count=1
#         )

#     # Supervisor Stats
#     test_cases = [
#         'slotsTotal',
#         'slotsUsed',
#         'totalMem',
#         'usedMem',
#         'totalCpu',
#         'usedCpu'
#     ]

#     for name in test_cases:
#         aggregator.assert_metric(
#             'storm.supervisor.{}'.format(name),
#             count=1
#         )

#     # Topology Stats
#     test_cases = [
#         'emitted',
#         'transferred',
#         'acked',
#         'failed',
#         'completeLatency',
#         'uptimeSeconds',
#         'executorsTotal',
#         'numBolts',
#         'replicationCount',
#         'tasksTotal',
#         'numSpouts',
#         'workersTotal',
#         'assignedMemOnHeap',
#         'assignedMemOffHeap',
#         'assignedTotalMem',
#         'requestedMemOnHeap',
#         'requestedMemOffHeap',
#         'requestedCpu',
#         'assignedCpu',
#         'msgTimeout',
#         'debug',
#         'samplingPct'
#     ]

#     test_tags = topology_tags + env_tags + storm_version_tags
#     interval = 'last_60'

#     for name in test_cases:
#         aggregator.assert_metric(
#             'storm.topologyStats.{}.{}'.format(interval, name),
#             at_least=1,
#             tags=test_tags
#         )

#     # Bolt Stats
#     for name, values in [
#         ('split', (8, None, None, None, None, None, None, None, None, 8, None, None, None, None)),
#         ('count', (12, None, None, None, None, None, None, None, None, 12, None, None, None, None))
#     ]:
#         test_tags = env_tags + topology_tags + ['bolt:{}'.format(name)] + storm_version_tags
#         for i, metric_name in enumerate([
#             'tasks', 'executeLatency', 'processLatency', 'capacity', 'failed', 'acked', 'transferred', 'executed',
#             'emitted', 'executors', 'errorLapsedSecs', 'requestedMemOnHeap', 'requestedCpu', 'requestedMemOffHeap'
#         ]):
#             aggregator.assert_metric(
#                 'storm.bolt.last_60.{}'.format(metric_name),
#                 value=values[i],
#                 tags=test_tags,
#                 at_least=1
#             )

#     # Spout Stats
#     for name, values in [
#         ('spout', (5, None, None, None, None, None, 5, None, None, None, None)),
#     ]:
#         test_tags = topology_tags + ['spout:{}'.format(name)] + env_tags + storm_version_tags
#         for i, metric_name in enumerate([
#             'tasks', 'completeLatency', 'failed', 'acked', 'transferred', 'emitted', 'executors', 'errorLapsedSecs',
#             'requestedMemOffHeap', 'requestedCpu', 'requestedMemOnHeap'
#         ]):
#             aggregator.assert_metric(
#                 'storm.spout.last_60.{}'.format(metric_name),
#                 value=values[i],
#                 tags=test_tags,
#                 at_least=1
#             )
