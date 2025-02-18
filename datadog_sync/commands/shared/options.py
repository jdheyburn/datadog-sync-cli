# Unless explicitly stated otherwise all files in this repository are licensed
# under the 3-clause BSD style license (see LICENSE).
# This product includes software developed at Datadog (https://www.datadoghq.com/).
# Copyright 2019 Datadog, Inc.
import configobj

from click import option, File

from datadog_sync import constants

_source_auth_options = [
    option(
        "--source-api-key",
        envvar=constants.DD_SOURCE_API_KEY,
        required=True,
        help="Datadog source organization API key.",
    ),
    option(
        "--source-app-key",
        envvar=constants.DD_SOURCE_APP_KEY,
        required=True,
        help="Datadog source organization APP key.",
    ),
    option(
        "--source-api-url",
        envvar=constants.DD_SOURCE_API_URL,
        required=False,
        default=constants.DEFAULT_API_URL,
        show_default=True,
        help="Datadog source organization API url.",
    ),
]

_destination_auth_options = [
    option(
        "--destination-api-key",
        envvar=constants.DD_DESTINATION_API_KEY,
        required=True,
        help="Datadog destination organization API key.",
    ),
    option(
        "--destination-app-key",
        envvar=constants.DD_DESTINATION_APP_KEY,
        required=True,
        help="Datadog destination organization APP key.",
    ),
    option(
        "--destination-api-url",
        envvar=constants.DD_DESTINATION_API_URL,
        required=False,
        default=constants.DEFAULT_API_URL,
        show_default=True,
        help="Datadog destination organization API url.",
    ),
]


def click_config_file_provider(ctx, value):
    config = configobj.ConfigObj(value, unrepr=True)
    ctx.default_map = ctx.default_map or {}
    ctx.default_map.update(config)


_common_options = [
    option(
        "--http-client-retry-timeout",
        envvar=constants.DD_HTTP_CLIENT_RETRY_TIMEOUT,
        required=False,
        type=int,
        default=60,
        show_default=True,
        help="The HTTP request retry timeout period. Defaults to 60s",
    ),
    option(
        "--resources",
        envvar=constants.DD_RESOURCES,
        required=False,
        help="Optional comma separated list of resource to import. All supported resources are imported by default.",
    ),
    option(
        "--verbose",
        "-v",
        required=False,
        is_flag=True,
        help="Enable verbose logging.",
    ),
    option(
        "--max-workers",
        envvar=constants.MAX_WORKERS,
        required=False,
        type=int,
        help="Max number of workers when running operations in multi-threads.",
    ),
    option(
        "--filter-operator",
        envvar=constants.DD_FILTER_OPERATOR,
        required=False,
        default="OR",
        help="Filter operator when multiple filters are passed. Supports `AND` or `OR`.",
    ),
    option("--filter", required=False, help="Filter resources.", multiple=True, envvar=constants.DD_FILTER),
    option("--config", help="Read configuration from FILE.", type=File('rb'), callback=click_config_file_provider),
]


_non_import_common_options = [
    option(
        "--skip-failed-resource-connections",
        type=bool,
        default=True,
        show_default=True,
        help="Skip resource if resource connection fails.",
    )
]


def source_auth_options(func):
    return _build_options_helper(func, _source_auth_options)


def destination_auth_options(func):
    return _build_options_helper(func, _destination_auth_options)


def common_options(func):
    return _build_options_helper(func, _common_options)


def non_import_common_options(func):
    return _build_options_helper(func, _non_import_common_options)


def _build_options_helper(func, options):
    for _option in options:
        func = _option(func)
    return func
