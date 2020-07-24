"""
Client for simulator requests
"""
__copyright__ = "Copyright 2020, Microsoft Corp."

# pyright: strict

from random import uniform
import time
from typing import Union

import jsons
import requests

from .exceptions import RetryTimeoutError, ServiceError
from .logger import Logger
from .simulator_protocol import (
    ServiceConfig,
    SimulatorEvent,
    SimulatorEventRequest,
    SimulatorInterface,
)

log = Logger()

_RETRYABLE_ERROR_CODES = {502, 503, 504}
_MAXIMUM_BACKOFF_SECONDS = 60
_BACKOFF_BASE_MULTIPLIER_MILLISECONDS = 50


class SimulatorClient:
    def __init__(self, config: ServiceConfig):
        self._config = config
        self._retry_attempts = 0
        self._retry_timeout = None
        self._session = requests.session()
        self._session.headers.update(
            {"Authorization": config.access_key, "Content-type": "application/json"}
        )

    def register_simulator(self, interface: SimulatorInterface) -> SimulatorEvent:
        return self._http_request(interface, self._config)

    def get_next_event(self, event_request: SimulatorEventRequest) -> SimulatorEvent:
        return self._http_request(event_request, self._config)

    def unregister_simulator(self, session_id: str):
        url = "{}/v2/workspaces/{}/simulatorSessions/{}".format(
            self._config.server, self._config.workspace, session_id
        )
        log.debug("Sending unregister request to {}".format(url))
        return self._session.delete(url, timeout=self._config.network_timeout_seconds)

    def _http_request(
        self,
        payload: Union[SimulatorInterface, SimulatorEventRequest],
        config: ServiceConfig,
    ) -> SimulatorEvent:
        res = None
        if self._retry_attempts >= 1:
            self._handle_retry()
        try:
            # NOTE: we assert these for the user here to allow the config object to be partially initialized before use.
            assert len(
                config.access_key
            ), "Environment variable SIM_ACCESS_KEY is unset or access_key is empty."
            assert len(
                config.workspace
            ), "Environment variable SIM_WORKSPACE is unset or workspace is empty."
            assert len(
                config.server
            ), "Environment variable SIM_API_HOST is unset or server is empty."

            # Register request
            if isinstance(payload, SimulatorInterface):
                reg_url = "{}/v2/workspaces/{}/simulatorSessions".format(
                    config.server, config.workspace
                )
                log.debug("Sending registration to {}".format(reg_url))
                log.debug("Registration payload: {}".format(jsons.dumps(payload)))
                res = self._session.post(
                    reg_url,
                    json=jsons.loads(payload.json),
                    headers={
                        "Authorization": config.access_key,
                        "Content-type": "application/json",
                    },
                    timeout=self._config.network_timeout_seconds,
                )
                log.debug("Response to registration received.")
            # Get next event request
            if isinstance(payload, SimulatorEventRequest):
                log.network("Sending get next event request.")
                res = self._session.post(
                    "{}/v2/workspaces/{}/simulatorSessions/{}/advance".format(
                        config.server, config.workspace, payload.sessionId
                    ),
                    json=jsons.loads(jsons.dumps(payload)),
                    headers={
                        "Authorization": config.access_key,
                        "Content-type": "application/json",
                    },
                    timeout=self._config.network_timeout_seconds,
                )
                log.network("Response to get next event request received.")
        except requests.exceptions.Timeout as err:
            log.error(err)
            self._retry_attempts += 1
            return self._http_request(payload, config)
        except requests.exceptions.RequestException as err:
            if res is not None:
                log.error(res.text)
            log.error(err)
            raise

        if res is not None:
            if res.status_code in _RETRYABLE_ERROR_CODES:
                log.debug(
                    "Service returned {}, a retryable response error code."
                    " Retrying request.".format(res.status_code)
                )
                self._retry_attempts += 1
                return self._http_request(payload, config)

            # bail on error
            if res.status_code != 200 and res.status_code != 201:
                log.error(
                    "Received response with {} http status code. "
                    "Raising exception.".format(res.status_code)
                )
                if res.text:
                    log.error(res.text)
                raise ServiceError(
                    "Unable to get next event for simulator, "
                    "received {} http status code".format(res.status_code)
                )

            # TODO estee: this needs validation
            # SimulatorEvent
            self._retry_attempts = 0
            self._retry_timeout = None
            return self._event_from_json(res.text)

        raise RuntimeError(
            "Usage error: Somehow http response ended up as none. "
            "Check arguments to _http_request and ensure the payload "
            "is either of type SimulatorInterface or SimulatorEventRequest"
        )

    def _event_from_json(self, json_text: str) -> SimulatorEvent:
        """Converts a json string into a SimulatorEvent."""
        event_dict = jsons.loads(json_text)
        log.debug("Event Response: {}".format(event_dict))
        return SimulatorEvent(event_dict)

    def _handle_retry(self):
        log.network("handling retry.")
        if (
            self._retry_timeout and time.time() > self._retry_timeout
        ) or self._config.retry_timeout_seconds == 0:
            raise RetryTimeoutError("Simulator Retry time exceeded.")

        if self._config.retry_timeout_seconds > 0 and self._retry_timeout is None:
            self._retry_timeout = time.time() + self._config.retry_timeout_seconds
            log.info(
                "Simulator will timeout in {} seconds if it is not able "
                "to connect to the platform.".format(self._retry_timeout - time.time())
            )

        self._backoff()
        log.network("retry handled.")

    def _backoff(self):
        """
        Implements Exponential backoff algorithm with full jitter
        Check the following url for more information
        https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/
        """
        power_of_two = 2 ** self._retry_attempts
        max_sleep = min(
            power_of_two * _BACKOFF_BASE_MULTIPLIER_MILLISECONDS / 1000.0,
            _MAXIMUM_BACKOFF_SECONDS,
        )
        sleep = uniform(0, max_sleep)
        log.debug(
            "Retry attempt: {}, backing off for {} seconds".format(
                self._retry_attempts, sleep
            )
        )
        time.sleep(sleep)
